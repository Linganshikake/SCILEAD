"""Bounded stage dependency watcher. No repeated model requests or inference retries."""
from pathlib import Path
import time,json,subprocess,fcntl
R=Path(__file__).resolve().parents[1];PY='/root/autodl-tmp/scilead/envs/llama/bin/python'
def main():
    lock=(R/'.followup.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    start=time.monotonic()
    while time.monotonic()-start<21600:
        p=R/'batch_status.json';s=json.loads(p.read_text()) if p.exists() else {}
        if s.get('status')=='READY_FOR_CS':break
        if s.get('status')=='FULLY_LLM_FAILED':raise RuntimeError('FULLY_FAILED_NO_AUTOMATIC_RETRY')
        time.sleep(20)
    else:raise RuntimeError('WAIT_TIMEOUT_NO_INFERENCE_RETRY')
    for name in ['remote_partial.py','replay_stages.py']:
        with (R/(name+'.log')).open('ab') as log:p=subprocess.run([PY,str(R/'scripts'/name)],stdout=log,stderr=log)
        if p.returncode:raise RuntimeError(name+'_FAILED')
        if name=='remote_partial.py':assert json.loads((R/'partial_status.json').read_text())['status']=='COMPLETE'
    (R/'formal_remote_complete.json').write_text(json.dumps({'status':'COMPLETE','followup_wall_seconds':time.monotonic()-start}))
if __name__=='__main__':main()
