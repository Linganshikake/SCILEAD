set -eu
python3 - <<'PY'
import json
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper'
for p in (r/'cache/public_python_artifacts').glob('*'):
 print(json.dumps({'file':p.name,'bytes':p.stat().st_size}))
for name in ['scispacy_resume','engrafo_pull_resume1','elasticsearch_pull']:
 p=run/(name+'_linux_status.json')
 if p.exists():
  d=json.loads(p.read_text());print(json.dumps({'stage':name,'exit_code':d['exit_code'],'seconds':d['seconds']}))
 else:
  p=run/(name+'.log');print(name,p.read_text(errors='replace')[-300:] if p.exists() else 'NO_LOG')
PY
