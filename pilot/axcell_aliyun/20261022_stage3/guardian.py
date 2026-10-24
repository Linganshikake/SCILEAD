"""Supplemental nonblocking kernel monitor; covers controller CLI waits and cleanup."""
import os,sys,json,time,signal,subprocess,datetime
from pathlib import Path
B=Path('/root/scilead/axcell/runs/20261022_stage3')
sys.path.insert(0,str(B))
from controller import meminfo,vmstat,cgread,save,write_tables
from policy import resource_stop
baseline=json.loads((B/'remote_before.json').read_text())['vmstat']['oom_kill']
def controller_pids():
 out=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   args=(p/'cmdline').read_bytes().split(b'\0')
   if b'controller.py' in args and (p/'cwd').resolve()==B:out.append(int(p.name))
  except (OSError,ProcessLookupError):pass
 return out
def kernel_sample(state,run):
 group='/system.slice/'+state['unit'];w=cgread(group);e={'memory':0};d=None
 ep=run/'es_initial_inspect.json'
 if ep.exists():
  d=json.loads(ep.read_text());pid=d['State']['Pid'];cg=Path('/proc',str(pid),'cgroup')
  if cg.exists():
   group2=cg.read_text().strip().split('::',1)[1]
   if d['Id'] in group2:e=cgread(group2)
 m=meminfo();v=vmstat()
 return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paper_id':run.name,'available':m['MemAvailable'],'worker':w['memory'],'es':e['memory'],**v},d
def stop_command(args,seconds):
 p=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:return p.wait(timeout=seconds)
 except subprocess.TimeoutExpired:p.kill();p.wait();return 'COMMAND_TIMEOUT'
save(B/'guardian_state.json',{'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controller_pids':controller_pids(),'method':'procfs/cgroup only for monitoring; no Docker/systemctl query waits'})
lastlog=0
while True:
 batch=json.loads((B/'batch_state.json').read_text())
 if batch['status'] in ['FINISHED','BLOCKED']:break
 active=[]
 for p in (B/'papers').glob('*/state.json'):
  state=json.loads(p.read_text())
  if state['status']=='RUNNING' and 'ownership_token' in state:active.append((p.parent,state))
 for run,state in active:
  try:s,d=kernel_sample(state,run)
  except (FileNotFoundError,ProcessLookupError):continue
  reason=resource_stop(s['available'],30*2**30,s['worker'],s['es'],s['oom_kill'],baseline,0)
  if time.monotonic()-lastlog>5 or reason:
   with (B/'guardian_samples.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
   lastlog=time.monotonic()
  if reason:
   save(B/'guardian_stop.json',{'reason':reason,'sample':s,'state':state})
   # Stop the verified controller before it can schedule another paper.
   for pid in controller_pids():os.kill(pid,signal.SIGTERM)
   actions=[]
   unit=state['unit'];token=state['ownership_token']
   assert unit=='axcell-stage3-worker-'+token+'.service'
   actions.append(stop_command(['systemctl','stop','--no-block',unit],3));time.sleep(2)
   if cgread('/system.slice/'+unit)['memory']:
    actions.append(stop_command(['systemctl','kill','--signal=KILL',unit],3))
   if d and d['Config']['Labels'].get('scilead.attempt')==token:
    actions.append(stop_command(['docker','stop','--time','2',d['Id']],5))
    # A failed stop never leads to unlimited retries. One force-stop of owned ID.
    if actions[-1]!=0:actions.append(stop_command(['docker','kill',d['Id']],3))
   state.update(status='FAILED',error=reason,resource_stop=reason,guardian_actions=actions);save(run/'state.json',state)
   queue=json.loads((B/'queue.json').read_text())
   for q in queue:
    target=B/'papers'/q['paper_id']/'state.json'
    if not target.exists():save(target,{'status':'BLOCKED' if q['status']=='PARSE_COMPLETE' else 'FAILED','error':reason if q['status']=='PARSE_COMPLETE' else q.get('error'),'record_count':None,'reused':False})
   write_tables(queue);batch.update(status='BLOCKED',stop_reason=reason,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(B/'batch_state.json',batch)
   save(B/'guardian_state.json',{'status':'STOPPED_RESOURCE','reason':reason,'actions':actions});sys.exit(2)
 time.sleep(1)
save(B/'guardian_state.json',{'status':'FINISHED','resource_stop':False,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
