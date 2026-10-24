set -eu
python3 - <<'PY'
from pathlib import Path
import json,subprocess
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
p=r/'conda_dry_run_linux_resources.jsonl'
if p.exists():
 lines=p.read_text().splitlines();d=json.loads(lines[-1]);print(json.dumps({'elapsed':round(d['elapsed_seconds'],1),'owned_processes':d['owned_processes'],'available_gib':round(d['memory']['MemAvailable']/2**30,2),'oom_count':d['vmstat']['oom_kill']}))
c=Path('/root/scilead/axcell/cache/conda-pkgs/cache')
if c.exists():print('CACHE',json.dumps([{'name':p.name,'bytes':p.stat().st_size} for p in c.iterdir() if p.is_file()]))
print('DNS_OR_NETWORK_ERRORS',subprocess.run(['tail','-n','8',str(r/'conda_dry_run.log')],capture_output=True,text=True).stdout)
PY
