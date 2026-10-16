"""Prepare all remaining papers, preserving failures and prior artifacts."""
import copy, hashlib, importlib.metadata, io, json, ssl, sys, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'pilot/subset15_uncapped_retry'; DEST=ROOT/'pilot/full43'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
def main():
    prior=read(SRC/'manifest.json');gold=read(Path(prior['gold_path']))
    assert sha(Path(prior['gold_path']))==prior['gold_sha256']
    assert len(gold)==43 and sum(len(v['TDMs']) for v in gold.values())==295
    assert len(prior['papers'])==15 and all(p['status'] in ('COMPLETE','COMPLETE_REUSED') for p in prior['papers'])
    taken={p['id'] for p in prior['papers']};remaining=sorted(set(gold)-taken)
    assert len(remaining)==28 and sum(len(gold[k]['TDMs']) for k in taken)==153
    if not (DEST/'manifest.json').exists():
        DEST.mkdir(exist_ok=False)
        preserved=read(SRC/'preserved_existing_sha256.json')
        for p,h in preserved.items(): assert sha(Path(p))==h,p
        preserved.update({str(p):sha(p) for p in SRC.rglob('*') if p.is_file()})
        save(DEST/'preserved_existing_sha256.json',preserved)
        env=read(SRC/'environment.json')
        for p,h in env['source_sha256'].items(): assert sha(Path(p))==h,p
        deps={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
        assert deps==env['dependencies'],'Dependency drift'
        env.update(started_epoch=time.time(),source_run=str(SRC),interpreter=sys.executable,dependencies=deps,api_parameters={'temperature':0,'seed':0,'output_limit_parameters':'omitted','context_input_cap':None,'max_retries':0})
        save(DEST/'environment.json',env)
        settings=read(ROOT/'pilot/experiment_settings.json')
        assert settings['extraction_max_tokens'] is None and settings['normalization_max_tokens'] is None and settings['input_token_limit'] is None
        save(DEST/'experiment_settings_snapshot.json',settings)
        save(DEST/'prior_accounting.json',read(SRC/'api_usage_summary.json'))
        m={k:copy.deepcopy(prior[k]) for k in ('gold_path','gold_sha256','gold_papers','gold_tdmrs')}
        m.update(scope='All 43 Gold papers; 15 reused and all remaining 28 queued without sampling',source_run=str(SRC),target_count=43,papers=copy.deepcopy(prior['papers']),download_failures=[],settings_path=str(DEST/'experiment_settings_snapshot.json'))
        for p in m['papers']:p.update(reused=True,status='COMPLETE_REUSED')
        for ident in remaining:
            folder=DEST/'papers'/ident.removesuffix('.pdf')
            m['papers'].append(dict(id=ident,gold_count=len(gold[ident]['TDMs']),reused=False,source_url=gold[ident]['PaperURL'],pdf_path=str(folder/'input'/ident),preprocess_dir=str(folder/'preprocess'),extraction_dir=str(folder/'extraction'),normalization_dir=str(folder/'extraction/normalization'),status='PDF_PENDING'))
        save(DEST/'manifest.json',m)
        save(DEST/'selection_plan.json',{'method':'Complete sorted set difference; no sampling or replacements','new_papers':remaining,'reused_papers':sorted(taken),'fixed_before_download_and_model_requests':True})
    m=read(DEST/'manifest.json')
    import certifi
    from pypdf import PdfReader
    ctx=ssl.create_default_context(cafile=certifi.where())
    local={}
    for folder in [Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_DATA'),Path(r'C:\Users\Administrator\Desktop\KG\SCILEAD_CODE')]:
        if folder.exists():
            for p in folder.rglob('*.pdf'):local.setdefault(p.name,p)
    for row in m['papers']:
        if row['reused'] or row['status']!='PDF_PENDING':continue
        start=time.time();dest=Path(row['pdf_path'])
        try:
            if row['id'] in local:
                data=local[row['id']].read_bytes();row['local_source']=str(local[row['id']])
            else:
                req=urllib.request.Request(row['source_url'],headers={'User-Agent':'SCILEAD-reproduction/1.0'})
                with urllib.request.urlopen(req,context=ctx,timeout=60) as response:
                    data=response.read(100_000_001);row['resolved_pdf_url']=response.url
            assert len(data)<=100_000_000 and data.startswith(b'%PDF'),'Not a supported PDF download'
            pages=len(PdfReader(io.BytesIO(data)).pages)
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            row.update(pdf_pages=pages,pdf_sha256=sha(dest),status='PDF_READY',download_seconds=round(time.time()-start,3))
        except Exception as exc:
            error={'id':row['id'],'error_type':type(exc).__name__,'error':str(exc),'url':row['source_url']}
            row.update(status='PDF_DOWNLOAD_FAILED',download_error=error);m['download_failures'].append(error)
        save(DEST/'manifest.json',m);print(row['id'],row['status'],row.get('pdf_pages'),flush=True)
    print('Queue',len(m['papers']),'new ready',sum(not p['reused'] and p['status']=='PDF_READY' for p in m['papers']),flush=True)
if __name__=='__main__': main()
