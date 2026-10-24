"""Upload/run once, inspect, or fetch the bounded P1 probe over the existing pinned SSH."""
from pathlib import Path
import hashlib, json, shlex, sys, time
OUT=Path(__file__).resolve().parent
REMOTE='/root/scilead/axcell/runs/20261022_formal/stage1'
SESSION='axcell-formal-p1'
sys.path.insert(0,str(OUT.parent.parent/'20261022_single_paper'))
import remote, paramiko

def execute(t,command,timeout=45):
    c=t.open_session(timeout=20); c.exec_command(command); c.shutdown_write()
    buf=bytearray(); err=bytearray(); start=time.monotonic()
    while True:
        if c.recv_ready():buf.extend(c.recv(65536))
        if c.recv_stderr_ready():err.extend(c.recv_stderr(65536))
        if c.exit_status_ready() and not c.recv_ready() and not c.recv_stderr_ready():break
        if time.monotonic()-start>timeout:raise TimeoutError('Check remote status before any retry')
        time.sleep(.05)
    return c.recv_exit_status(),buf.decode(),err.decode()

def main():
    mode=sys.argv[1]; assert mode in ('launch','peek','fetch')
    t=remote.connect(); s=paramiko.SFTPClient.from_transport(t)
    try:
        if mode=='launch':
            assert not (OUT/'launch_receipt.json').exists()
            before=json.loads((OUT/'remote_before.json').read_text(encoding='utf-8'))
            assert min(x['memory']['MemAvailable'] for x in before['memory_samples'])>=6*2**30
            assert before['disk_free_bytes']>=20*2**30 and before['running_containers']['stdout']==''
            for path in (REMOTE.rsplit('/',1)[0],REMOTE):
                try:s.stat(path)
                except FileNotFoundError:s.mkdir(path)
            for name in ('verify_saved_artifacts.py','runtime_probe.py','authorization_and_limits.json'):
                target=REMOTE+'/'+name
                try:s.stat(target)
                except FileNotFoundError:pass
                else:raise RuntimeError('Remote probe already exists; inspect before retry')
                s.put(str(OUT/name),target)
            launch='PYTHONDONTWRITEBYTECODE=1 python3 '+shlex.quote(REMOTE+'/runtime_probe.py')+' > '+shlex.quote(REMOTE+'/runtime.log')+' 2>&1'
            code,out,err=execute(t,'tmux new-session -d -s '+shlex.quote(SESSION)+' '+shlex.quote(launch))
            receipt={'session':SESSION,'exit_code':code,'stdout':out,'stderr':err,'remote':REMOTE,'stage':1,'completion_not_assumed':True}
            (OUT/'launch_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
            assert code==0
        elif mode=='peek':
            code,out,err=execute(t,'if test -f '+shlex.quote(REMOTE+'/runtime_result.json')+'; then cat '+shlex.quote(REMOTE+'/runtime_result.json')+'; else tmux has-session -t '+shlex.quote(SESSION)+' 2>/dev/null && echo RUNNING; tail -n 5 '+shlex.quote(REMOTE+'/runtime.log')+'; fi')
            print(out);print(err)
        else:
            allowed=['runtime_result.json','saved_artifact_verification.json','artifact_read.log','resource_samples.jsonl',
                     'service_launch_config.json','container_id.json','elasticsearch_version.json','elasticsearch_health.json',
                     'container_before_stop.json','container_after_stop.json','elasticsearch.log','attempt_started.json','runtime.log',
                     'runtime_probe.py','verify_saved_artifacts.py','authorization_and_limits.json']
            dest=OUT/'remote_reports';dest.mkdir(exist_ok=True)
            checks=[]
            for name in allowed:
                try:info=s.stat(REMOTE+'/'+name)
                except FileNotFoundError:continue
                data=s.open(REMOTE+'/'+name,'rb').read()
                assert len(data)==info.st_size
                local=dest/name
                assert not local.exists(), 'Never overwrite earlier evidence'
                local.write_bytes(data)
                checks.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            (OUT/'remote_transfer_manifest.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
            print(json.dumps({'files_fetched':len(checks),'destination':str(dest)}))
    finally:s.close();t.close()
if __name__=='__main__': main()
