python3 - <<'PY'
import json
from pathlib import Path
p=Path('/root/scilead/axcell/runs/20261022_single_paper/dependency_pin_verification.json')
d=json.loads(p.read_text());print(json.dumps([x for x in d['checks'] if not x['match']]))
PY
