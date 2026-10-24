set -eu
python3 - <<'PY'
from pathlib import Path
import json
for root in ['/root/scilead/axcell/cache/conda-pkgs','/root/scilead/axcell/envs/mamba-root/pkgs','/root/scilead/axcell/cache/tmp']:
 p=Path(root)
 if p.exists():print(root,json.dumps([{'name':f.name,'size':f.stat().st_size,'dir':f.is_dir()} for f in list(p.iterdir())[:35]]))
r=Path('/root/scilead/axcell/runs/20261022_single_paper');d=json.loads((r/'conda_install_linux_resources.jsonl').read_text().splitlines()[-1])
for x in d['owned_processes']:
 if x['name']=='micromamba':
  p=Path('/proc')/str(x['pid']);print('IO', (p/'io').read_text());print('WAIT',(p/'wchan').read_text())
  print('STATUS','\n'.join(l for l in (p/'status').read_text().splitlines() if l.startswith(('State:','VmRSS:','Threads:'))))
  print('OPEN_FILES',json.dumps([str(q.resolve()) for q in (p/'fd').iterdir() if str(q.resolve()).startswith('/root/scilead/axcell/')]))
PY
