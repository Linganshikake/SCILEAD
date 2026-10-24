set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,shutil
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'engrafo_pull_resume1_linux_status.json').read_text())['exit_code']==0
assert json.loads((r/'conversion_environment_validation.json').read_text())['status']=='PASS'
assert not (r/'conversion_linux_owner.json').exists()
assert shutil.disk_usage(r).free>20*2**30
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-conversion "python3 -u $ROOT/scripts/monitor.py --stage conversion --timeout 1200 -- bash $ROOT/scripts/run_stage.sh conversion > $RUN/conversion.log 2>&1"
tmux list-sessions -F '#{session_name}'
