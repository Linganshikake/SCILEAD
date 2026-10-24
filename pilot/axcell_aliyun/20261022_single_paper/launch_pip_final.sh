set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,hashlib
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper';cache=r/'cache/public_python_artifacts'
assert json.loads((run/'docker_transport_fix_linux_status.json').read_text())['exit_code']==0
assert json.loads((run/'scispacy_artifact_verification.json').read_text())['gzip_crc_and_package_metadata_verified'] is True
assert not (run/'pip_install_final_linux_owner.json').exists()
artifacts=json.loads((run/'cpu_wheel_artifacts.json').read_text())
scispacy=json.loads((run/'scispacy_artifact_verification.json').read_text())
artifacts.append({'file':scispacy['file'],'bytes':scispacy['actual_bytes'],'sha256':scispacy['sha256'],'source_url':scispacy['source_url']})
artifacts.append({'file':'en_core_web_sm-2.2.5.tar.gz','bytes':12013172,'sha256':'60b69065c97fd2e4972c33300205e1dead3501d2e0bfd6a182c3a033e337caee','source_url':'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz'})
text=(run/'requirements-pip-cpu.txt').read_text();verified=[]
for row in artifacts:
 p=cache/row['file'];assert p.stat().st_size==row['bytes'];h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 assert h.hexdigest()==row['sha256']
 assert text.count(row['source_url'])==1;text=text.replace(row['source_url'],str(p))
 verified.append({'file':p.name,'bytes':p.stat().st_size,'sha256':h.hexdigest(),'source_url':row['source_url']})
text+='\n# Compatibility-only HTTP pins for original Docker SDK 4.1.0\nrequests==2.31.0\nurllib3==1.26.20\n'
(run/'requirements-pip-cpu-compatible-local.txt').write_text(text)
(run/'pip_local_artifact_verification.json').write_text(json.dumps(verified,indent=2))
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-pip-final "AXCELL_REQUIREMENTS_FILE=$RUN/requirements-pip-cpu-compatible-local.txt python3 -u $ROOT/scripts/monitor.py --stage pip_install_final --timeout 2400 -- bash $ROOT/scripts/install_pip.sh > $RUN/pip_install_final.log 2>&1"
