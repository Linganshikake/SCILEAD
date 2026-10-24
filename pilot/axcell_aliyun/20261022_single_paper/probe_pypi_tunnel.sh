set -eu
python3 - <<'PY'
import urllib.request,json,subprocess
from pathlib import Path
with urllib.request.urlopen('http://127.0.0.1:37141/simple/requests/',timeout=30) as r:
 body=r.read();assert r.status==200 and b'http://127.0.0.1:37141/files/packages/' in body and b'#sha256=' in body
print('Official PyPI HTML over loopback SSH: PASS; package SHA256 anchors preserved')
rows=subprocess.check_output(['ss','-lnt'],text=True).splitlines()
print('\n'.join(x for x in rows if ':37141' in x))
p=Path('/root/scilead/axcell/runs/20261022_single_paper/wheelhouse_resolve_linux_status.json')
print('WHEELHOUSE_STATUS',p.read_text() if p.exists() else 'RUNNING')
PY
