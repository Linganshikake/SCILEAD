set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,os
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'pip_install_tunnel_linux_status.json').read_text())['stop_reason']=='TASK_STOP_REQUEST'
assert not (r/'pip_install_compatible_linux_owner.json').exists()
old=(r/'requirements-pip-cpu-local-complete.txt').read_text()
(r/'requirements-pip-cpu-local-compatible.txt').write_text(old+'\n# AWS CLI transitive requirement: colorama <0.4.5\ncolorama==0.4.4\n')
PY
tmux new-session -d -s axcell-single-pip-compatible "AXCELL_PIP_INDEX_URL=http://127.0.0.1:37141/simple AXCELL_REQUIREMENTS_FILE=$RUN/requirements-pip-cpu-local-compatible.txt python3 -u $ROOT/scripts/monitor.py --stage pip_install_compatible --timeout 1200 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install_compatible.log 2>&1"
