set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
export PATH="$ROOT/envs/axcell-original/bin:$PATH"
export PIP_CONFIG_FILE=/dev/null PIP_INDEX_URL=https://pypi.org/simple PIP_CACHE_DIR="$ROOT/cache/pip" TMPDIR="$ROOT/cache/tmp" PIP_DISABLE_PIP_VERSION_CHECK=1
unset PIP_EXTRA_INDEX_URL PIP_TRUSTED_HOST
python - <<'PY'
import json,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'pip_install_relay_linux_status.json').read_text())['stop_reason']=='TASK_STOP_REQUEST'
rows=json.loads(subprocess.check_output(['python','-m','pip','list','--format=json']).decode())
assert rows==json.loads((r/'conda_python_packages_before_pip.json').read_text())
(r/'constraints-http-fix.txt').write_text('\n'.join(x['name']+'=='+x['version'] for x in rows if x['name'].lower() not in ['requests','urllib3'])+'\n')
PY
python -m pip install --no-input --index-url https://pypi.org/simple --retries 2 --timeout 45 'requests==2.31.0' 'urllib3==1.26.20' -c "$RUN/constraints-http-fix.txt"
python - <<'PY'
import requests,urllib3,docker,json,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert requests.__version__=='2.31.0' and urllib3.__version__=='1.26.20'
c=docker.from_env(version='auto');v=c.version()
d={'requests':requests.__version__,'urllib3':urllib3.__version__,'docker_sdk':docker.__version__,'server':v.get('Version'),'server_api':v.get('ApiVersion'),'negotiated_api':c.api._version,'containers_property_is_stable':c.containers is c.containers,'no_containers_started':True,'rationale':'Compatibility-only transitive HTTP pins and explicit Docker API negotiation; no original environment.yml pins changed.'}
c.close();(r/'docker_transport_compatibility.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
rows=json.loads(subprocess.check_output(['python','-m','pip','list','--format=json']).decode())
before={x['name']:x['version'] for x in json.loads((r/'conda_python_packages_before_pip.json').read_text())}
after={x['name']:x['version'] for x in rows};diff={k:{'before':before.get(k),'after':v} for k,v in after.items() if before.get(k)!=v}
assert set(diff)=={'requests','urllib3'}
(r/'http_compatibility_package_diff.json').write_text(json.dumps(diff,indent=2))
(r/'python_packages_after_http_fix.json').write_text(json.dumps(rows,indent=2))
PY
