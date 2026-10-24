from pathlib import Path
import json,hashlib
R=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_formal42')
assert json.loads((R/'formal_remote_complete.json').read_text())['status']=='COMPLETE'
records=[]
for p in R.rglob('*'):
 if not p.is_file() or any(x in p.parts for x in ['cache','__pycache__','delivery']):continue
 if p.name=='artifact_manifest_remote.json' or p.suffix not in ['.json','.txt','.csv','.log','.md','.py']:continue
 records.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'artifact_manifest_remote.json').write_text(json.dumps(records,indent=2));print(json.dumps({'remote_artifact_files':len(records),'bytes':sum(x['bytes'] for x in records)}))
