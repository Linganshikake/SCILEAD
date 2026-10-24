set -eu
python3 - <<'PY'
from pathlib import Path
import re,json
r=Path('/root/scilead/axcell');text=(r/'source/axcell/environment.yml').read_text();block=text.split('- pip:\n',1)[1]
lines=[]
for line in block.splitlines():
 if not line.strip():continue
 assert line.startswith('    - ')
 s=line[len('    - '):].strip().strip('"')
 if s=='torch==1.3.1':s='https://download.pytorch.org/whl/cpu/torch-1.3.1%2Bcpu-cp37-cp37m-linux_x86_64.whl'
 elif s=='torchvision==0.4.2':s='https://download.pytorch.org/whl/cpu/torchvision-0.4.2%2Bcpu-cp37-cp37m-linux_x86_64.whl'
 elif s=='.':s=str(r/'source/axcell')
 lines.append(s)
(r/'runs/20261022_single_paper/requirements-pip-cpu.txt').write_text('\n'.join(lines)+'\n')
# Restore the executable bits recorded in the pinned upstream Git tree.
for p in ['axcell/scripts/latex2html.sh','scripts/pull_docker_images.sh']:(r/'source/axcell'/p).chmod(0o755)
print(json.dumps({'requirements':lines,'only_build_variant_change':'torch 1.3.1+cpu and torchvision 0.4.2+cpu official CPU wheels; original environment.yml unchanged','restored_upstream_executable_bits':True},indent=2))
PY
