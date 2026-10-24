"""Approved formal extraction, without model retries or changes to official algorithms."""
from pathlib import Path
import json,subprocess,time,os,fcntl,hashlib,shutil,sys,traceback
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');PY=ROOT/'envs/llama/bin/python'
sys.path.insert(0,str(R/'scripts'))
from format_candidate import audit
def read(p):return json.loads(p.read_text())
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2));tmp.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classify(pid,ext,target,expected):
    rec={'paper_id':pid,'generation_status':'FAILED','parse_status':'BLOCKED'}
    if not (ext/'calls/000000/complete.json').exists():return dict(rec,reason='NO_COMPLETED_GENERATION')
    usage=read(ext/'calls/000000/complete.json');req=read(ext/'calls/000000/request.json')
    assert req['prompt_sha256']==expected['prompt_sha256']
    data=read(ext/'output.json');assert list(data)==[pid]
    evidence=read(ROOT/'data/evidence'/(pid+'.json'))[pid];assert data[pid]['source_documents']==evidence
    raw=(ext/'calls/000000/response.txt').read_text();assert raw==data[pid]['output'];assert hashlib.sha256(raw.encode()).hexdigest()==usage['response_sha256']
    result=audit(raw);candidate=result.pop('candidate_text',None)
    ok=result['candidate_eligible'] and usage['actual_generation']['finish_reason']=='eos'
    rec.update(generation_status='COMPLETE',parse_status='COMPLETE' if ok else 'FAILED',usage=usage,format_audit=result,raw_output_sha256=sha(ext/'output.json'),input_evidence_sha256=sha(ROOT/'data/evidence'/(pid+'.json')),reason=None if ok else ('NON_EOS' if usage['actual_generation']['finish_reason']!='eos' else result['reason']))
    if ok:
        output=raw if result['raw_json_valid'] else candidate
        assert json.loads(output)==json.loads(candidate)
        save(target/'prepared_output.json',{pid:{'output':output,'source_documents':evidence}})
        rec.update(records=len(json.loads(output)),format_applied=not result['raw_json_valid'],prepared_sha256=sha(target/'prepared_output.json'))
    save(target/'format_audit.json',rec);return rec
def main():
    lock=(R/'.batch.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    approval=read(R/'approval.json');assert approval['scope_response']=='批准范围和评价口径并启动';assert sha(R/'scripts/format_candidate.py')==approval['parser_sha256']
    for rel,digest in read(R/'config/remote_expected_hashes.json').items():
        assert sha(ROOT/rel)==digest,'FROZEN_FILE_CHANGED:'+rel
    gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,capture_output=True)
    assert gpu.returncode==0 and not gpu.stdout.strip(),'GPU_NOT_IDLE'
    scope=read(R/'config/scope42.json');queue=read(R/'config/extraction_queue.json');reuse=read(R/'config/reuse.json');assert len(queue)==38 and len(reuse)==4
    audit_index={x['paper_id']:x for x in read(R/'preflight.json')['audit']}
    env=os.environ.copy();env.update(PYTHONHASHSEED='0',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',PYTHONUTF8='1')
    start=time.monotonic();state={'status':'EXTRACTION_RUNNING','paid_api_calls':0,'papers':{},'new_request_limit':38};save(R/'batch_status.json',state)
    for pid in scope['eligible_ids']:
        target=R/'extraction'/pid.removesuffix('.pdf');target.mkdir(parents=True,exist_ok=True)
        t=time.monotonic()
        try:
            if pid in reuse:
                ext=Path(reuse[pid]['remote_extraction']);assert sha(ext/'output.json')==reuse[pid]['output_sha256']
                if not (target/'raw').exists():shutil.copytree(ext,target/'raw')
                else:assert sha(target/'raw/output.json')==reuse[pid]['output_sha256']
                ext=target/'raw'
            else:
                ext=target/'extraction';existing=list(target.rglob('request.json'))
                if not (ext/'calls/000000/complete.json').exists():
                    if existing:
                        state['papers'][pid]={'generation_status':'BLOCKED','reason':'UNFINISHED_CHECKPOINT_NO_RETRY'};save(R/'batch_status.json',state);continue
                    state['papers'][pid]={'generation_status':'RUNNING'};save(R/'batch_status.json',state)
                    command=[str(PY),str(ROOT/'adapters/run_llama.py'),'extract','--model','llama3','--paper-id',pid,'--out',str(target),'--formal-authorized']
                    save(target/'command.json',{'argv':command,'no_retry':True})
                    with (target/'process.log').open('wb') as log:p=subprocess.run(command,env=env,stdout=log,stderr=log)
                    save(target/'process_exit.json',{'exit_code':p.returncode,'seconds':time.monotonic()-t})
            rec=classify(pid,ext,target,audit_index[pid]);rec['reused_generation']=pid in reuse;rec['phase_wall_seconds']=time.monotonic()-t
            state['papers'][pid]=rec
        except Exception as e:
            state['papers'][pid]={'generation_status':'FAILED','error_type':type(e).__name__,'reason':str(e),'traceback':traceback.format_exc()}
        save(target/'state.json',state['papers'][pid]);save(R/'batch_status.json',state)
    valid={};raw={}
    for pid in scope['eligible_ids']:
        target=R/'extraction'/pid.removesuffix('.pdf');ext=target/('raw' if pid in reuse else 'extraction')
        if (ext/'output.json').exists():raw.update(read(ext/'output.json'))
        if state['papers'][pid].get('parse_status')=='COMPLETE':valid.update(read(target/'prepared_output.json'))
    save(R/'extraction/raw_output.json',raw);save(R/'extraction/prepared_output.json',valid)
    cfg=read(R/'extraction/2020.findings-emnlp.378/raw/config.json');save(R/'extraction/config.json',cfg)
    state.update(status='EXTRACTION_COMPLETE',valid_papers=len(valid),failed_papers=[p for p in scope['eligible_ids'] if p not in valid],extraction_wall_seconds=time.monotonic()-start)
    save(R/'batch_status.json',state)
    if valid:
        state['status']='FULLY_LLM_RUNNING';save(R/'batch_status.json',state)
        out=R/'normalization/fully_llm';out.mkdir(parents=True,exist_ok=True)
        cmd=[str(PY),str(R/'scripts/run_stage.py'),'fully']
        with (out/'process.log').open('ab') as log:p=subprocess.run(cmd,env=env,stdout=log,stderr=log)
        state.update(status='READY_FOR_CS' if p.returncode==0 else 'FULLY_LLM_FAILED',fully_exit_code=p.returncode,total_wall_seconds=time.monotonic()-start);save(R/'batch_status.json',state)
if __name__=='__main__':main()
