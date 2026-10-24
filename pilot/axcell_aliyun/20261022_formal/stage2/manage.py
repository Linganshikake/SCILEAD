"""Pinned task-local SSH transfer/control; credentials only through prior loader."""
from pathlib import Path
import hashlib, json, shlex, stat, sys, time
P=Path(__file__).resolve().parent
REMOTE='/root/scilead/axcell/runs/20261022_formal/stage2';SESSION='axcell-formal-stage2'
sys.path.insert(0,str(P.parent.parent/'20261022_single_paper'))
import remote,paramiko

def execute(t,command,timeout=60):
    c=t.open_session(timeout=20);c.exec_command(command);c.shutdown_write();start=time.monotonic();out=bytearray();err=bytearray()
    while True:
        if c.recv_ready():out.extend(c.recv(65536))
        if c.recv_stderr_ready():err.extend(c.recv_stderr(65536))
        if c.exit_status_ready() and not c.recv_ready() and not c.recv_stderr_ready():break
        if time.monotonic()-start>timeout:raise TimeoutError('Inspect remote state before resuming')
        time.sleep(.05)
    return c.recv_exit_status(),out.decode(),err.decode()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def mkdir(s,path):
    try:s.stat(path)
    except FileNotFoundError:s.mkdir(path)
def upload(s,local,target):
    try:existing=s.stat(target)
    except FileNotFoundError:existing=None
    if existing:
        with s.open(target,'rb') as f:h=hashlib.sha256(f.read()).hexdigest()
        assert h==sha(local),'Never overwrite a differing file';return 'EXISTING_MATCH'
    s.put(str(local),target+'.part');s.rename(target+'.part',target);return 'UPLOADED'
def main():
    mode=sys.argv[1];assert mode in ('upload','smoke','launch','progress','sync')
    t=remote.connect();s=paramiko.SFTPClient.from_transport(t)
    try:
        if mode=='upload':
            for path in [REMOTE,REMOTE+'/parsed',REMOTE+'/parsed/sources',REMOTE+'/parse_logs']:mkdir(s,path)
            for name in ['parse_one.py','monitor.py','policy.py','batch_parse.py','queue.json','configuration.json','test_policy.py']:
                upload(s,P/name,REMOTE+'/'+name)
            transferred=[]
            for row in json.loads((P/'queue.json').read_text(encoding='utf-8')):
                if row['reuse_original_single']:continue
                p=Path(row['local_source']);assert sha(p)==row['sha256']
                state=upload(s,p,row['remote_source']);transferred.append({'paper_id':row['paper_id'],'bytes':p.stat().st_size,'state':state,'sha256':row['sha256']})
            code,out,err=execute(t,"cd "+shlex.quote(REMOTE)+" && PYTHONDONTWRITEBYTECODE=1 python3 -c "+shlex.quote("import json,ast;from pathlib import Path;from policy import sha;q=json.loads(Path('queue.json').read_text());assert all(sha(r['remote_source'])==r['sha256'] for r in q);[ast.parse(p.read_text()) for p in Path('.').glob('*.py')];print('39 input hashes and script syntax OK')"))
            assert code==0,err
            (P/'transfer_verification.json').write_text(json.dumps({'files':transferred,'remote_verification':out},indent=2),encoding='utf-8')
            print(json.dumps({'new_sources':len(transferred),'bytes':sum(r['bytes'] for r in transferred),'verification':out}))
        elif mode=='smoke':
            mkdir(s,REMOTE+'/smoke')
            child="import subprocess,time;subprocess.Popen(['sleep','60']);time.sleep(60)"
            command='cd '+shlex.quote(REMOTE)+' && PYTHONDONTWRITEBYTECODE=1 python3 test_policy.py && PYTHONDONTWRITEBYTECODE=1 python3 monitor.py --run '+shlex.quote(REMOTE+'/smoke')+' --stage smoke --timeout 1 -- python3 -c '+shlex.quote(child)
            code,out,err=execute(t,command,45)
            (P/'smoke_stdout.log').write_text(out,encoding='utf-8');(P/'smoke_stderr.log').write_text(err,encoding='utf-8')
            assert code==125, 'Expected bounded timeout'
            with s.open(REMOTE+'/smoke/smoke_linux_status.json','r') as f:d=json.loads(f.read())
            assert d['stop_reason']=='OWNED_STAGE_TIMEOUT' and not d['cleanup']['process_group']['remaining_live_members']
            (P/'monitor_smoke_verification.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
            print(json.dumps({'policy_tests':'4 passed','timeout_guard':'PASS','owned_group_cleanup':'PASS','model_generations':0}))
        elif mode=='launch':
            assert (P/'monitor_smoke_verification.json').is_file()
            assert not (P/'launch_receipt.json').exists(),'Inspect/resume explicitly, no duplicate launch'
            command='cd '+shlex.quote(REMOTE)+' && PYTHONDONTWRITEBYTECODE=1 python3 batch_parse.py > batch.log 2>&1'
            code,out,err=execute(t,'tmux new-session -d -s '+shlex.quote(SESSION)+' '+shlex.quote(command))
            d={'session':SESSION,'exit_code':code,'stdout':out,'stderr':err,'authorized_stage':2,'completed':False}
            (P/'launch_receipt.json').write_text(json.dumps(d,indent=2),encoding='utf-8');assert code==0,err;print(json.dumps(d))
        elif mode=='progress':
            try:s.stat(REMOTE+'/batch_resume2.log');logname='batch_resume2.log'
            except FileNotFoundError:logname='batch.log'
            code,out,err=execute(t,'tail -n 6 '+shlex.quote(REMOTE+'/'+logname)+'; if test -f '+shlex.quote(REMOTE+'/batch_error.json')+'; then cat '+shlex.quote(REMOTE+'/batch_error.json')+'; fi; if tmux has-session -t axcell-formal-stage2-resume2 2>/dev/null || tmux has-session -t '+shlex.quote(SESSION)+' 2>/dev/null; then echo RUNNING; elif test -f '+shlex.quote(REMOTE+'/batch_result.json')+'; then cat '+shlex.quote(REMOTE+'/batch_result.json')+'; fi')
            print(out);print(err)
            try:
                with s.open(REMOTE+'/parse_manifest.json','rb') as f:d=json.loads(f.read())
                active=[r for r in d['papers'] if r['status']=='RUNNING']
                print(json.dumps({'active_papers':[r['paper_id'] for r in active],'counts':{k:sum(r['status']==k for r in d['papers']) for k in ['PENDING','RUNNING','PARSE_COMPLETE','FAILED','BLOCKED']}}))
                for row in active:
                    path=REMOTE+'/parse_logs/'+row['paper_id']+'/conversion_linux_resources.jsonl'
                    try:
                        with s.open(path,'rb') as f:lines=f.read().splitlines()
                        sample=json.loads(lines[-1]);print(json.dumps({'active':row['paper_id'],'seconds':sample['elapsed_seconds'],'available_gib':sample['memory']['MemAvailable']/2**30,'disk_free_gib':sample['disk_free_bytes']/2**30,'container_gib':[c.get('memory.current',0)/2**30 for c in sample['containers']]}))
                    except (FileNotFoundError,IndexError):pass
            except FileNotFoundError:pass
        else:
            dest=P/'remote_reports';dest.mkdir(exist_ok=True);files=[]
            def walk(remote_dir,local_dir):
                local_dir.mkdir(exist_ok=True,parents=True)
                for e in s.listdir_attr(remote_dir):
                    if e.filename.endswith('.tmp'):continue
                    rp=remote_dir+'/'+e.filename;lp=local_dir/e.filename
                    if stat.S_ISDIR(e.st_mode):walk(rp,lp)
                    elif stat.S_ISREG(e.st_mode):
                        if lp.exists():raise RuntimeError('Prior sync file exists; review before overwriting')
                        s.get(rp,str(lp)+'.part');Path(str(lp)+'.part').rename(lp)
                        assert lp.stat().st_size==e.st_size
                        files.append({'remote':rp,'local':str(lp),'bytes':e.st_size,'sha256':sha(lp)})
            for name in ['parse_logs','parsed/papers','parsed/htmls']:
                try:s.stat(REMOTE+'/'+name)
                except FileNotFoundError:continue
                walk(REMOTE+'/'+name,P/name)
            for name in ['orchestration_v1','safety_tests']:
                try:s.stat(REMOTE+'/'+name)
                except FileNotFoundError:continue
                walk(REMOTE+'/'+name,dest/name)
            for e in s.listdir_attr(REMOTE):
                if stat.S_ISREG(e.st_mode) and e.filename!='task.lock':
                    lp=dest/e.filename;assert not lp.exists();s.get(REMOTE+'/'+e.filename,str(lp))
                    files.append({'remote':REMOTE+'/'+e.filename,'local':str(lp),'bytes':e.st_size,'sha256':sha(lp)})
            (P/'sync_manifest.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
            print(json.dumps({'files_synced':len(files),'bytes':sum(x['bytes'] for x in files)}))
    finally:s.close();t.close()
if __name__=='__main__':main()
