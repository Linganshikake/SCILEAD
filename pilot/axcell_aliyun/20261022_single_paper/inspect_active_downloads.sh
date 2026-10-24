set -eu
python3 - <<'PY'
import json,subprocess,os
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
owner=json.loads((r/'pip_install_relay_linux_owner.json').read_text())
rows=subprocess.check_output(['ps','-eo','pid=,pgid=,rss=,etimes=,comm='],text=True).splitlines()
for line in rows:
 f=line.split()
 if len(f)!=5 or int(f[1])!=owner['pgid']:continue
 print('TASK_PROCESS',line)
 for fd in (Path('/proc')/f[0]/'fd').glob('*'):
  try:
   target=os.readlink(str(fd))
   if target.startswith('/root/scilead/axcell/cache/') and '(deleted)' not in target:
    p=Path(target)
    if p.is_file():print(json.dumps({'open_task_file':target,'bytes':p.stat().st_size}))
  except OSError:pass
base=Path('/var/lib/containerd/io.containerd.content.v1.content/ingest')
print('LAYER_PARTIALS',json.dumps([{'directory':p.parent.name,'bytes':p.stat().st_size} for p in base.glob('*/data')]))
PY
