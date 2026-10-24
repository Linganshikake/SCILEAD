set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/pip_install_relay_linux_status.json"
test "$(grep -c 'Installing collected packages:' "$RUN/pip_install_relay.log" || true)" -eq 0
touch "$RUN/pip_install_relay.stop"
python3 - <<'PY'
import time,json,os,shutil
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper';p=run/'pip_install_relay_linux_status.json'
for i in range(20):
 if p.exists():break
 time.sleep(1)
assert p.exists()
d=json.loads(p.read_text());assert d['stop_reason']=='TASK_STOP_REQUEST'
owner=json.loads((run/'pip_install_relay_linux_owner.json').read_text())
try:os.kill(owner['pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('pip process still alive')
files=list((r/'cache/tmp').glob('pip-unpack-*/en_core_sci_sm-0.2.4.tar.gz'))
assert len(files)==1
source=files[0];assert 0<source.stat().st_size<17042664
dest=r/'cache/public_python_artifacts/en_core_sci_sm-0.2.4.tar.gz.part';assert not dest.exists()
shutil.copy2(source,dest)
(run/'scispacy_resume_origin.json').write_text(json.dumps({'original_partial':str(source),'preserved_partial':str(dest),'bytes':dest.stat().st_size,'source_url':'https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz','expected_size':17042664},indent=2))
print(json.dumps({'pip_stopped_before_install':True,'partial_bytes_preserved':dest.stat().st_size}))
PY
