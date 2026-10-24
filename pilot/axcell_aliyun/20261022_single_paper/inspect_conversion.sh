set -eu
python3 - <<'PY'
import json,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
for name in ['conversion_linux_status.json','conversion_result.json','conversion_container_config.json']:
 print(name,(r/name).read_text())
d=json.loads((r/'parsed_artifacts.json').read_text())
print('PARSED',json.dumps({k:v for k,v in d.items() if k!='tables'}))
print('TABLES',json.dumps([{k:v for k,v in row.items() if k!='cells'} for row in d['tables']]))
print('RUNNING_TASK_CONTAINERS',subprocess.check_output(['docker','ps','--filter','label=scilead.task=axcell-single-20261022','--format','{{.Names}}'],text=True))
PY
