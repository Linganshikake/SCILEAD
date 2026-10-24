set -eu
python3 - <<'PY'
from pathlib import Path
import json,ctypes.util
c=Path('/root/scilead/axcell/cache/conda-pkgs/cache')
for p in c.glob('*.state.json'):
 d=json.loads(p.read_text());print(p.name,json.dumps(d))
print('libzstd',ctypes.util.find_library('zstd'))
PY
