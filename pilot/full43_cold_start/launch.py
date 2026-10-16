"""Sequential independent runs; resume only confirmed saved responses."""
import subprocess
from common import *

def main():
    assert not RUN_ID;assert read(TOP/'preflight_audit.json')['status']=='PASS'
    assert read(TOP/'reproducibility/offline_tests.json')['status']=='PASS'
    assert read(TOP/'reproducibility/failure_control_tests.json')['status']=='PASS'
    manifest=read(TOP/'experiment_manifest.json');verify()
    for name,info in manifest['orders'].items():assert sha(TOP/name/'paper_order.json')==info['paper_order_sha256']
    for run_id in manifest['orders']:
        env=dict(os.environ,PYTHONHASHSEED='0',SCILEAD_COLD_RUN_ID=run_id)
        for script in ('run_cold.py','evaluate.py','verify_run.py'):
            log=TOP/run_id/(script+'.log')
            print('START',run_id,script,flush=True)
            with log.open('a',encoding='utf-8') as f:r=subprocess.run([sys.executable,'-B','-X','utf8',str(TOP/script)],env=env,stdout=f,stderr=subprocess.STDOUT)
            if r.returncode:
                save(TOP/'execution_status.json',{'status':'PAUSED','run_id':run_id,'script':script,'exit_code':r.returncode,'time':time.time()});print('PAUSED',run_id,script,r.returncode,flush=True);return r.returncode
            print('DONE',run_id,script,flush=True)
        save(TOP/'execution_status.json',{'status':'RUN_COMPLETE','run_id':run_id,'time':time.time()})
    save(TOP/'execution_status.json',{'status':'ALL_RUNS_COMPLETE','time':time.time()});return 0
if __name__=='__main__':sys.exit(main())
