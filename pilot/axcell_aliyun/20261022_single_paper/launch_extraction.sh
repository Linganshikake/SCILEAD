set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,shutil
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'environment_validation_linux_status.json').read_text())['exit_code']==0
assert json.loads((r/'elasticsearch_start_linux_status.json').read_text())['exit_code']==0
assert not (r/'extraction_linux_owner.json').exists()
assert not (r/'raw_outputs').exists()
assert shutil.disk_usage(r).free>20*2**30
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-extraction "python3 -u $ROOT/scripts/monitor.py --stage extraction --timeout 1800 -- bash $ROOT/scripts/run_stage.sh extraction > $RUN/extraction.log 2>&1"
