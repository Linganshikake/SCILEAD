set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,os
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
d=json.loads((r/'pip_install_linux_status.json').read_text());assert d['stop_reason']=='TASK_STOP_REQUEST'
o=json.loads((r/'pip_install_linux_owner.json').read_text())
try:os.kill(o['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Previous pip process is still running')
PY
test ! -e "$RUN/pip_install_official_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-pip-official "python3 -u $ROOT/scripts/monitor.py --stage pip_install_official --timeout 3600 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install_official.log 2>&1"
tmux list-sessions -F '#{session_name}'
