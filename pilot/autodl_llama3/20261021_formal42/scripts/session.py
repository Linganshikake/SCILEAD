"""Task-specific pinned SSH transfer and detached launch. Credentials stay in memory."""
from pathlib import Path
import sys,json,argparse,hashlib,stat
R=Path(__file__).resolve().parents[1];PRE=Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021')
sys.path.insert(0,str(PRE/'scripts'))
from remote_client import connect,execute
RR='/root/autodl-tmp/scilead/runs/llama3/20261021_formal42'
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['push','start','status','collect','script','partial']);p.add_argument('--file',type=Path);a=p.parse_args();c=connect()
    try:
        if a.mode=='push':
            sf=c.open_sftp()
            def mkdir(path):
                if path=='/root/autodl-tmp/scilead/runs':return
                mkdir(path.rsplit('/',1)[0])
                try:sf.stat(path)
                except FileNotFoundError:sf.mkdir(path)
            files=[x for x in R.rglob('*') if x.is_file() and '__pycache__' not in x.parts and 'remote_snapshot' not in x.parts and x.suffix in ['.py','.json','.md'] and x.name not in ['session.py','protected_diagnostics.json','cs_transfer_progress.json'] and not x.name.endswith('.log')]
            records=[]
            for x in files:
                target=RR+'/'+x.relative_to(R).as_posix();data=x.read_bytes();mkdir(target.rsplit('/',1)[0])
                try:
                    with sf.open(target,'rb') as f:old=f.read()
                    assert old==data,'EXISTING_REMOTE_DIFFERS:'+x.name
                except FileNotFoundError:
                    with sf.open(target+'.uploading','wb') as f:f.write(data)
                    sf.rename(target+'.uploading',target)
                with sf.open(target,'rb') as f:assert hashlib.sha256(f.read()).digest()==hashlib.sha256(data).digest()
                records.append({'path':x.relative_to(R).as_posix(),'sha256':hashlib.sha256(data).hexdigest()})
            sf.close();print(json.dumps({'verified_uploaded_files':len(records)}))
        elif a.mode in ['start','partial']:
            marker='launch.json' if a.mode=='start' else 'partial_launch.json';script='remote_batch.py' if a.mode=='start' else 'remote_followup.py'
            code=f'''from pathlib import Path
import json,subprocess,os
r=Path({RR!r});marker=r/{marker!r};assert not marker.exists(),'ALREADY_LAUNCHED'
env=os.environ.copy();env.update(PYTHONHASHSEED='0',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',PYTHONUTF8='1')
with (r/{(script+'.log')!r}).open('ab') as log:p=subprocess.Popen(['/root/autodl-tmp/scilead/envs/llama/bin/python',str(r/'scripts'/{script!r})],stdout=log,stderr=log,env=env,start_new_session=True)
marker.write_text(json.dumps({{'pid':p.pid,'script':{script!r}}}));print(marker.read_text())
'''
            v=execute(c,'/root/miniconda3/bin/python -',code,timeout=30);print(json.dumps(v));assert v['exit_code']==0
        elif a.mode=='status':
            code=f'''from pathlib import Path
import json,subprocess
r=Path({RR!r});p=r/'batch_status.json';s=json.loads(p.read_text()) if p.exists() else {{}}
rows=s.pop('papers',{{}});s['paper_summary']=[{{'id':p,'generation':v.get('generation_status'),'parse':v.get('parse_status'),'records':v.get('records'),'reason':v.get('reason')}} for p,v in rows.items()]
s['stage_calls']={{str(p.relative_to(r)):len(list(p.glob('*/complete.json'))) for p in (r/'normalization').rglob('calls')}}
s['gpu']=subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout.strip()
for name in ['partial_status.json']:
 if (r/name).exists():s[name]=json.loads((r/name).read_text())
print(json.dumps(s))
'''
            v=execute(c,'/root/miniconda3/bin/python -',code,timeout=40);assert v['exit_code']==0;print(v['stdout'])
        elif a.mode=='script':
            assert a.file and a.file.resolve().is_relative_to(R.resolve())
            v=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',a.file.read_text(encoding='utf-8'),timeout=180);print(json.dumps(v));assert v['exit_code']==0
        else:
            sf=c.open_sftp();dest=R/'remote_snapshot';count=0
            def walk(remote,local):
                nonlocal count
                local.mkdir(parents=True,exist_ok=True)
                for entry in sf.listdir_attr(remote):
                    rp=remote+'/'+entry.filename;lp=local/entry.filename
                    if stat.S_ISDIR(entry.st_mode):
                        if entry.filename!='__pycache__':walk(rp,lp)
                    elif Path(entry.filename).suffix in ['.json','.txt','.csv','.log','.md','.py'] and entry.st_size<20000000:
                        if lp.exists() and lp.stat().st_size==entry.st_size and int(lp.stat().st_mtime)==entry.st_mtime:continue
                        with sf.open(rp,'rb') as f:data=f.read()
                        lp.write_bytes(data)
                        import os
                        os.utime(lp,(entry.st_atime,entry.st_mtime));count+=1
            walk(RR,dest);sf.close();print(json.dumps({'collected_files':count}))
    finally:c.close()
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'status':'FAILED','type':type(e).__name__,'detail':str(e) if isinstance(e,AssertionError) else 'withheld'}));raise SystemExit(1)
