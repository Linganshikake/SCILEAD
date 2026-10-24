set -eu
python3 - <<'PY'
import json,os,subprocess,shutil
from pathlib import Path
def cmd(args):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
 return {'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
d={'meminfo':{l.split(':')[0]:l.split(':')[1].strip() for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemTotal:','MemAvailable:','SwapTotal:','SwapFree:'))},'cpu':os.cpu_count(),'disk':cmd(['df','-B1','-T','/']), 'inodes':cmd(['df','-i','/']), 'docker_service':cmd(['systemctl','is-active','docker']), 'docker_binary':shutil.which('docker'),'root_candidates':{p:Path(p).exists() for p in ['/root/scilead','/root/scilead/axcell','/opt/conda','/root/miniconda3']},'tools':{x:shutil.which(x) for x in ['python3','curl','wget','tar','tmux','screen','git','conda','micromamba']},'cgroups':{p:Path(p).read_text().strip() if Path(p).exists() else None for p in ['/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current','/sys/fs/cgroup/cpu.max']}}
if d['docker_service']['stdout'].strip()=='active':
 d['docker_info']=cmd(['docker','info','--format','{{json .}}'])
 d['containers']=cmd(['docker','ps','-a','--format','{{json .}}'])
 d['images']=cmd(['docker','image','ls','--digests','--format','{{json .}}'])
print(json.dumps(d,indent=2))
PY
