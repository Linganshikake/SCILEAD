set -euo pipefail
ROOT=/root/scilead/axcell
ENV=$ROOT/envs/axcell-original
RUN=$ROOT/runs/20261022_single_paper
REQUIREMENTS_FILE=${AXCELL_REQUIREMENTS_FILE:-$RUN/requirements-pip-cpu.txt}
export PATH="$ENV/bin:$PATH"
export TMPDIR=$ROOT/cache/tmp
export PIP_CACHE_DIR=$ROOT/cache/pip
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_CONFIG_FILE=/dev/null
export PIP_INDEX_URL=${AXCELL_PIP_INDEX_URL:-https://pypi.org/simple}
unset PIP_EXTRA_INDEX_URL PIP_TRUSTED_HOST
export PYTHONNOUSERSITE=1
export CUDA_VISIBLE_DEVICES=""
python - <<'PY'
import json,subprocess,re
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
rows=json.loads(subprocess.check_output(['python','-m','pip','list','--format=json']).decode())
p=r/'python_packages_after_http_fix.json'
if p.exists():assert json.loads(p.read_text())==rows,'Environment changed since original pip precheck; inspect before proceeding'
else:raise RuntimeError('Validated HTTP compatibility snapshot missing')
declared={'sentencepiece','elasticsearch','elasticsearch-dsl','scikit-learn','regex','scispacy','psutil','en-core-web-sm','en-core-sci-sm','torch','torchvision','fastai','fastprogress','axcell','colorama'}
norm=lambda s:re.sub(r'[-_.]+','-',s.lower())
constraints=[x['name']+'=='+x['version'] for x in rows if norm(x['name']) not in declared]
(r/'constraints-preserve-conda.txt').write_text('\n'.join(constraints)+'\n')
print('Original pip pins govern their declared packages; all other installed packages constrained.',flush=True)
PY
cd "$ROOT/source/axcell"
python -m pip install --no-input --index-url "$PIP_INDEX_URL" --retries 3 --timeout 60 -r "$REQUIREMENTS_FILE" -c "$RUN/constraints-preserve-conda.txt"
python -m pip check
python -m pip freeze > "$RUN/dependency_freeze.txt"
