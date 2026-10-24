from pathlib import Path
import sys,json,time
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from client import remote,execute
t=remote.connect()
try:
 code,out,err=execute(t,'PYTHONDONTWRITEBYTECODE=1 python3 -',(R/'status.py').read_bytes(),30)
 (R/'status_latest.json').write_bytes(out);(R/'status_latest.stderr').write_bytes(err);assert code==0,err.decode()
 d=json.loads(out);summary={k:d[k] for k in ['batch','counts','records','memory']}
 summary['running']=[]
 for x in d['running_detail']:
  s=x['last_sample'] or {};summary['running'].append({'paper':x['paper_id'],'elapsed':s.get('elapsed'),'worker_gib':s.get('worker',0)/2**30,'cpu_seconds':s.get('worker_cpu_usage_usec',0)/1e6,'oom_kill':s.get('oom_kill'),'last_log':x['logs'].get('worker.stdout.log','')[-350:]})
 summary['failed']=[x for x in d['rows'] if x['status']=='FAILED']
 print(json.dumps(summary,ensure_ascii=True))
finally:t.close()
