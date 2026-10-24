set -eu
/root/scilead/axcell/envs/axcell-original/bin/python - <<'PY'
import docker,json
from pathlib import Path
c=docker.from_env();v=c.version()
d={'sdk':docker.__version__,'server':v.get('Version'),'api':v.get('ApiVersion'),'containers_property_is_stable':c.containers is c.containers,'no_container_started':True}
Path('/root/scilead/axcell/runs/20261022_single_paper/docker_sdk_probe.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));c.close()
PY
