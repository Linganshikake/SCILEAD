"""Phase 9 API-only orchestration. Never parses PDFs or builds a vector store."""
import argparse, hashlib, importlib.metadata, json, os, pickle, shutil, subprocess, sys, time
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; PILOT=ROOT/'pilot'; OLD=PILOT/'full43'; RUN=PILOT/'full43_uncapped'; REPO=ROOT/'emnlp2024-leaderboard-generation'
LONG='1912.08777.pdf'; SCRIPTS=Path(__file__).parent
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def requests(d,stage):
    fs=sorted(d.glob('api_calls/*/request.json'))
    if not fs: fs=[d/'request_payload.json'] if stage=='extract' else sorted(d.glob('call-*-request.json'))
    assert fs and all(f.exists() for f in fs)
    return fs
def check_preserved():
    for p,h in read(RUN/'preserved_existing_sha256.json').items(): assert sha(Path(p))==h,p
    for p,h in read(RUN/'environment.json')['source_sha256'].items(): assert sha(Path(p))==h,p
def prepare():
    assert not RUN.exists(),'Existing run: use --run, never prepare again'
    old=read(OLD/'manifest.json');assert len(old['papers'])==43 and sum(r['gold_count'] for r in old['papers'])==295
    assert read(OLD/'verification.json')['coverage']['completed_papers']==43
    assert abs(read(OLD/'evaluation/metrics_with_f1.json')['aggregate']['TDMR Exact Match']['F1']-.38903933439480964)<1e-12
    for p,h in read(OLD/'file_integrity_sha256.json').items(): assert sha(OLD/p)==h,p
    preserved=read(OLD/'preserved_existing_sha256.json')
    for f in OLD.rglob('*'):
        if f.is_file():preserved[str(f)]=sha(f)
    preserved[str(PILOT/'experiment_settings.json')]=sha(PILOT/'experiment_settings.json')
    preserved[str(SCRIPTS/'scilead_api.py')]=sha(SCRIPTS/'scilead_api.py')
    audit=[]
    for i,r in enumerate(old['papers']):
        for stage,key in [('extract','extraction_dir'),('normalize','normalization_dir')]:
            fs=requests(Path(r[key]),stage);expected=1024 if i<15 and stage=='extract' and r['id']!=LONG else 15 if i<15 and stage=='normalize' else None
            for f in fs:
                q=read(f);caps={k:v for k,v in q.items() if k in ('max_tokens','max_completion_tokens','max_output_tokens')}
                assert caps==({'max_tokens':expected} if expected else {}),(r['id'],stage,caps)
                assert q['model']=='gpt-4.1-2025-04-14' and q['temperature']==0 and q['seed']==0
            audit.append({'paper':r['id'],'stage':stage,'requests':len(fs),'output_cap':expected,'request_paths':[str(f) for f in fs]})
    RUN.mkdir();(RUN/'work').mkdir()
    save(RUN/'historical_request_audit.json',audit);save(RUN/'preserved_existing_sha256.json',preserved)
    env=read(OLD/'environment.json');env.update(started_epoch=time.time(),source_run=str(OLD))
    assert env['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    save(RUN/'environment.json',env);save(RUN/'prior_accounting.json',read(OLD/'api_usage_summary.json'));save(RUN/'experiment_settings_snapshot.json',read(PILOT/'experiment_settings.json'))
    manifest={**old,'source_run':str(OLD),'scope':'43 papers, uniform omitted client output limits; no PDF/retrieval reruns','papers':[]}
    for i,source in enumerate(old['papers']):
        r=dict(source);r['pdf_pages']=source.get('pdf_pages') or source.get('stage_summary',{}).get('pdf_pages');r.pop('stage_summary',None)
        r.update(source_preprocess_dir=source['preprocess_dir'],source_extraction_dir=source['extraction_dir'],source_normalization_dir=source['normalization_dir'],preprocess_reused=True,extraction_reused=(i>=15 or r['id']==LONG),normalization_reused=i>=15,reused=i>=15,status='REUSED' if i>=15 else 'PENDING')
        if i<15:
            ex=RUN/'papers'/Path(r['id']).stem/'extraction';r.update(extraction_dir=str(ex),normalization_dir=str(ex/'normalization'))
            if r['id']==LONG:
                ex.mkdir(parents=True)
                for f in Path(source['extraction_dir']).iterdir():
                    if f.name=='normalization':continue
                    if f.is_dir():shutil.copytree(f,ex/f.name)
                    else:shutil.copy2(f,ex/f.name)
                assert sha(ex/'output.json')==sha(Path(source['extraction_dir'])/'output.json')
            pre=Path(source['preprocess_dir'])
            if not (pre/'summary.json').exists():
                proxy=RUN/'reused_cache'/Path(r['id']).stem;proxy.mkdir(parents=True)
                shutil.copy2(pre/'processed_docs.pkl',proxy/'processed_docs.pkl')
                summary=read(pre/'pilot-summary.json');assert summary['status']=='PASS';summary.update(status='COMPLETE',source_summary=str(pre/'pilot-summary.json'),cache_copy_only=True)
                save(proxy/'summary.json',summary);r['preprocess_dir']=str(proxy)
        r['evidence_sha256']=sha(Path(r['preprocess_dir'])/'processed_docs.pkl')
        assert r['evidence_sha256']==sha(Path(r['source_preprocess_dir'])/'processed_docs.pkl')
        manifest['papers'].append(r)
    save(RUN/'manifest.json',manifest)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HOME=str(ROOT/'assets/huggingface'),PYTHONDONTWRITEBYTECODE='1')
    sys.path.insert(0,str(REPO));from prompting import TDMPrompt
    prompts=read(REPO/'prompts.json');template=TDMPrompt(prompts['tdm-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    checks=[]
    for r in manifest['papers']:
        with (Path(r['preprocess_dir'])/'processed_docs.pkl').open('rb') as f:papers=pickle.load(f)
        assert list(papers)==[r['id']];docs=papers[r['id']]
        messages=[{'role':{'system':'system','human':'user'}[m.type],'content':m.content} for m in template.format_messages(question=prompts['query'],context='\n\n'.join(d.page_content for d in docs))]
        historical=read(requests(Path(r['source_extraction_dir']),'extract')[0]);assert messages==historical['messages'],r['id']
        checks.append({'paper':r['id'],'evidence_count':len(docs),'cache_sha256':r['evidence_sha256'],'messages_identical_to_historical_request':True})
    save(RUN/'input_preflight.json',checks);check_preserved()
    print(json.dumps({'historical_request_audit':'PASS','input_messages_identical':43,'new_extractions':14,'new_normalizations':15,'entirely_reused':28,'preserved_files':len(preserved)}))
def run():
    check_preserved();start=time.time();save(RUN/'execution_started.json',{'epoch':start}) if not (RUN/'execution_started.json').exists() else None
    env=dict(os.environ,SCILEAD_RUN_ROOT=str(RUN),PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
    for row in read(RUN/'manifest.json')['papers']:
        if row['normalization_reused']:continue
        assert sha(Path(row['preprocess_dir'])/'processed_docs.pkl')==row['evidence_sha256']
        for stage,key,reuse_key in [('extract','extraction_dir','extraction_reused'),('normalize','normalization_dir','normalization_reused')]:
            if row[reuse_key]:continue
            folder=Path(row[key]);folder.mkdir(parents=True,exist_ok=True)
            if (folder/'summary.json').exists():
                status=read(folder/'summary.json')['status']
                if status=='COMPLETE':continue
                if status in ('INVALID_OUTPUT','TRUNCATED_OUTPUT'):break
            if stage=='normalize' and (not (Path(row['extraction_dir'])/'summary.json').exists() or read(Path(row['extraction_dir'])/'summary.json')['status']!='COMPLETE'):break
            print('START',row['id'],stage,flush=True)
            with (folder/'run.log').open('a',encoding='utf-8') as log:
                p=subprocess.run([sys.executable,'-X','utf8',str(SCRIPTS/'scilead_api.py'),'--paper',row['id'],'--stage',stage],env=env,stdout=log,stderr=subprocess.STDOUT)
            status=read(folder/'summary.json')['status'] if (folder/'summary.json').exists() else 'FAILED'
            m=read(RUN/'manifest.json');r=next(r for r in m['papers'] if r['id']==row['id']);r['status']=stage.upper()+'_'+status;save(RUN/'manifest.json',m)
            print('END',row['id'],stage,status,'exit',p.returncode,flush=True)
            if p.returncode or status!='COMPLETE':break
    check_preserved();save(RUN/'execution_finished.json',{'epoch':time.time(),'this_invocation_seconds':time.time()-start});print('PIPELINE_FINISHED',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true');a=p.parse_args()
    if a.prepare:prepare()
    elif a.run:run()
