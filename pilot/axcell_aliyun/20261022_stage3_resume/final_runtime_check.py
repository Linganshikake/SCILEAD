import json,subprocess
from pathlib import Path
B=Path('/root/scilead/axcell/runs/20261022_stage3_resume')
checks={}
for name,args in [('running_containers',['docker','ps','--format','{{.Names}}']),('active_task_services',['systemctl','list-units','--no-legend','--state=running','axcell-stage3*'])]:
 p=subprocess.run(args,capture_output=True,text=True);checks[name]={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
checks['all_new_cleanup_clean']=all(json.loads(p.read_text())['clean'] for p in (B/'papers').glob('*/cleanup.json'))
checks['new_cleanup_count']=len(list((B/'papers').glob('*/cleanup.json')))
checks['batch_state']=json.loads((B/'batch_state.json').read_text())
print(json.dumps(checks))
