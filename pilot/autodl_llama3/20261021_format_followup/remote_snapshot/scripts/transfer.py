"""Pinned existing SSH; explicit user-authorized follow-up directory only."""
from pathlib import Path
import sys,json,hashlib,tarfile,argparse
R=Path(__file__).resolve().parents[1];RR='/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup'
sys.path.insert(0,str(Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\scripts')))
from remote_client import connect,execute
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['push','start','status','collect']);x=ap.parse_args();c=connect()
    try:
        if x.mode=='push':
            files=[p for p in R.rglob('*') if p.is_file() and p.relative_to(R).parts[0] in ['scripts','parser_v2','format_v2'] and p.suffix in ['.py','.json','.md','.txt'] and '__pycache__' not in p.parts]
            records=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
            archive=R/'input_bundle.tar.gz'
            with tarfile.open(archive,'w:gz') as t:
                for p in files:t.add(p,arcname=p.relative_to(R).as_posix(),recursive=False)
            sf=c.open_sftp()
            try:sf.stat(RR)
            except FileNotFoundError:sf.mkdir(RR)
            sf.put(str(archive),RR+'/input_bundle.tar.gz');sf.close()
            code=f'''from pathlib import Path
import tarfile,json,hashlib
r=Path({RR!r});records={records!r}
assert hashlib.sha256((r/'input_bundle.tar.gz').read_bytes()).hexdigest()=={hashlib.sha256(archive.read_bytes()).hexdigest()!r}
with tarfile.open(r/'input_bundle.tar.gz','r:gz') as t:
 for m in t.getmembers():
  p=(r/m.name).resolve();assert p.is_relative_to(r) and m.isfile() and not m.issym() and not m.islnk();data=t.extractfile(m).read();p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():assert p.read_bytes()==data,'EXISTING_REMOTE_DIFFERS'
  else:p.write_bytes(data)
assert all(hashlib.sha256((r/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in records)
(r/'input_transfer_manifest.json').write_text(json.dumps(records));print(json.dumps({{'uploaded_verified':len(records)}}))
'''
        elif x.mode=='start':
            code=f'''from pathlib import Path
import os,json,subprocess,shutil
r=Path({RR!r});assert not (r/'launch.json').exists(),'ALREADY_LAUNCHED'
env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
with (r/'workflow.log').open('ab') as log:p=subprocess.Popen(['/root/autodl-tmp/scilead/envs/llama/bin/python','-B',str(r/'scripts/remote_workflow.py')],stdout=log,stderr=log,env=env,start_new_session=True)
(r/'launch.json').write_text(json.dumps({{'pid':p.pid,'detached_session':True,'log':'workflow.log','automatic_retries':False}}));print((r/'launch.json').read_text())
'''
        elif x.mode=='status':
            code=f'''from pathlib import Path
import json,subprocess
r=Path({RR!r});s={{}}
for name in ['workflow_status.json','workflow_complete.json']:
 if (r/name).exists():s[name]=json.loads((r/name).read_text())
s['gpu']=subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout
s['calls']={{str(p.relative_to(r)):len(list(p.glob('*/complete.json'))) for p in r.rglob('new_calls')}}
s['log_tail']=(r/'workflow.log').read_text()[-2000:] if (r/'workflow.log').exists() else ''
for p in r.glob('*.log'):
 if p.stat().st_size:s[p.name]=p.read_text(errors='replace')[-900:]
print(json.dumps(s))
'''
        else:
            code=f'''from pathlib import Path
import json,tarfile,hashlib
r=Path({RR!r});files=[p for p in r.rglob('*') if p.is_file() and 'cache' not in p.relative_to(r).parts and '__pycache__' not in p.parts and p.suffix not in ['.gz']]
records=[{{'path':p.relative_to(r).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}} for p in files];(r/'export_manifest.json').write_text(json.dumps(records))
with tarfile.open(r/'export.tar.gz','w:gz') as t:
 for p in files+[r/'export_manifest.json']:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
print(json.dumps({{'sha256':hashlib.sha256((r/'export.tar.gz').read_bytes()).hexdigest(),'files':len(files)}}))
'''
        result=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',code,timeout=180);assert result['exit_code']==0,result['stderr'];print(result['stdout'])
        if x.mode=='collect':
            sf=c.open_sftp();archive=R/'export.tar.gz';sf.get(RR+'/export.tar.gz',str(archive));sf.close();assert hashlib.sha256(archive.read_bytes()).hexdigest()==json.loads(result['stdout'])['sha256']
            dest=R/'remote_snapshot';dest.mkdir(exist_ok=True)
            with tarfile.open(archive,'r:gz') as t:
                for m in t.getmembers():
                    p=(dest/m.name).resolve();assert p.is_relative_to(dest.resolve()) and m.isfile() and not m.issym() and not m.islnk();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
            records=json.loads((dest/'export_manifest.json').read_text());assert all(hashlib.sha256((dest/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in records)
            (R/'reports').mkdir(exist_ok=True);(R/'reports/transfer_verification.json').write_text(json.dumps({'status':'PASS','files':len(records),'archive_sha256':json.loads(result['stdout'])['sha256']}));print('ALL_TRANSFER_HASHES_MATCH')
    finally:c.close()
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'error_type':type(e).__name__,'details':str(e) if isinstance(e,AssertionError) else 'withheld'}));raise SystemExit(1)
