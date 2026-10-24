set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
if docker container inspect axcell-single-es >/dev/null 2>&1; then
 docker logs axcell-single-es > "$RUN/elasticsearch_service.log" 2>&1
fi
python3 "$ROOT/scripts/final_audit.py"
python3 - <<'PY'
import json,hashlib
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper'
rows=[]
for folder in [r/'scripts',r/'data/papers/1511.08308v5',r/'data/htmls/1511.08308v5']:
 if not folder.exists():continue
 for p in sorted(folder.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:
   rows.append({'path':str(p.relative_to(r)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(run/'task_artifact_hashes.json').write_text(json.dumps(rows,indent=2));print('TASK_HASHED_FILES',len(rows))
PY
