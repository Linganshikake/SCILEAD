"""Sequential subprocesses release the embedding model before evaluation."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import time

RUN=Path(__file__).resolve().parent
PYTHON=Path(r'D:\miniconda3\envs\scilead\python.exe')
STAGES=[('normalization','run_cs.py'),('tuple_evaluation','evaluate_cs.py'),('official_leaderboard','leaderboard_evaluation/run_official_leaderboard_eval.py'),('supplementary_leaderboard','leaderboard_evaluation/evaluate_paper_metrics.py')]

def main():
    previous=list(RUN.glob('*.log'))+[RUN/'execution_status.json',RUN/'blocked_resources.json']
    if any(p.exists() for p in previous):
        archive=RUN/'reproducibility/attempts'/str(time.time_ns());archive.mkdir(parents=True)
        for p in previous:
            if p.exists():shutil.copy2(p,archive/p.name)
    env=os.environ.copy()
    env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',HF_HUB_DISABLE_TELEMETRY='1',TMP=str(RUN/'runtime/tmp'),TEMP=str(RUN/'runtime/tmp'))
    status={'started_epoch':time.time(),'scope':'ONLY offline Fully+CS','stages':[]}
    for name,script in STAGES:
        start=time.monotonic();print('START',name,flush=True)
        with (RUN/(name+'.log')).open('wb') as log:
            result=subprocess.run([str(PYTHON),'-u','-B','-X','utf8',str(RUN/script)],cwd=RUN,env=env,stdout=log,stderr=subprocess.STDOUT)
        status['stages'].append({'name':name,'script':script,'returncode':result.returncode,'seconds':time.monotonic()-start})
        status['status']='RUNNING' if result.returncode==0 else 'FAILED'
        (RUN/'execution_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
        print('DONE',name,result.returncode,flush=True)
        if result.returncode:
            print((RUN/(name+'.log')).read_text(encoding='utf-8')[-14000:],flush=True)
            return result.returncode
    status['status']='EXECUTION_COMPLETE';status['ended_epoch']=time.time()
    (RUN/'execution_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    with (RUN/'finish.log').open('wb') as log:
        result=subprocess.run([str(PYTHON),'-u','-B','-X','utf8',str(RUN/'finish.py')],cwd=RUN,env=env,stdout=log,stderr=subprocess.STDOUT)
    print((RUN/'finish.log').read_text(encoding='utf-8'),flush=True)
    return result.returncode

if __name__=='__main__':sys.exit(main())
