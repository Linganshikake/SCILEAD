from pathlib import Path
import sys,json,hashlib,tarfile
R=Path(__file__).resolve().parents[1];RR='/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup'
sys.path.insert(0,str(Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\scripts')))
from remote_client import connect,execute
assert json.loads((R/'reports/verification.json').read_text(encoding='utf-8'))['status']=='PASS'
files=[p for p in R.rglob('*') if p.is_file() and p.suffix in ['.json','.md','.py','.txt','.csv','.log'] and not any(x in p.relative_to(R).parts for x in ['remote_snapshot','cache','__pycache__']) and p.name not in ['delivery_transfer.json','artifact_hashes.json']]
records=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
archive=R/'delivery.tar.gz'
with tarfile.open(archive,'w:gz') as t:
 for p in files:t.add(p,arcname=p.relative_to(R).as_posix(),recursive=False)
digest=hashlib.sha256(archive.read_bytes()).hexdigest();c=connect()
try:
 sf=c.open_sftp();sf.put(str(archive),RR+'/delivery.tar.gz');sf.close()
 code=f'''from pathlib import Path
import json,hashlib,tarfile
r=Path({RR!r});dest=r/'delivery';dest.mkdir(exist_ok=True);records={records!r}
assert hashlib.sha256((r/'delivery.tar.gz').read_bytes()).hexdigest()=={digest!r}
with tarfile.open(r/'delivery.tar.gz','r:gz') as t:
 for m in t.getmembers():
  p=(dest/m.name).resolve();assert p.is_relative_to(dest) and m.isfile() and not m.issym() and not m.islnk();p.parent.mkdir(parents=True,exist_ok=True);data=t.extractfile(m).read()
  if p.exists():assert p.read_bytes()==data,'DELIVERY_ALREADY_DIFFERS'
  else:p.write_bytes(data)
assert all(hashlib.sha256((dest/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in records)
(r/'DELIVERY.md').write_text('Final report: delivery/reports/run_report.md\\nV1/V2 comparison: delivery/format_v2/comparison_v1_v2.md\\nIndependent budget diagnostic: delivery/token2048_diagnostic/diagnostic_report.md\\n')
print(json.dumps({{'status':'PASS','files':len(records),'destination':str(dest)}}))
'''
 v=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',code,timeout=180);assert v['exit_code']==0
 proof=json.loads(v['stdout']);proof['archive_sha256']=digest;(R/'reports/delivery_transfer.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof))
finally:c.close()
