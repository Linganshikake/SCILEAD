set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
export PATH="$ROOT/envs/axcell-original/bin:$PATH"
export TMPDIR="$ROOT/cache/tmp" PIP_CACHE_DIR="$ROOT/cache/pip-mirror-transport" PIP_CONFIG_FILE=/dev/null
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple PIP_DISABLE_PIP_VERSION_CHECK=1
unset PIP_EXTRA_INDEX_URL PIP_TRUSTED_HOST
mkdir -p "$ROOT/cache/pypi-wheelhouse-unverified"
python -m pip download --no-input --retries 2 --timeout 30 --index-url https://mirrors.aliyun.com/pypi/simple --dest "$ROOT/cache/pypi-wheelhouse-unverified" -r "$RUN/requirements-pip-cpu-local-complete.txt" -c "$RUN/constraints-preserve-conda.txt"
python - <<'PY'
import json,hashlib,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper'
assert json.loads(subprocess.check_output(['python','-m','pip','list','--format=json']))==json.loads((run/'python_packages_after_http_fix.json').read_text())
rows=[]
for p in sorted((r/'cache/pypi-wheelhouse-unverified').iterdir()):
 assert p.is_file()
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 rows.append({'file':p.name,'bytes':p.stat().st_size,'sha256':h.hexdigest(),'status':'UNVERIFIED_PENDING_PRIMARY_PYPI_CHECK'})
(run/'wheelhouse_unverified_manifest.json').write_text(json.dumps(rows,indent=2));print('Downloaded files pending primary-source SHA256 audit:',len(rows))
PY
