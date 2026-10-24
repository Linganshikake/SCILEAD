"""Read-only verification against the existing local AxCell manifests."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent
ROOT=Path(r'E:\SCILEAD\axcell')

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()

source=json.loads((ROOT/'manifests/axcell_source_manifest.json').read_text(encoding='utf-8'))
models=json.loads((ROOT/'runs/20261021_235603/model_manifest.json').read_text(encoding='utf-8'))
transfer=json.loads((OUT/'transfer_manifest.json').read_text(encoding='utf-8'))
entries=[(ROOT/'source/axcell'/e['path'],e['sha256']) for e in source['files']]
entries += [(Path(e['path']),e['sha256']) for e in models['files']]
entries += [(Path(models['path']),models['sha256'])]
entries += [(Path(transfer['selected_paper']['tex_path']),transfer['selected_paper']['tex_sha256'])]
checks=[{'path':str(p),'sha256_match':p.is_file() and sha(p)==expected} for p,expected in entries]
result={'all_match':all(x['sha256_match'] for x in checks),'files':checks,'verification_scope':'Existing frozen AxCell source, seven model files, model archive and selected TeX; does not assert a new hash audit of all historical SCILEAD experiments'}
(OUT/'local_asset_integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checked':len(checks),'all_match':result['all_match']}))
assert result['all_match']
