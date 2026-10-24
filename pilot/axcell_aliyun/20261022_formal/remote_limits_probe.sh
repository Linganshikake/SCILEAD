set -eu
python3 - <<'PY'
import datetime,json,subprocess
from pathlib import Path
cg=next(x.split('::',1)[1] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
root=Path('/sys/fs/cgroup');current=root/cg.lstrip('/');rows=[]
while True:
 row={'path':str(current)}
 for key in ['memory.max','memory.high','memory.current','memory.swap.max','cpu.max']:
  p=current/key;row[key]=p.read_text().strip() if p.exists() else None
 rows.append(row)
 if current==root:break
 current=current.parent
q=subprocess.run(['docker','info','--format','{{.DockerRootDir}}'],capture_output=True,text=True,check=True)
docker_root=q.stdout.strip()
out={'utc_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cgroup_ancestry':rows,'docker_root':docker_root,'docker_disk':subprocess.check_output(['df','-B1','-T',docker_root],text=True),'block_devices':subprocess.check_output(['lsblk','-f','-J'],text=True),'overcommit_memory':Path('/proc/sys/vm/overcommit_memory').read_text().strip(),'overcommit_ratio':Path('/proc/sys/vm/overcommit_ratio').read_text().strip(),'read_only':True}
print(json.dumps(out))
PY
