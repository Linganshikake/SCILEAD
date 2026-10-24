"""Publish final reports into a new remote delivery directory; preserve execution artifacts."""
from pathlib import Path
import sys,json,hashlib,tarfile
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021\scripts')))
from remote_client import connect,execute
assert json.loads((R/'verification.json').read_text(encoding='utf-8'))['status']=='PASS'
assert json.loads((R/'privacy_verification.json').read_text(encoding='utf-8'))['status']=='PASS'
files=[p for p in R.rglob('*') if p.is_file() and not any(x in p.relative_to(R).parts for x in ['remote_snapshot','cache','download','__pycache__']) and p.suffix in ['.json','.jsonl','.md','.py','.txt','.csv'] and p.name not in ['delivery_transfer_verified.json','artifact_sha256.json']]
records=[{'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
archive=R/'download/final_delivery.tar.gz';archive.parent.mkdir(exist_ok=True)
with tarfile.open(archive,'w:gz') as t:
    for p in files:t.add(p,arcname=p.relative_to(R).as_posix(),recursive=False)
archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest();rr='/root/autodl-tmp/scilead/runs/llama3/20261021_formal42';c=connect()
try:
    s=c.open_sftp();s.put(str(archive),rr+'/final_delivery.tar.gz');s.close()
    code=f'''from pathlib import Path
import json,hashlib,tarfile
r=Path({rr!r});archive=r/'final_delivery.tar.gz';assert hashlib.sha256(archive.read_bytes()).hexdigest()=={archive_hash!r}
records={records!r};target=r/'delivery';target.mkdir(exist_ok=True)
with tarfile.open(archive,'r:gz') as t:
 for m in t.getmembers():
  p=(target/m.name).resolve();assert p.is_relative_to(target.resolve()) and m.isfile() and not m.issym() and not m.islnk()
  data=t.extractfile(m).read();p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():assert p.read_bytes()==data,'EXISTING_DELIVERY_DIFFERS'
  else:p.write_bytes(data)
for x in records:assert hashlib.sha256((target/x['path']).read_bytes()).hexdigest()==x['sha256']
(r/'DELIVERY.md').write_text('# Final approved formal42 results\\n\\nFinal report: delivery/run_report.md\\nFinal manifest: delivery/experiment_manifest.json\\nIntegrity proof: delivery/verification.json\\nRaw execution records remain in the original extraction/normalization directories. The initial root manifest is preserved.\\n')
print(json.dumps({{'status':'ALL_DELIVERY_HASHES_MATCH','files':len(records),'remote_delivery':str(target)}}))
'''
    v=execute(c,'/root/autodl-tmp/scilead/envs/llama/bin/python -',code,timeout=180);assert v['exit_code']==0
    proof=json.loads(v['stdout']);proof['archive_sha256']=archive_hash;(R/'delivery_transfer_verified.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print(json.dumps(proof))
finally:c.close()
