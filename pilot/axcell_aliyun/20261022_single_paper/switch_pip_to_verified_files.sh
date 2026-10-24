set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/pip_install_final_linux_status.json"
test -f "$RUN/pypi_package_artifacts.json"
test "$(grep -c 'Installing collected packages:' "$RUN/pip_install_final.log" || true)" -eq 0
touch "$RUN/pip_install_final.stop"
python3 - <<'PY'
import json,time,os,hashlib
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper'
for i in range(30):
 if (run/'pip_install_final_linux_status.json').exists():break
 time.sleep(1)
assert json.loads((run/'pip_install_final_linux_status.json').read_text())['stop_reason']=='TASK_STOP_REQUEST'
owner=json.loads((run/'pip_install_final_linux_owner.json').read_text())
try:os.kill(owner['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Prior pip process has not stopped')
text=(run/'requirements-pip-cpu-compatible-local.txt').read_text()
for item in json.loads((run/'pypi_package_artifacts.json').read_text()):
 p=r/'cache/public_python_artifacts'/item['file']
 assert p.stat().st_size==item['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
 token=item['name']+'=='+item['version'];assert text.count(token)==1
 text=text.replace(token,str(p))
(run/'requirements-pip-cpu-local-complete.txt').write_text(text)
assert not (run/'pip_install_local_linux_owner.json').exists()
PY
tmux new-session -d -s axcell-single-pip-local "AXCELL_REQUIREMENTS_FILE=$RUN/requirements-pip-cpu-local-complete.txt python3 -u $ROOT/scripts/monitor.py --stage pip_install_local --timeout 1800 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install_local.log 2>&1"
