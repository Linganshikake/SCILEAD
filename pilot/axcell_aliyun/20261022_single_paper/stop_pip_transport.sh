set -eu
python3 - <<'PY'
from pathlib import Path
import json
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert not (r/'pip_install_linux_status.json').exists(),'Inspect finished state before changing anything'
s=(r/'pip_install.log').read_text()
assert 'Installing collected packages:' not in s,'Installation has begun; inspect before interruption'
(r/'pip_install.stop').write_text('Switch this task only from inherited HTTP pip mirror to official HTTPS PyPI; retain log and cache.\n')
print('Requested orderly stop of the owned pip download stage; no other processes targeted.')
PY
