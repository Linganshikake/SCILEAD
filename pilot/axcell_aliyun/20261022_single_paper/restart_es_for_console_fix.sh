set -euo pipefail
python3 - <<'PY'
import subprocess,json,time,urllib.request
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'extract_error.json').read_text())['error_type']=='ZeroDivisionError'
d=json.loads(subprocess.check_output(['docker','inspect','axcell-single-es']))[0]
assert d['Config']['Labels']['scilead.task']=='axcell-single-20261022' and not d['State']['Running']
assert d['HostConfig']['Memory']==3*2**30
subprocess.run(['docker','start','axcell-single-es'],check=True)
start=time.monotonic()
while time.monotonic()-start<90:
 try:
  with urllib.request.urlopen('http://127.0.0.1:9200',timeout=4) as response:version=json.load(response)
  if version['version']['number']=='6.7.1':break
 except OSError:pass
 time.sleep(2)
else:raise RuntimeError('ES restart failed')
with urllib.request.urlopen('http://127.0.0.1:9200/_cat/indices?format=json',timeout=5) as response:indices=json.load(response)
assert indices==[],'Unexpected preexisting index; do not alter or delete it'
(r/'elasticsearch_restart_check.json').write_text(json.dumps({'version':'6.7.1','indices_before_inference':indices,'same_task_container_restarted':True,'first_attempt_failed_before_any_indexing':True},indent=2))
print('Same task Elasticsearch restarted, no preexisting indices.')
PY
