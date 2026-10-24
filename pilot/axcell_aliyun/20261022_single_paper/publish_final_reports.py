"""Publish only final, non-secret reports to this task's remote delivery directory."""
from pathlib import Path
import hashlib,json,stat
P=Path(__file__).resolve().parent
import remote,paramiko
NAMES=['README.md','single_paper_resource_report.md','run_report.md','manifest.json','final_config.json','resource_summary.json','verification.json','local_asset_integrity.json','output_inspection.json','pypi_transport_integrity.json','report_sync_manifest.json']
DEST='/root/scilead/axcell/runs/20261022_single_paper/delivery'
def sha(data):return hashlib.sha256(data).hexdigest()
t=remote.connect();s=paramiko.SFTPClient.from_transport(t);rows=[]
try:
 try:
  attrs=s.stat(DEST);assert stat.S_ISDIR(attrs.st_mode)
 except FileNotFoundError:s.mkdir(DEST)
 for name in NAMES:
  p=P/name;data=p.read_bytes();assert len(data)<2*1024*1024
  dst=DEST+'/'+name
  try:
   with s.open(dst,'rb') as f:existing=f.read()
   assert existing==data,'Existing published report differs; preserve before updating'
  except FileNotFoundError:
   s.put(str(p),dst+'.part');s.rename(dst+'.part',dst)
  with s.open(dst,'rb') as f:assert sha(f.read())==sha(data)
  rows.append({'local':name,'remote':dst,'bytes':len(data),'sha256':sha(data),'remote_readback_hash_matches':True})
 (P/'published_reports_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'published_reports':len(rows),'all_remote_readback_hashes_match':True}))
finally:s.close();t.close()
