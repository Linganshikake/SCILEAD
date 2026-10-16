"""Reproducible count-stratified selection; no model quality based selection."""
import hashlib
import json
from pathlib import Path
import random
import re
import ssl
import time
import urllib.request
import certifi
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'pilot/subset5'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261013
EXISTING = '2020.findings-emnlp.378.pdf'

def save(name, obj):
    target = OUT / name
    temporary = target.with_suffix(target.suffix + '.tmp')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(target)

def year(name):
    if re.match(r'^20\d\d[.]', name): return int(name[:4])
    if re.match(r'^\d{4}[.]', name): return 2000 + int(name[:2])
    m = re.search(r'[A-Za-z](\d\d)', name)
    return 2000 + int(m[1]) if m else None

def main():
    if (OUT / 'manifest.json').exists():
        old = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
        if len(old['papers']) == 5:
            print('Existing selection retained; no downloads repeated.'); return
        raise RuntimeError('Incomplete selection exists; inspect recorded download state before resuming selection')
    candidates = []
    for p in Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA').rglob('*.json'):
        data = json.loads(p.read_text(encoding='utf-8'))
        if isinstance(data, dict) and len(data) == 43 and all(isinstance(v, dict) and 'TDMs' in v and 'PaperURL' in v for v in data.values()):
            candidates.append((p, data))
    assert len(candidates) == 1
    gold_path, gold = candidates[0]
    rng = random.Random(SEED)
    rules = [('low_1_to_3', 1, 3, {2015,2016,2017}), ('medium_4_to_6', 4, 6, {2018}), ('high_7_to_11', 7, 11, {2020,2021,2022}), ('very_high_12_plus', 12, 1000, {2019})]
    strata = []
    for label, lo, hi, years in rules:
        ids = sorted(k for k, v in gold.items() if k != EXISTING and lo <= len(v['TDMs']) <= hi)
        rng.shuffle(ids)
        # Fixed publication-era preference, then ACL host preference for availability.
        ids.sort(key=lambda k: (year(k) not in years, 'aclanthology.org' not in gold[k]['PaperURL']))
        strata.append({'stratum': label, 'count_interval': [lo,hi], 'preferred_id_years': sorted(years), 'candidate_order': ids})
    save('selection_plan.json', {'seed':SEED, 'method':'One paper per disjoint Gold-count stratum. Seeded shuffle from sorted IDs; stable priority for preset ID-year eras, then ACL availability. No use of Gold answer content or model performance. Years inferred from IDs, not verified publication dates. Replace only PDF acquisition failures in recorded order.', 'strata':strata})
    old = ROOT / 'pilot/outputs/gpt41_single_paper'
    preserved = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in old.rglob('*') if p.is_file()}
    old_pre = ROOT / 'pilot/outputs/scilead-pilot-13.10.2026-16-58-13'
    for p in old_pre.rglob('*'):
        if p.is_file(): preserved[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    save('preserved_existing_sha256.json',preserved)
    manifest = {'scope':'5 papers total, only four new; original completed baseline reused unchanged', 'seed':SEED, 'gold_path':str(gold_path), 'gold_sha256':hashlib.sha256(gold_path.read_bytes()).hexdigest(), 'gold_papers':43, 'gold_tdmrs':sum(len(v['TDMs']) for v in gold.values()), 'selection_plan':'selection_plan.json', 'download_failures':[], 'papers':[{'id':EXISTING,'gold_count':len(gold[EXISTING]['TDMs']), 'id_year':2020,'reused':True,'pdf_path':str(ROOT/'pilot/papers'/EXISTING),'preprocess_dir':str(old_pre),'extraction_dir':str(old),'normalization_dir':str(old/'normalization'),'status':'COMPLETE_REUSED'}]}
    save('manifest.json',manifest)
    ctx = ssl.create_default_context(cafile=certifi.where())
    for stratum in strata:
        for paper in stratum['candidate_order']:
            entry = gold[paper]; start=time.monotonic()
            try:
                response=urllib.request.urlopen(entry['PaperURL'],context=ctx,timeout=60)
                content=response.read(100_000_001)
                assert len(content) <= 100_000_000 and content.startswith(b'%PDF'), 'Not a valid PDF or exceeds 100 MB safety limit'
                import io
                pages=len(PdfReader(io.BytesIO(content)).pages)
                folder=OUT/'papers'/paper.removesuffix('.pdf');(folder/'input').mkdir(parents=True,exist_ok=True)
                path=folder/'input'/paper;path.write_bytes(content)
                row={'id':paper,'gold_count':len(entry['TDMs']),'id_year':year(paper),'reused':False,'stratum':stratum['stratum'],'source_url':entry['PaperURL'],'pdf_path':str(path),'pdf_pages':pages,'pdf_sha256':hashlib.sha256(content).hexdigest(),'download_seconds':round(time.monotonic()-start,2),'preprocess_dir':str(folder/'preprocess'),'extraction_dir':str(folder/'extraction'),'normalization_dir':str(folder/'extraction/normalization'),'status':'PDF_READY'}
                manifest['papers'].append(row);save('manifest.json',manifest)
                print(json.dumps(row),flush=True);break
            except Exception as exc:
                failure={'id':paper,'url':entry['PaperURL'],'error_type':type(exc).__name__,'error':str(exc),'seconds':round(time.monotonic()-start,2)}
                manifest['download_failures'].append(failure);save('manifest.json',manifest);print(json.dumps(failure),flush=True)
        else:
            raise RuntimeError('No available PDF in stratum '+stratum['stratum'])
    print('SELECTED',len(manifest['papers']),flush=True)

if __name__=='__main__': main()
