"""Authorized three-paper diagnostic only; unmodified author-adapter subprocesses."""
from pathlib import Path
import json,subprocess,time,os,fcntl,hashlib
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');PY=ROOT/'envs/llama/bin/python'
def read(p):return json.loads(p.read_text())
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(p)
def main():
    lock=(R/'.batch.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    queue=read(R/'config/diagnostic_queue.json');assert len(queue)==3
    assert {x['paper_id'] for x in queue}=={'D18-1105.pdf','2203.16804.pdf','1511.08308.pdf'}
    preflight=read(R/'preflight.json');assert preflight['status']=='PASS'
    start=time.monotonic();state={'status':'RUNNING','formal_started':False,'paid_api_calls':0,'papers':[]};save(R/'batch_status.json',state)
    env=os.environ.copy();env.update(PYTHONHASHSEED='0',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    for entry in queue:
        pid=entry['paper_id'];out=R/'extraction'/pid.removesuffix('.pdf');ext=out/'extraction'
        record={'paper_id':pid,'generation_status':'PENDING','parse_status':'PENDING','normalization_status':'BLOCKED','evaluation_status':'BLOCKED'};state['papers'].append(record)
        requests=list(out.rglob('request.json')) if out.exists() else []
        if requests:
            record.update(generation_status='BLOCKED',reason='PRIOR_REQUEST_NO_AUTOMATIC_REPLAY');save(R/'batch_status.json',state);continue
        observed=next(x for x in preflight['audit'] if x['paper_id']==pid)
        assert observed['eligible'] and observed['input_tokens']==entry['input_tokens'] and observed['prompt_sha256']==entry['prompt_sha256']
        gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,capture_output=True)
        if gpu.returncode or gpu.stdout.strip():
            record.update(generation_status='BLOCKED',reason='GPU_NOT_IDLE');save(R/'batch_status.json',state);continue
        out.mkdir(parents=True,exist_ok=True);record['generation_status']='RUNNING';save(R/'batch_status.json',state)
        t=time.monotonic();command=[str(PY),str(ROOT/'adapters/run_llama.py'),'extract','--model','llama3','--paper-id',pid,'--out',str(out)]
        save(out/'command.json',{'argv':command,'no_retry':True,'expected_prompt_sha256':entry['prompt_sha256']})
        with (out/'process.log').open('wb') as log:p=subprocess.run(command,env=env,stdout=log,stderr=log)
        record.update(exit_code=p.returncode,wall_seconds=time.monotonic()-t)
        complete=ext/'calls/000000/complete.json'
        if complete.exists():
            req=read(complete.with_name('request.json'));assert req['prompt_sha256']==entry['prompt_sha256']
            v=read(complete);record.update(generation_status='COMPLETE',usage=v)
        else:record.update(generation_status='FAILED',reason='NO_COMPLETED_GENERATION')
        if (ext/'validation.json').exists():
            validation=read(ext/'validation.json');record.update(parse_status='COMPLETE' if validation['valid'] else 'FAILED',original_adapter_validation=validation)
        else:record['parse_status']='BLOCKED'
        save(out/'state.json',record);save(R/'batch_status.json',state)
    state.update(status='DIAGNOSTIC_COMPLETE_FORMAL_BLOCKED',seconds=time.monotonic()-start,actual_generation_calls=sum(x['generation_status']=='COMPLETE' for x in state['papers']))
    state['final_gpu']=subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free','--format=csv,noheader'],text=True,capture_output=True).stdout.strip()
    save(R/'batch_status.json',state)
if __name__=='__main__':main()
