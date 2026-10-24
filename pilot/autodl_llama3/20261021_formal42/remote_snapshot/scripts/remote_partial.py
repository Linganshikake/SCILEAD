"""CS then both author Partially stages; stage checkpoints prevent regeneration."""
from pathlib import Path
import json,subprocess,time,os,fcntl
R=Path(__file__).resolve().parents[1];PY='/root/autodl-tmp/scilead/envs/llama/bin/python'
def save(d):
    p=R/'partial_status.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2));t.replace(p)
def main():
    lock=(R/'.partial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert (R/'normalization/fully_llm/stage_complete.json').exists()
    start=time.monotonic();s={'status':'RUNNING','stages':{}}
    for name,argv,out in [('cs',[PY,str(R/'scripts/run_cs.py')],R/'normalization/fully_cs'),('partial',[PY,str(R/'scripts/run_stage.py'),'partial'],R/'normalization/partially/stage1'),('leaderboard',[PY,str(R/'scripts/run_stage.py'),'leaderboard'],R/'normalization/partially/stage2')]:
        out.mkdir(parents=True,exist_ok=True);s['current_stage']=name;save(s);t=time.monotonic()
        with (out/'process.log').open('ab') as log:p=subprocess.run(argv,stdout=log,stderr=log)
        s['stages'][name]={'exit_code':p.returncode,'seconds':time.monotonic()-t};save(s)
        if p.returncode:s.update(status='FAILED',failed_stage=name);save(s);return
    s.update(status='COMPLETE',seconds=time.monotonic()-start);save(s)
if __name__=='__main__':main()
