import subprocess
from variant_runtime import *

def main():
    setup();results=[]
    for kind in ('partially','cold_start'):
        text=(PILOT/('full43_'+kind)/'test_offline.py').read_text('utf-8')
        prefix="import variant_runtime as v\nfrom variant_runtime import *\nRUN=TOP=Path(__file__).resolve().parent/'reproducibility'/'"+kind+"'\n(RUN/'reproducibility').mkdir(parents=True,exist_ok=True)\nv.RUN_ID='"+('cold_test' if kind=='cold_start' else 'partially_test')+"'"
        text=text.replace('from common import *',prefix).replace('from engine import run_original,SimulatedInterruption','from variant_runtime import run_original,SimulatedInterruption')
        target=TOP/('test_original_'+kind+'.py');target.write_text(text,encoding='utf-8')
    for name in ('test_transport','test_original_partially','test_original_cold_start'):
        log=TOP/'reproducibility'/(name+'.log');log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('w',encoding='utf-8') as f:
            proc=subprocess.run([sys.executable,'-X','utf8','-B',str(TOP/(name+'.py'))],stdout=f,stderr=subprocess.STDOUT)
        results.append({'test':name,'exit_code':proc.returncode,'log':str(log)})
        print(json.dumps(results[-1]),flush=True)
        if proc.returncode:print(log.read_text('utf-8')[-5000:],flush=True);break
    passed=len(results)==3 and all(x['exit_code']==0 for x in results)
    save(TOP/'reproducibility/offline_tests.json',{'status':'PASS' if passed else 'FAIL','suites':results,'new_api_requests':0,'methods':'Unmodified official main with synthetic responses. All trial output files are isolated under reproducibility.'})
    return 0 if passed else 1
if __name__=='__main__':sys.exit(main())
