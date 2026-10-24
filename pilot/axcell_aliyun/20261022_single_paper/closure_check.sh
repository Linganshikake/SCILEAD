set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
"$ROOT/envs/axcell-original/bin/python" -m pip check > "$RUN/pip_check_final.txt"
python3 - <<'PY'
import json,hashlib,subprocess,datetime
from pathlib import Path
r=Path('/root/scilead/axcell/runs/20261022_single_paper')
a=r/'attempts/console_progress_compat'
raw=json.loads((a/'raw_outputs/records.json').read_text())
out=json.loads((a/'scilead_compatible_outputs/output.json').read_text())
assert list(out)==['1511.08308.pdf']
pred=json.loads(out['1511.08308.pdf']['output'])
assert len(raw)==len(pred)==2
assert all(set(x)=={'Task','Dataset','Metric','Result'} and isinstance(x['Result'],str) for x in pred)
assert all(x=={'Task':y['task'],'Dataset':y['dataset'],'Metric':y['metric'],'Result':str(y['score'])} for x,y in zip(pred,raw))
status=json.loads((r/'extraction_console_fix_linux_status.json').read_text())
assert status['exit_code']==0 and status['stop_reason'] is None
assert not status['cleanup']['containers']['remaining_running_task_containers']
assert not status['cleanup']['process_group']['remaining_live_members']
assert (r/'extract_error.json').exists() and not (r/'raw_outputs/records.json').exists()
running=subprocess.check_output(['docker','ps','-q','--filter','label=scilead.task=axcell-single-20261022'],text=True).split()
sessions=subprocess.run(['tmux','list-sessions','-F','#{session_name}'],capture_output=True,text=True).stdout.splitlines()
task_sessions=[x for x in sessions if x.startswith('axcell-')]
listeners=subprocess.run(['ss','-H','-lnt'],capture_output=True,text=True,check=True).stdout.splitlines()
relay_listeners=[x for x in listeners if x.split()[3].endswith(':37141')]
assert not running and not task_sessions and not relay_listeners
result={'utc_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'valid_paper_count':1,'prediction_count':len(pred),'result_strings':True,'field_adapter_matches_original_output':True,'original_initialization_failure_preserved':True,'owned_containers_running':running,'owned_tmux_sessions':task_sessions,'temporary_pypi_relay_listeners':relay_listeners,'paid_api_calls':0,'normalization_executed':False,'batch_executed':False,'pip_check':(r/'pip_check_final.txt').read_text().strip()}
(r/'output_validation.json').write_text(json.dumps(result,indent=2))
rows=[]
for p in sorted(r.rglob('*')):
 if p.is_file() and p.name!='delivery_hashes.json':
  assert p.stat().st_size<50*1024*1024 and not p.name.endswith('.env')
  rows.append({'path':str(p.relative_to(r)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(r/'delivery_hashes.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(result));print('HASHED_DELIVERY_REPORTS',len(rows))
PY
