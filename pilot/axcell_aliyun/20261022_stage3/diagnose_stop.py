import json,subprocess
from pathlib import Path
B=Path('/root/scilead/axcell/runs/20261022_stage3');R=B/'papers/1912.08777.pdf'
out={}
for name in ['state.json','resource_summary.json','cleanup.json','worker_unit_final.json','worker_exit.json','extraction_result.json','extract_error.json','raw_outputs/pipeline_events.json','es_final_inspect.json']:
 p=R/name
 if p.exists():out[name]=json.loads(p.read_text())
samples=json.loads((R/'all_resource_samples.json').read_text());out['sample_count']=len(samples)
out['sample_curve']=[{k:s.get(k) for k in ['utc','elapsed','phase','available','worker','worker_rss','es','oom_kill','worker_events']} for i,s in enumerate(samples) if i%5==0 or i>=len(samples)-4]
out['baseline_window']=samples[-46] if len(samples)>=46 else None
for name in ['worker.stdout.log','worker.stderr.log','controller_error.log','cleanup_samples.jsonl']:
 p=R/name
 if p.exists():out[name]=p.read_text(errors='replace')[-12000:]
out['guardian_state']=json.loads((B/'guardian_state.json').read_text())
out['files']=[str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and 'es_data' not in p.parts]
out['running_containers']=subprocess.check_output(['docker','ps','-q'],text=True)
out['units']=subprocess.check_output(['systemctl','list-units','--no-legend','--state=running','axcell-stage3*'],text=True)
out['kernel_tail']=subprocess.run(['journalctl','-k','--since','2026-10-22 18:03:00','--no-pager'],capture_output=True,text=True).stdout[-4000:]
print(json.dumps(out))
