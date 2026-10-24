set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/wheelhouse_resolve_linux_status.json"
touch "$RUN/wheelhouse_resolve.stop"
python3 - <<'PY'
import json,time,os
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
for i in range(30):
 if (r/'wheelhouse_resolve_linux_status.json').exists():break
 time.sleep(1)
assert json.loads((r/'wheelhouse_resolve_linux_status.json').read_text())['stop_reason']=='TASK_STOP_REQUEST'
owner=json.loads((r/'wheelhouse_resolve_linux_owner.json').read_text())
try:os.kill(owner['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Prior download process is still running')
assert not (r/'pip_install_tunnel_linux_owner.json').exists()
PY
tmux new-session -d -s axcell-single-pip-tunnel "AXCELL_PIP_INDEX_URL=http://127.0.0.1:37141/simple AXCELL_REQUIREMENTS_FILE=$RUN/requirements-pip-cpu-local-complete.txt python3 -u $ROOT/scripts/monitor.py --stage pip_install_tunnel --timeout 1200 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install_tunnel.log 2>&1"
