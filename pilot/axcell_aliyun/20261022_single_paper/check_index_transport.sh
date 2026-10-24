set -eu
MAMBA_USE_SHARDED_REPODATA=false /root/scilead/axcell/envs/bootstrap/micromamba --no-rc config list --all | grep use_sharded_repodata
python3 - <<'PY'
import urllib.request,json,time
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
d=json.loads((r/'conda_dry_run_linux_resources.jsonl').read_text().splitlines()[-1])
for x in d['owned_processes']:
 if x['name']=='micromamba' and Path('/proc',str(x['pid']),'io').exists():print('IO',Path('/proc',str(x['pid']),'io').read_text())
for sub in ['linux-64','noarch']:
 u='https://conda.anaconda.org/conda-forge/'+sub+'/repodata.json.zst';start=time.monotonic()
 try:
  with urllib.request.urlopen(u,timeout=15) as response:chunk=response.read(1024*1024);print(json.dumps({'subdir':sub,'first_megabyte_bytes':len(chunk),'seconds':round(time.monotonic()-start,2),'http_status':response.status}))
 except Exception as e:print(json.dumps({'subdir':sub,'error_type':type(e).__name__}))
PY
