from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from client import remote,paramiko
B='/root/scilead/axcell/runs/20261022_stage3/reports'
names=['extraction_status.csv','extraction_manifest.json','resource_usage.csv','extraction_summary.md','stage3_verification.json','resource_summary.json','resource_stop_analysis.md','resource_stop_diagnosis.json','error_inspection.md','prediction_source_inspection.json','environment_preflight.md','resume.md']
t=remote.connect()
try:
 s=paramiko.SFTPClient.from_transport(t)
 try:s.mkdir(B)
 except IOError:s.stat(B)
 for name in names:
  try:s.stat(B+'/'+name);raise RuntimeError('Existing delivered report protected: '+name)
  except FileNotFoundError:pass
  s.put(str(R/name),B+'/'+name)
 checks=[]
 for name in names:
  with s.open(B+'/'+name,'rb') as f:remote_hash=hashlib.sha256(f.read()).hexdigest()
  checks.append({'name':name,'sha256':remote_hash,'match':remote_hash==hashlib.sha256((R/name).read_bytes()).hexdigest()})
 (R/'report_delivery_verification.json').write_text(json.dumps({'remote':B,'files':checks,'all_match':all(x['match'] for x in checks)},indent=2),encoding='utf-8')
 print(json.dumps({'reports':len(checks),'all_match':all(x['match'] for x in checks)}))
finally:t.close()
