set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,subprocess,shutil
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'environment_validation_linux_status.json').read_text())['exit_code']==0
assert json.loads((r/'conversion_linux_status.json').read_text())['exit_code']==0
assert not (r/'elasticsearch_start_linux_owner.json').exists()
d=json.loads(subprocess.check_output(['docker','image','inspect','docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1']))[0]
assert any(x.endswith('@sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b') for x in d['RepoDigests'])
assert shutil.disk_usage(r).free>20*2**30
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-es-start "python3 -u $ROOT/scripts/monitor.py --stage elasticsearch_start --timeout 180 -- bash $ROOT/scripts/run_stage.sh elasticsearch_start > $RUN/elasticsearch_start.log 2>&1"
