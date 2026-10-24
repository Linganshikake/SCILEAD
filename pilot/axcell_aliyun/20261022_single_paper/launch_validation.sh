set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,shutil
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'pip_consistency_fix_linux_status.json').read_text())['exit_code']==0
assert not (r/'environment_validation_linux_owner.json').exists()
assert shutil.disk_usage(r).free>=20*2**30
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-validation "python3 -u $ROOT/scripts/monitor.py --stage environment_validation --timeout 180 -- bash $ROOT/scripts/run_stage.sh environment_validation > $RUN/environment_validation.log 2>&1"
