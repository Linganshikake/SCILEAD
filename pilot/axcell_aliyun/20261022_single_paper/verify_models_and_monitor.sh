set -eu
cd /root/scilead/axcell
python3 - <<'PY'
from pathlib import Path
import hashlib,json,tarfile
r=Path('/root/scilead/axcell');m=json.loads((r/'manifests/transfer_manifest.json').read_text())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
a=r/m['model_archive']['relative']
assert a.stat().st_size==m['model_archive']['bytes'] and digest(a)==m['model_archive']['sha256']
expected={e['relative']:e for e in m['model_files']}
with tarfile.open(a,'r:xz') as tf:
 for e in tf.getmembers():
  p=(r/e.name).resolve()
  assert p.is_relative_to(r)
  assert e.isdir() and e.name.rstrip('/')=='models' or e.isfile() and e.name in expected,e.name
  if e.isfile():assert not p.exists(),'Never overwrite a model'
 tf.extractall(r)
checks=[]
for e in m['model_files']:
 p=r/e['relative'];checks.append({'relative':e['relative'],'size_match':p.stat().st_size==e['bytes'],'sha256_match':digest(p)==e['sha256']})
assert all(x['size_match'] and x['sha256_match'] for x in checks)
(r/'runs/20261022_single_paper/remote_models_verification.json').write_text(json.dumps({'status':'VERIFIED','checks':checks,'model_loaded':False},indent=2))
print(json.dumps({'model_files_verified':len(checks),'model_loaded':False}))
PY
python3 /root/scilead/axcell/scripts/monitor.py --stage monitor_smoke --timeout 10 -- /bin/true
set +e
python3 /root/scilead/axcell/scripts/monitor.py --stage monitor_timeout_test --timeout 1 -- python3 -c 'import time; time.sleep(20)'
code=$?
set -e
test "$code" -eq 125
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/root/scilead/axcell/runs/20261022_single_paper/monitor_timeout_test_linux_status.json')
d=json.loads(p.read_text());assert d['stop_reason']=='OWNED_STAGE_TIMEOUT' and d['exit_code']==-15
print('Monitor graceful timeout test passed; only its test process group was stopped.')
PY
