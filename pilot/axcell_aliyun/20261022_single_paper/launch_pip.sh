set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path('/root/scilead/axcell/runs/20261022_single_paper/conda_install_linux_status.json').read_text())
assert d['exit_code']==0 and d['stop_reason'] is None
PY
test -x "$ROOT/envs/axcell-original/bin/python"
test ! -e "$RUN/pip_install_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-pip "python3 -u $ROOT/scripts/monitor.py --stage pip_install --timeout 3600 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install.log 2>&1"
tmux list-sessions -F '#{session_name}'
