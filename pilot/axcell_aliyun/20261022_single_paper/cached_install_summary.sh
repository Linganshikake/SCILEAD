set -eu
python3 - <<'PY'
from pathlib import Path
import json
r=Path('/root/scilead/axcell/runs/20261022_single_paper');c=Path('/root/scilead/axcell/cache/conda-pkgs/https')
indices=list(c.glob('**/info/index.json'));archives=[p for p in c.glob('**/*') if p.is_file() and p.name.endswith(('.conda','.tar.bz2'))]
print(json.dumps({'extracted_package_count':len(indices),'archives_count':len(archives),'archive_bytes':sum(p.stat().st_size for p in archives)}))
for stage in ['conda_install','engrafo_pull','engrafo_pull_resume1','pip_install']:
 s=r/(stage+'_linux_status.json')
 if s.exists():print(s.name,s.read_text())
 elif (r/(stage+'_linux_resources.jsonl')).exists():
  p=r/(stage+'_linux_resources.jsonl');d=json.loads(p.read_text().splitlines()[-1]);print(json.dumps({'stage':stage,'elapsed_seconds':round(d['elapsed_seconds'],1),'available_gib':round(d['memory']['MemAvailable']/2**30,2)}))
for path in ['/var/lib/containerd/io.containerd.content.v1.content/ingest','/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256']:
 p=Path(path)
 if p.exists():
  fs=[f for f in p.glob('**/*') if f.is_file()];print(json.dumps({'path':path,'bytes':sum(f.stat().st_size for f in fs)}))
PY
