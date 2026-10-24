set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json,hashlib
from pathlib import Path
r=Path('/root/scilead/axcell')
for p in (r/'cache/public_python_artifacts').glob('*'):
 print(json.dumps({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
print('INSTALL_SCRIPT_BYTES', (r/'scripts/install_pip.sh').stat().st_size)
p=r/'runs/20261022_single_paper/pip_install_official.log'
print('PIP_LOG_TAIL',p.read_text(errors='replace')[-2200:])
PY
