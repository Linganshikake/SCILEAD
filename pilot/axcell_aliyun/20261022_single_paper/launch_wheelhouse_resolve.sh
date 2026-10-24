set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/pip_install_local_linux_status.json"
test "$(grep -c 'Installing collected packages:' "$RUN/pip_install_local.log" || true)" -eq 0
touch "$RUN/pip_install_local.stop"
python3 - <<'PY'
import json,time,os
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
for i in range(30):
 if (r/'pip_install_local_linux_status.json').exists():break
 time.sleep(1)
assert json.loads((r/'pip_install_local_linux_status.json').read_text())['stop_reason']=='TASK_STOP_REQUEST'
owner=json.loads((r/'pip_install_local_linux_owner.json').read_text())
try:os.kill(owner['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Prior pip process is still running')
assert not (r/'wheelhouse_resolve_linux_owner.json').exists()
PY
tmux new-session -d -s axcell-single-wheelhouse "python3 -u $ROOT/scripts/monitor.py --stage wheelhouse_resolve --timeout 1200 -- bash $ROOT/scripts/download_wheelhouse.sh > $RUN/wheelhouse_resolve.log 2>&1"
