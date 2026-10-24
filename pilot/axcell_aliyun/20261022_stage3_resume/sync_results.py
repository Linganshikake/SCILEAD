import sys,json,hashlib,zipfile,os
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));from client import remote,paramiko,execute
B='/root/scilead/axcell/runs/20261022_stage3_resume'
t=remote.connect()
try:
 code,out,err=execute(t,'PYTHONDONTWRITEBYTECODE=1 python3 -',(R/'final_audit.py').read_bytes(),120)
 (R/'final_audit.json').write_bytes(out);(R/'final_audit.stderr').write_bytes(err);assert code==0,err.decode()
 audit=json.loads(out);s=paramiko.SFTPClient.from_transport(t)
 payload='''from pathlib import Path
import json,zipfile
b=Path("%s")
assert json.loads((b/'batch_state.json').read_text())['status']!='RUNNING'
with zipfile.ZipFile(b/'delivery.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in b.rglob('*'):
  if p.is_file() and 'es_data' not in p.relative_to(b).parts and p.name not in ['delivery.zip','task.lock']:z.write(p,str(p.relative_to(b)))
print((b/'delivery.zip').stat().st_size)
'''%B
 code,o,e=execute(t,'python3 -',payload.encode(),120);assert code==0,e.decode()
 s.get(B+'/delivery.zip',str(R/'delivery.zip'))
 target=R/'remote_results';target.mkdir(exist_ok=True)
 with zipfile.ZipFile(R/'delivery.zip') as z:
  for entry in z.infolist():
   path=(target/entry.filename).resolve();assert os.path.commonpath([str(path),str(target.resolve())])==str(target.resolve())
  z.extractall(target)
 checks=[]
 for f in audit['files']:
  p=target/f['path'];checks.append(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'])
 (R/'sync_verification.json').write_text(json.dumps({'files':len(checks),'all_match':all(checks),'archive_bytes':(R/'delivery.zip').stat().st_size},indent=2),encoding='utf-8')
 print(json.dumps({'files':len(checks),'all_match':all(checks),'archive_bytes':(R/'delivery.zip').stat().st_size}))
finally:t.close()
