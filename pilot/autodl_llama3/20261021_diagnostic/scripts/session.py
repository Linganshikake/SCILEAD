"""Pinned existing SSH connection; no credential values in parameters or output."""
from pathlib import Path
import sys,json,argparse,hashlib,stat
R=Path(__file__).resolve().parents[1]
PRE=Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021')
sys.path.insert(0,str(PRE/'scripts'))
from remote_client import connect,execute
RR='/root/autodl-tmp/scilead/runs/llama3/20261021_diagnostic'
def main():
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['preflight','push','start','status','collect','publish']);args=a.parse_args()
    c=connect()
    try:
        if args.mode=='preflight':
            code=(R/'scripts/remote_preflight.py').read_text(encoding='utf-8').replace('__EXPECTED_HASHES__',repr(json.loads((R/'config/remote_expected_hashes.json').read_text(encoding='utf-8'))))
            v=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',code,timeout=180)
            (R/'preflight_command.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
            assert v['exit_code']==0,'PREFLIGHT_FAILED'
            result=json.loads(v['stdout']);(R/'preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:v for k,v in result.items() if k!='audit'}))
        elif args.mode in ['push','publish']:
            sf=c.open_sftp()
            def mkdir(p):
                if p=='/root/autodl-tmp/scilead/runs':return
                parent=p.rsplit('/',1)[0];mkdir(parent)
                try:sf.stat(p)
                except FileNotFoundError:sf.mkdir(p)
            paths=[R/'config/diagnostic_queue.json',R/'scripts/remote_batch.py',R/'generation_config.json',R/'preflight.json'] if args.mode=='push' else [p for p in R.rglob('*') if p.is_file() and p.suffix in ['.md','.json','.csv','.py','.txt'] and 'remote_snapshot' not in p.parts and '__pycache__' not in p.parts and p.name not in ['session.py','user_request.txt','preflight_command.json']]
            records=[]
            for p in paths:
                rel=p.relative_to(R).as_posix();target=RR+'/'+rel;data=p.read_bytes();mkdir(target.rsplit('/',1)[0])
                try:
                    with sf.open(target,'rb') as f:old=f.read()
                    if old!=data:raise RuntimeError('DELIVERY_CONFLICT')
                except FileNotFoundError:
                    with sf.open(target+'.uploading','wb') as f:f.write(data)
                    sf.rename(target+'.uploading',target)
                with sf.open(target,'rb') as f:assert hashlib.sha256(f.read()).digest()==hashlib.sha256(data).digest()
                records.append({'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            (R/(args.mode+'_transfer.json')).write_text(json.dumps(records,indent=2),encoding='utf-8');print(json.dumps({'files_verified':len(records)}));sf.close()
        elif args.mode=='start':
            code=f'''from pathlib import Path
import subprocess,json,os
r=Path({RR!r});marker=r/'launch.json'
assert not marker.exists(),'EXISTING_LAUNCH_NO_AUTOMATIC_RESTART'
env=os.environ.copy();env.update(PYTHONHASHSEED='0',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
with (r/'batch.log').open('ab') as log:
 p=subprocess.Popen(['/root/autodl-tmp/scilead/envs/llama/bin/python',str(r/'scripts/remote_batch.py')],stdout=log,stderr=log,env=env,start_new_session=True)
marker.write_text(json.dumps({{'pid':p.pid,'diagnostic_only':True,'maximum_calls':3}}));print(marker.read_text())
'''
            v=execute(c,'/root/miniconda3/bin/python -',code,timeout=30);assert v['exit_code']==0;print(v['stdout'])
        elif args.mode=='status':
            code=f'''from pathlib import Path
import json
r=Path({RR!r});p=r/'batch_status.json'
print(p.read_text() if p.exists() else '{{"status":"NOT_STARTED"}}')
'''
            v=execute(c,'/root/miniconda3/bin/python -',code,timeout=30);assert v['exit_code']==0;print(v['stdout'])
        elif args.mode=='collect':
            sf=c.open_sftp();dest=R/'remote_snapshot';count=0
            def walk(remote,local):
                nonlocal count
                local.mkdir(parents=True,exist_ok=True)
                for entry in sf.listdir_attr(remote):
                    rp=remote+'/'+entry.filename;lp=local/entry.filename
                    if stat.S_ISDIR(entry.st_mode):
                        if entry.filename!='__pycache__':walk(rp,lp)
                    elif Path(entry.filename).suffix in ['.json','.txt','.csv','.log','.md','.py'] and entry.st_size<10000000:
                        with sf.open(rp,'rb') as f:data=f.read()
                        lp.write_bytes(data);count+=1
            walk(RR,dest);sf.close();print(json.dumps({'collected_files':count}))
    finally:c.close()
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'detail':'credential values withheld'}));raise SystemExit(1)
