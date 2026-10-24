set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,hashlib,os
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper'
status=json.loads((run/'pip_install_official_linux_status.json').read_text());assert status['exit_code']==1
assert 'Installing collected packages:' not in (run/'pip_install_official.log').read_text()
owner=json.loads((run/'pip_install_official_linux_owner.json').read_text())
try:os.kill(owner['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('Prior pip process remains active')
p=r/'cache/public_python_artifacts/en_core_web_sm-2.2.5.tar.gz'
assert p.stat().st_size==12013172
h=hashlib.sha256(p.read_bytes()).hexdigest();assert h=='60b69065c97fd2e4972c33300205e1dead3501d2e0bfd6a182c3a033e337caee'
original=(run/'requirements-pip-cpu.txt').read_text()
url='https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz'
assert original.count(url)==1
(run/'requirements-pip-cpu-relay.txt').write_text(original.replace(url,str(p)))
(run/'public_artifact_transfer_verification.json').write_text(json.dumps({'file':p.name,'bytes':p.stat().st_size,'sha256':h,'source_url':url,'transfer_verified':True,'upstream_checksum_available':False},indent=2))
PY
test ! -e "$RUN/pip_install_relay_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-pip-relay "AXCELL_REQUIREMENTS_FILE=$RUN/requirements-pip-cpu-relay.txt python3 -u $ROOT/scripts/monitor.py --stage pip_install_relay --timeout 3600 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install_relay.log 2>&1"
tmux list-sessions -F '#{session_name}'
