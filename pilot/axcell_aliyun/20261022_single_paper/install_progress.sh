set -eu
python3 - <<'PY'
from pathlib import Path
import json,shutil
r=Path('/root/scilead/axcell/runs/20261022_single_paper');p=r/'conda_install_linux_resources.jsonl'
if p.exists():
 d=json.loads(p.read_text().splitlines()[-1]);print(json.dumps({'elapsed_seconds':round(d['elapsed_seconds'],1),'owned_rss_mib':round(d['owned_rss_sum']/2**20,1),'available_gib':round(d['memory']['MemAvailable']/2**30,2)}))
c=Path('/root/scilead/axcell/cache/conda-pkgs');files=[p for p in c.iterdir() if p.is_file() and p.name.endswith(('.conda','.tar.bz2'))]
print(json.dumps({'cached_package_files':len(files),'cached_package_bytes':sum(p.stat().st_size for p in files),'python_present':Path('/root/scilead/axcell/envs/axcell-original/bin/python').exists(),'gcc':shutil.which('gcc'),'g++':shutil.which('g++')}))
for p in [r/'conda_install_linux_status.json']:
 if p.exists():print(p.read_text())
for path in ['/var/lib/containerd/io.containerd.content.v1.content/ingest','/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256']:
 p=Path(path)
 if p.exists():
  fs=[f for f in p.glob('**/*') if f.is_file()];print(json.dumps({'path':path,'bytes':sum(f.stat().st_size for f in fs)}))
PY
