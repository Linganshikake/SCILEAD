set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
from pathlib import Path
import json,os
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
d=json.loads((r/'engrafo_pull_linux_status.json').read_text())
assert d['stop_reason']=='OWNED_STAGE_TIMEOUT',d
o=json.loads((r/'engrafo_pull_linux_owner.json').read_text())
try:os.kill(o['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Previous image pull still running; do not duplicate')
assert not (r/'engrafo_pull_resume1_linux_owner.json').exists()
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
test "$(df -B1 --output=avail / | tail -n 1)" -gt 21474836480
tmux new-session -d -s axcell-single-engrafo-resume "python3 -u $ROOT/scripts/monitor.py --stage engrafo_pull_resume1 --timeout 5400 -- bash $ROOT/scripts/pull_engrafo.sh > $RUN/engrafo_pull_resume1.log 2>&1"
tmux list-sessions -F '#{session_name}'
