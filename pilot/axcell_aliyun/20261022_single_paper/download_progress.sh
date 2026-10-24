set -eu
python3 - <<'PY'
from pathlib import Path
import json,subprocess
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
for name in ['conda_dry_run','engrafo_pull']:
 p=r/(name+'_linux_resources.jsonl')
 if p.exists():
  d=json.loads(p.read_text().splitlines()[-1]);print(json.dumps({'stage':name,'elapsed_seconds':round(d['elapsed_seconds'],1),'available_gib':round(d['memory']['MemAvailable']/2**30,2),'owned_rss_mib':round(d['owned_rss_sum']/2**20,1)}))
 p=r/(name+'_linux_status.json')
 if p.exists():print('FINISHED',p.name,p.read_text())
 p=r/(name+'.log')
 if p.exists():print('LOG',name,p.read_text(errors='replace')[-1800:])
for path in ['/var/lib/containerd/io.containerd.content.v1.content/ingest','/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256']:
 p=Path(path)
 if p.exists():
  files=[f for f in p.glob('**/*') if f.is_file()];print(json.dumps({'path':path,'files':len(files),'bytes':sum(f.stat().st_size for f in files)}))
PY
