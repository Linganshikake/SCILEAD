set -eu
/root/scilead/axcell/envs/axcell-original/bin/python - <<'PY'
import sys,json
from pathlib import Path
sys.path.insert(0,'/root/scilead/axcell/scripts')
from run_single import safe_empty_console_progress
from fastprogress.fastprogress import ConsoleProgressBar
original_failed=False
try:list(ConsoleProgressBar([]))
except ZeroDivisionError:original_failed=True
assert original_failed
with safe_empty_console_progress():
 assert list(ConsoleProgressBar([]))==[]
 assert list(ConsoleProgressBar([1,2,3],display=False))==[1,2,3]
assert list(ConsoleProgressBar([1,2,3],display=False))==[1,2,3]
r={'original_empty_console_failure_reproduced':True,'empty_sequence_after_adapter':[],'nonempty_sequence_unchanged':True,'models_loaded':False,'model_predictions_generated':False,'library_files_modified':False}
Path('/root/scilead/axcell/runs/20261022_single_paper/empty_progress_compatibility_test.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
PY
