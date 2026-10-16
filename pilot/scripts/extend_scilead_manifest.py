"""Prepare an independent larger run. This helper never calls an LLM.

Default only prepares metadata. --download fetches the newly selected PDFs;
candidate order is fixed before any fetch and downloads are checkpointed.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import random
import ssl
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--destination',type=Path,required=True);parser.add_argument('--target',type=int,required=True);parser.add_argument('--seed',type=int,default=20261013);parser.add_argument('--download',action='store_true');a=parser.parse_args()
    src=a.source.resolve();dest=a.destination.resolve();assert dest.is_relative_to((ROOT/'pilot').resolve()) and dest!=src
    prior=read(src/'manifest.json');gold=read(Path(prior['gold_path']));assert len(prior['papers'])<a.target<=len(gold)
    assert all(p['status'] in ('COMPLETE','COMPLETE_REUSED') for p in prior['papers']),'Source run must be complete'
    if not (dest/'manifest.json').exists():
        dest.mkdir(parents=True,exist_ok=False)
        taken={p['id'] for p in prior['papers']};rng=random.Random(a.seed);buckets=[]
        for lo,hi in [(1,3),(4,6),(7,11),(12,1000)]:
            ids=sorted(k for k,v in gold.items() if k not in taken and lo<=len(v['TDMs'])<=hi);rng.shuffle(ids);buckets.append(ids)
        order=[]
        while any(buckets):
            for bucket in buckets:
                if bucket:order.append(bucket.pop(0))
        m=copy.deepcopy(prior);m.update(scope=f'{a.target} papers, immutable completed source reused',seed=a.seed,source_run=str(src),download_failures=[],extension_candidate_order=order,extension_cursor=0,target_count=a.target)
        for p in m['papers']:p['reused']=True;p['status']='COMPLETE_REUSED'
        save(dest/'manifest.json',m);save(dest/'selection_plan.json',{'seed':a.seed,'method':'Deterministic shuffled Gold-count strata, round-robin; no score-based selection. New run only; previous completed outputs referenced unchanged.','candidate_order':order})
        preserved=read(src/'preserved_existing_sha256.json')
        preserved.update({str(p):sha(p) for p in src.rglob('*') if p.is_file()});save(dest/'preserved_existing_sha256.json',preserved)
        import importlib.metadata,sys
        env=read(src/'environment.json');env['started_epoch']=time.time();env['source_run']=str(src);env['python']=sys.version;env['interpreter']=sys.executable;env['dependencies']={d.metadata['Name']:d.version for d in importlib.metadata.distributions()};save(dest/'environment.json',env)
    m=read(dest/'manifest.json');assert m['target_count']==a.target
    if not a.download:print('Manifest prepared; no new PDF download or API call. Rerun with --download when authorized.');return
    import certifi
    from pypdf import PdfReader
    ctx=ssl.create_default_context(cafile=certifi.where())
    while len(m['papers'])<a.target and m['extension_cursor']<len(m['extension_candidate_order']):
        ident=m['extension_candidate_order'][m['extension_cursor']];m['extension_cursor']+=1;save(dest/'manifest.json',m)
        try:
            b=urllib.request.urlopen(gold[ident]['PaperURL'],context=ctx,timeout=60).read(100_000_001);assert len(b)<=100_000_000 and b.startswith(b'%PDF')
            pages=len(PdfReader(io.BytesIO(b)).pages);folder=dest/'papers'/ident.removesuffix('.pdf');(folder/'input').mkdir(parents=True,exist_ok=True);pdf=folder/'input'/ident;pdf.write_bytes(b)
            m['papers'].append({'id':ident,'gold_count':len(gold[ident]['TDMs']),'reused':False,'source_url':gold[ident]['PaperURL'],'pdf_path':str(pdf),'pdf_pages':pages,'pdf_sha256':sha(pdf),'preprocess_dir':str(folder/'preprocess'),'extraction_dir':str(folder/'extraction'),'normalization_dir':str(folder/'extraction/normalization'),'status':'PDF_READY'})
        except Exception as exc:m['download_failures'].append({'id':ident,'error_type':type(exc).__name__,'error':str(exc)})
        save(dest/'manifest.json',m)
    print('Selected',len(m['papers']),'requested',a.target,'download failures',len(m['download_failures']))
if __name__=='__main__':main()
