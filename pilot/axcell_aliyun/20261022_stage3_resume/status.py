from pathlib import Path
import json,collections,subprocess,time
B=Path('/root/scilead/axcell/runs/20261022_stage3_resume')
def read(name):
 p=B/name
 return json.loads(p.read_text()) if p.exists() else None
rows=[]
for p in (B/'papers').glob('*/state.json'):
 d=json.loads(p.read_text());rows.append({k:d.get(k) for k in ['status','record_count','reused','seconds','error','started_utc'] }|{'paper_id':p.parent.name})
running=[x for x in rows if x['status']=='RUNNING']
details=[]
for x in running:
 p=B/'papers'/x['paper_id']
 logs={f:(p/f).read_text(errors='replace')[-1600:] for f in ['worker.stdout.log','worker.stderr.log','controller_error.log'] if (p/f).exists()}
 sample=p/'resource_samples.jsonl'
 details.append({'paper_id':x['paper_id'],'logs':logs,'last_sample':json.loads(sample.read_text().splitlines()[-1]) if sample.exists() else None})
report={'batch':read('batch_state.json'),'counts':dict(collections.Counter(x['status'] for x in rows)), 'records':sum(x['record_count'] or 0 for x in rows),'rows':rows,'running_detail':details,
 'containers':subprocess.check_output(['docker','ps','--format','{{.Names}} {{.Status}}'],text=True),
 'memory':next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')),
 'controller_tail':(B/'controller.log').read_text()[-2000:] if (B/'controller.log').exists() else ''}
print(json.dumps(report))
