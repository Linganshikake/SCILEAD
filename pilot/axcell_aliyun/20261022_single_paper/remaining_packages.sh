set -eu
python3 - <<'PY'
from pathlib import Path
from urllib.parse import urlparse
import json
r=Path('/root/scilead/axcell/runs/20261022_single_paper');c=Path('/root/scilead/axcell/cache/conda-pkgs');plan=json.loads((r/'conda_solve_plan.json').read_text())
rows=[]
for p in plan['actions']['LINK']:
 u=urlparse(p['url']);f=c/u.scheme/u.netloc/u.path.lstrip('/')
 size=f.stat().st_size if f.exists() else 0
 if size!=p['size']:rows.append({'name':p['name'],'expected':p['size'],'actual':size,'remaining':max(0,p['size']-size)})
print(json.dumps({'packages_total':len(plan['actions']['LINK']),'packages_pending':len(rows),'pending_bytes':sum(x['remaining'] for x in rows),'pending':rows},indent=2))
PY
