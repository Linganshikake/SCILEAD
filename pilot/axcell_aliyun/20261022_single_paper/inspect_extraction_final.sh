set -eu
python3 - <<'PY'
import json,subprocess
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
for n in ['extraction_console_fix_linux_status.json','attempts/console_progress_compat/extraction_result.json','attempts/console_progress_compat/extract_error.json']:
 p=r/n
 if p.exists():print(n,p.read_text())
p=r/'extraction_console_fix.log'
if p.exists():print('LOG_TAIL',p.read_text(errors='replace')[-5000:])
for p in r.glob('extraction_console_fix*jsonl'):
 lines=p.read_text().splitlines()
 if lines:print('RESOURCE_LAST',lines[-1])
print('OWNED_RUNNING',subprocess.run(['docker','ps','--filter','label=scilead.task=axcell-single-20261022','--format','{{.Names}} {{.Status}}'],capture_output=True,text=True).stdout)
print('TASK_SESSIONS',subprocess.run(['tmux','list-sessions','-F','#{session_name}'],capture_output=True,text=True).stdout)
PY
