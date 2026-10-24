"""Collect completed artifacts as one hash-verified archive, avoiding per-file RTT."""
from pathlib import Path
import sys,json,hashlib,tarfile
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\scripts')))
from remote_client import connect,execute
rr='/root/autodl-tmp/scilead/runs/llama3/20261021_formal42'
c=connect()
try:
    code=f'''from pathlib import Path
import json,hashlib,tarfile
r=Path({rr!r});assert json.loads((r/'formal_remote_complete.json').read_text())['status']=='COMPLETE'
rows=json.loads((r/'artifact_manifest_remote.json').read_text());archive=r/'export_snapshot.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as t:
 for x in rows:
  p=r/x['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'];t.add(p,arcname=x['path'],recursive=False)
 t.add(r/'artifact_manifest_remote.json',arcname='artifact_manifest_remote.json')
h=hashlib.sha256()
with archive.open('rb') as f:
 for b in iter(lambda:f.read(1048576),b''):h.update(b)
print(json.dumps({{'archive':str(archive),'bytes':archive.stat().st_size,'sha256':h.hexdigest(),'files':len(rows)+1}}))
'''
    result=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',code,timeout=180);assert result['exit_code']==0;info=json.loads(result['stdout'])
    dest=R/'download/export_snapshot.tar.gz';dest.parent.mkdir(parents=True,exist_ok=True);sf=c.open_sftp();sf.get(info['archive'],str(dest));sf.close()
    with dest.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==info['sha256']
    target=(R/'remote_snapshot').resolve();assert target.is_relative_to(R.resolve())
    with tarfile.open(dest,'r:gz') as t:
        members=t.getmembers()
        for m in members:
            assert m.isfile() and not m.issym() and not m.islnk()
            path=(target/m.name).resolve();assert path.is_relative_to(target) and '..' not in Path(m.name).parts
        t.extractall(target,members=members,filter='data')
    for x in json.loads((target/'artifact_manifest_remote.json').read_text(encoding='utf-8')):assert hashlib.sha256((target/x['path']).read_bytes()).hexdigest()==x['sha256']
    (R/'bundle_transfer_verified.json').write_text(json.dumps(info,indent=2),encoding='utf-8');print(json.dumps({'status':'BUNDLE_AND_ALL_FILES_SHA256_VERIFIED',**info}))
finally:c.close()
