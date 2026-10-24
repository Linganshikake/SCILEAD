set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 - <<'PY'
import json
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
assert json.loads((r/'elasticsearch_restart_console_fix_linux_status.json').read_text())['exit_code']==0
assert json.loads((r/'empty_progress_compatibility_test.json').read_text())['original_empty_console_failure_reproduced']
assert not (r/'extraction_console_fix_linux_owner.json').exists()
assert not (r/'attempts/console_progress_compat/raw_outputs').exists()
PY
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-extraction-fix "python3 -u $ROOT/scripts/monitor.py --stage extraction_console_fix --timeout 1800 -- bash $ROOT/scripts/run_stage.sh extraction_console_fix > $RUN/extraction_console_fix.log 2>&1"
