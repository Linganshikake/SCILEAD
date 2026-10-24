"""Read-only complete before/after verification; no model imports."""
import sys,json,hashlib,subprocess,datetime,shutil
from pathlib import Path
B=Path('/root/scilead/axcell/runs/20261022_stage3')
before=json.loads((B/'remote_before.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1024*1024),b''):h.update(v)
 return h.hexdigest()
def checkrows(rows):
 out=[]
 for x in rows:
  p=Path(x['path']);h=sha(p) if p.is_file() else None
  out.append({'path':str(p),'sha256':h,'match':h==x['sha256']})
 return out
frozen=[]
for p,d in before['frozen_files'].items():
 path=Path(p);h=sha(path) if path.is_file() else None
 frozen.append({'path':str(path),'match':h==d['sha256'],'sha256':h})
assets=checkrows(before['assets']);parsed=checkrows(before['parsed_artifacts'])
q=json.loads((B/'queue.json').read_text());paperchecks=[];new_attempts=[]
for x in q:
 run=B/'papers'/x['paper_id'];s=json.loads((run/'state.json').read_text());checks=[]
 for name,h in s.get('output_hashes',{}).items():checks.append((run/name).is_file() and sha(run/name)==h)
 entry={'paper_id':x['paper_id'],'status':s['status'],'files_verified':len(checks),'all_output_hashes_match':all(checks) if checks else None}
 if s['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY']:
  raw=json.loads((run/'raw_outputs/records.json').read_text());prov=json.loads((run/'raw_outputs/provenance.json').read_text())
  compat=json.loads((run/'scilead_compatible_outputs/output.json').read_text());tdmr=json.loads(compat[x['paper_id']]['output'])
  entry.update(record_count=len(raw),provenance_aligned=len(raw)==len(prov)==len(tdmr)==s['record_count'],result_strings=all(isinstance(t['Result'],str) for t in tdmr))
 if (run/'worker_start.json').exists():new_attempts.append(x['paper_id'])
 paperchecks.append(entry)
files=[]
for p in B.rglob('*'):
 if p.is_file() and 'es_data' not in p.relative_to(B).parts and p.name not in ['task.lock','delivery.zip','final_audit.json']:
  files.append({'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':sha(p)})
pip=subprocess.run(['/root/scilead/axcell/envs/axcell-original/bin/python','-m','pip','freeze'],capture_output=True,text=True)
running=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines()
vm={k:int(v) for k,v in (x.split() for x in Path('/proc/vmstat').read_text().splitlines()) if k in ['oom_kill','pswpin','pswpout']}
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_files':frozen,'assets':assets,'parsed':parsed,'papers':paperchecks,'new_attempts':new_attempts,'files':files,
 'dependency_freeze_unchanged':pip.stdout==before['pip_freeze']['stdout'],'running_containers':running,'vmstat':vm,'disk_free_bytes':shutil.disk_usage(B).free,
 'memory_available_bytes':next(int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))}))
