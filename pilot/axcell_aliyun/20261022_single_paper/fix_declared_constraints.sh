set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
export PATH="$ROOT/envs/axcell-original/bin:$PATH"
export PIP_CONFIG_FILE=/dev/null PIP_INDEX_URL=http://127.0.0.1:37141/simple PIP_CACHE_DIR="$ROOT/cache/pip" TMPDIR="$ROOT/cache/tmp" PIP_DISABLE_PIP_VERSION_CHECK=1
unset PIP_EXTRA_INDEX_URL PIP_TRUSTED_HOST
python - <<'PY'
import json,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
rows=json.loads(subprocess.check_output(['python','-m','pip','list','--format=json']))
(r/'packages_before_consistency_fix.json').write_text(json.dumps(rows,indent=2))
allow={'prompt-toolkit','jsonschema','pyyaml','websocket-client'}
(r/'constraints-consistency-fix.txt').write_text('\n'.join(x['name']+'=='+x['version'] for x in rows if x['name'].lower() not in allow)+'\n')
q=subprocess.run(['python','-m','pip','check'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(r/'pip_check_before_consistency_fix.txt').write_text(q.stdout)
PY
python -m pip install --no-input --retries 3 --timeout 60 --index-url "$PIP_INDEX_URL" 'prompt-toolkit==2.0.10' 'jsonschema==3.2.0' 'PyYAML==5.4.1' 'websocket-client==0.59.0' -c "$RUN/constraints-consistency-fix.txt"
python -m pip check > "$RUN/pip_check.txt"
python -m pip freeze > "$RUN/dependency_freeze.txt"
python - <<'PY'
import json,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
rows=json.loads(subprocess.check_output(['python','-m','pip','list','--format=json']))
before={x['name'].lower():x['version'] for x in json.loads((r/'packages_before_consistency_fix.json').read_text())}
after={x['name'].lower():x['version'] for x in rows}
diff={k:{'before':before.get(k),'after':v} for k,v in after.items() if before.get(k)!=v}
assert set(diff)=={'prompt-toolkit','jsonschema','pyyaml','websocket-client'}
(r/'declared_constraints_fix_diff.json').write_text(json.dumps(diff,indent=2))
(r/'final_python_packages.json').write_text(json.dumps(rows,indent=2));print(json.dumps(diff))
PY
