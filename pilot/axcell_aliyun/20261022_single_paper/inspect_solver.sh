set -eu
/root/scilead/axcell/envs/bootstrap/micromamba --no-rc config list --all | grep -E 'repodata|shard|ssl_verify|remote_.*timeout|retry'
python3 - <<'PY'
from pathlib import Path
import json
p=Path('/root/scilead/axcell/runs/20261022_single_paper/conda_dry_run_linux_resources.jsonl')
d=json.loads(p.read_text().splitlines()[-1]);print('elapsed_seconds',d['elapsed_seconds'])
for x in d['owned_processes']:
 if x['name']=='micromamba':
  p=Path('/proc')/str(x['pid'])
  if p.exists():
   print('process_io', (p/'io').read_text())
   print('process_status', '\n'.join(l for l in (p/'status').read_text().splitlines() if l.startswith(('State:','VmRSS:','VmHWM:','Threads:'))))
PY
