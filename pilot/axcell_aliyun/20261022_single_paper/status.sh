set -eu
python3 - <<'PY'
import json,subprocess
from pathlib import Path
run=Path('/root/scilead/axcell/runs/20261022_single_paper')
for p in sorted(run.glob('*_linux_status.json')):
 d=json.loads(p.read_text());print(json.dumps({k:d[k] for k in ['stage','exit_code','stop_reason','seconds','peak_sampled_owned_process_group_rss_bytes'] if k in d}))
for p in sorted(run.glob('*.log')):
 if p.stem.startswith('monitor_') or (run/(p.stem+'_linux_status.json')).exists():continue
 s=p.read_text(errors='replace')
 print('LOG',p.name,'BYTES',p.stat().st_size,'TAIL',s[-1200:])
print('MEM',[(l.split(':')[0],l.split(':')[1].strip()) for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemAvailable:','SwapFree:'))])
print('SESSIONS',subprocess.run(['tmux','list-sessions','-F','#{session_name}'],capture_output=True,text=True).stdout)
PY
