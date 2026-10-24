from pathlib import Path
import os,sys,json,subprocess,time,hashlib,shutil,fcntl
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');OLD=ROOT/'runs/llama3/20261021_formal42'
def read(p):return json.loads(p.read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2));tmp.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=(R/'.workflow.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if (R/'workflow_complete.json').exists():print('ALREADY_COMPLETE');return
    started=time.monotonic();env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',HF_HOME=str(R/'cache'),HF_MODULES_CACHE=str(R/'cache/modules'),PYTHONUTF8='1')
    marker=R/'audit/remote_protected_before.json'
    if not marker.exists():
        records={str(p):sha(p) for p in OLD.rglob('*') if p.is_file()}
        for rel,digest in read(OLD/'config/remote_expected_hashes.json').items():
            p=ROOT/rel;assert sha(p)==digest;records[str(p)]=digest
        save(marker,records)
    assert all(sha(Path(p))==h for p,h in read(marker).items())
    gpu=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'],capture_output=True,text=True);assert not gpu.stdout.strip(),'OTHER_GPU_TASK_PRESENT'
    if (OLD/'cache/modules').exists() and not (R/'cache/modules').exists():shutil.copytree(OLD/'cache/modules',R/'cache/modules')
    state={'stages':{},'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    def run(name,args):
        state['current']=name;save(R/'workflow_status.json',state);t=time.monotonic()
        with (R/(name+'.log')).open('ab') as log:proc=subprocess.run([sys.executable,'-B',str(R/'scripts'/args[0]),*args[1:]],stdout=log,stderr=log,env=env)
        state['stages'][name]={'exit_code':proc.returncode,'seconds':time.monotonic()-t};save(R/'workflow_status.json',state);print(name,proc.returncode,flush=True);return proc.returncode==0
    indexed={stage:run('index_'+stage,['stage_runner.py','index',stage]) for stage in ['fully','partial','leaderboard']}
    full=indexed['fully'] and run('v2_fully',['stage_runner.py','v2','fully'])
    if full:run('v2_cs',['cs_runner.py','v2'])
    partial=indexed['partial'] and run('v2_partial',['stage_runner.py','v2','partial'])
    if partial and indexed['leaderboard']:run('v2_leaderboard',['stage_runner.py','v2','leaderboard'])
    diagnostic=run('diagnostic2048',['diagnostic2048.py'])
    if diagnostic and (R/'token2048_diagnostic/extraction/prepared_output.json').exists() and indexed['fully']:
        if run('diagnostic_fully',['stage_runner.py','diagnostic','fully']):run('diagnostic_cs',['cs_runner.py','diagnostic'])
    assert all(sha(Path(p))==h for p,h in read(marker).items()),'PROTECTED_REMOTE_FILE_CHANGED'
    state.update(seconds=time.monotonic()-started,protected_remote_files_unchanged=len(read(marker)),gpu_after=subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout,status='COMPLETE' if all(x['exit_code']==0 for x in state['stages'].values()) else 'PARTIAL_FAILURE')
    save(R/'workflow_complete.json',state);print(json.dumps(state),flush=True)
if __name__=='__main__':main()
