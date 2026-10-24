from pathlib import Path
import json,subprocess
r=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup');s={}
for name in ['workflow_status.json','workflow_complete.json']:
 if (r/name).exists():s[name]=json.loads((r/name).read_text())
s['new_calls']={str(p.relative_to(r)):len(list(p.glob('*/complete.json'))) for p in r.rglob('new_calls')}
s['stages_done']={str(p.parent.relative_to(r)):json.loads(p.read_text()) for p in r.rglob('done.json')}
s['gpu']=subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True).stdout
if 'workflow_status.json' in s:
 current=s['workflow_status.json'].get('current');p=r/(current+'.log');s['current_log_tail']=p.read_text(errors='replace')[-1600:] if p.exists() else ''
print(json.dumps(s))
