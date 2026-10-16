"""Execute the explicitly authorized, exact-input exception once; no PDF rerun."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'pilot/subset15';SCRIPTS=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
def main():
    approval=read(RUN/'context_limit_exception.json');assert approval['approved'] is True
    manifest=read(RUN/'manifest.json');row=next(x for x in manifest['papers'] if x['id']==approval['paper']);assert row['id']=='1912.08777.pdf' and not row['reused']
    blocked=Path(approval['blocked_extraction_dir']);assert not list(blocked.glob('api_calls/*/attempt.json'))
    assert hashlib.sha256((blocked/'request_plan.json').read_bytes()).hexdigest()==approval['blocked_plan_sha256']
    out=blocked.parent/'extraction-approved-context';out.mkdir(exist_ok=True)
    row.update(blocked_extraction_dir=str(blocked),extraction_dir=str(out),normalization_dir=str(out/'normalization'),context_limit_exception=str(RUN/'context_limit_exception.json'))
    save(RUN/'manifest.json',manifest)
    progress=read(RUN/'execution_progress.json');progress.setdefault('initial_batch_finished_epoch',progress['finished_epoch'])
    env=dict(os.environ,SCILEAD_RUN_ROOT=str(RUN),PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
    for stage,script,folder in [('extract','subset15_large_input_api.py',out),('normalize','subset5_api.py',out/'normalization')]:
        folder.mkdir(exist_ok=True)
        if (folder/'summary.json').exists() and read(folder/'summary.json')['status']=='COMPLETE':continue
        print('START_AUTHORIZED_EXCEPTION',stage,row['id'],flush=True);started=time.monotonic()
        progress['active']={'paper':row['id'],'stage':stage,'context_exception':True};save(RUN/'execution_progress.json',progress)
        with (folder/'run.log').open('a',encoding='utf-8') as log:
            result=subprocess.run([sys.executable,'-X','utf8',str(SCRIPTS/script),'--paper',row['id'],'--stage',stage],env=env,stdout=log,stderr=subprocess.STDOUT)
        summary=read(folder/'summary.json') if (folder/'summary.json').exists() else {'status':'FAILED'}
        state={'status':summary['status'],'exit_code':result.returncode,'wall_seconds':round(time.monotonic()-started,3),'authorized_context_exception':True}
        progress['papers'][row['id']][stage+'_authorized_exception']=state;save(RUN/'execution_progress.json',progress)
        manifest=read(RUN/'manifest.json');next(x for x in manifest['papers'] if x['id']==row['id'])['status']=stage.upper()+'_'+state['status'];save(RUN/'manifest.json',manifest)
        print('END_AUTHORIZED_EXCEPTION',stage,state,flush=True)
        if result.returncode or state['status']!='COMPLETE':break
    progress['active']=None;progress['finished_epoch']=time.time();save(RUN/'execution_progress.json',progress)
if __name__=='__main__':main()
