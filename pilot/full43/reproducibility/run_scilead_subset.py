"""Run unchanged per-paper adapters in sequence, with durable stage checkpoints."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);a=ap.parse_args()
    run=a.run_root.resolve();assert run.is_relative_to((ROOT/'pilot').resolve())
    m=read(run/'manifest.json');assert len(m['papers'])==m['target_count']
    for filename,digest in read(run/'preserved_existing_sha256.json').items():
        assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==digest,filename
    env=dict(os.environ,SCILEAD_RUN_ROOT=str(run),PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
    status_path=run/'execution_progress.json'
    progress=read(status_path) if status_path.exists() else {'started_epoch':time.time(),'papers':{}}
    for row in m['papers']:
        if row['reused']:
            print('REUSE',row['id'],flush=True);continue
        stages=[('preprocess','preprocess_dir','subset5_preprocess.py',[]),('extract','extraction_dir','scilead_api.py',['--stage','extract']),('normalize','normalization_dir','scilead_api.py',['--stage','normalize'])]
        for stage,key,script,extra in stages:
            folder=Path(row[key]);folder.mkdir(parents=True,exist_ok=True)
            if (folder/'summary.json').exists() and read(folder/'summary.json').get('status')=='COMPLETE':
                print('SKIP_COMPLETE',stage,row['id'],flush=True);continue
            # Original adapter refuses unresolved attempted requests. Never erase checkpoints.
            print('START',stage,row['id'],flush=True)
            progress['active']={'paper':row['id'],'stage':stage};save(status_path,progress)
            started=time.monotonic()
            with (folder/'run.log').open('a',encoding='utf-8') as log:
                result=subprocess.run([sys.executable,'-X','utf8',str(SCRIPTS/script),'--paper',row['id'],*extra],env=env,stdout=log,stderr=subprocess.STDOUT)
            summary=read(folder/'summary.json') if (folder/'summary.json').exists() else {'status':'FAILED'}
            entry={'status':summary.get('status'),'exit_code':result.returncode,'wall_seconds':round(time.monotonic()-started,3)}
            progress['papers'].setdefault(row['id'],{})[stage]=entry;save(status_path,progress)
            current=read(run/'manifest.json');next(p for p in current['papers'] if p['id']==row['id'])['status']=stage.upper()+'_'+entry['status'];save(run/'manifest.json',current)
            print('END',stage,row['id'],entry,flush=True)
            if result.returncode or entry['status']!='COMPLETE':break
    progress['active']=None;progress['finished_epoch']=time.time();save(status_path,progress)
    print('BATCH_FINISHED; consult progress and manifest for coverage',flush=True)
if __name__=='__main__':main()
