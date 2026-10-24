set -eu
python3 - <<'PY'
import json,time,shutil,subprocess
from pathlib import Path
root=Path('/root/scilead/axcell');run=root/'runs/20261022_single_paper'
for stage in ['pip_consistency_fix','environment_validation','conversion','elasticsearch_start','extraction']:
 p=run/(stage+'_linux_status.json')
 if p.exists():
  d=json.loads(p.read_text());print(json.dumps({k:d.get(k) for k in ['stage','exit_code','stop_reason','seconds']}));continue
 p=run/(stage+'_linux_owner.json')
 if not p.exists():continue
 log=run/(stage+'.log');tail=log.read_text(errors='replace')[-700:] if log.exists() else ''
 print(json.dumps({'stage':stage,'active_log_tail':tail}))
tmp=root/'cache/tmp'
print('TEMP_FILES',json.dumps([{'name':str(p.relative_to(tmp)),'bytes':p.stat().st_size} for p in tmp.rglob('*') if p.is_file() and p.stat().st_size>1000000][-12:]))
base=Path('/var/lib/containerd/io.containerd.content.v1.content')
for sub in ['ingest','blobs/sha256']:
 print(sub,sum(p.stat().st_size for p in (base/sub).rglob('*') if p.is_file()))
print('DISK_FREE_GIB',round(shutil.disk_usage(root).free/2**30,3))
PY
