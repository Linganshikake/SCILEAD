"""Serial CPU AxCell stage3, isolated ES per paper, durable attempt checkpoints."""
import os,sys,json,time,hashlib,shutil,subprocess,datetime,fcntl,csv,socket,urllib.request,traceback,uuid
from pathlib import Path
from policy import resource_stop,checkpoint_action,owned_unit,recovered_stop,owns_service,G
ROOT=Path('/root/scilead/axcell');BASE=ROOT/'runs/20261022_stage3'
PY=ROOT/'envs/axcell-original/bin/python'
IMAGE='sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b'
LABEL='axcell-stage3-20261022'
SINGLE=ROOT/'runs/20261022_single_paper/attempts/console_progress_compat'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp')
 with q.open('w') as f:json.dump(d,f,indent=2,ensure_ascii=False,allow_nan=False);f.flush();os.fsync(f.fileno())
 q.replace(p)
def cmd(args,check=True,timeout=25):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=timeout)
 if check and p.returncode:raise RuntimeError('Command failed: '+repr(args)+': '+p.stderr[-2000:])
 return {'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def meminfo():return {x.split(':')[0]:int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines()}
def vmstat():return {x.split()[0]:int(x.split()[1]) for x in Path('/proc/vmstat').read_text().splitlines() if x.split()[0] in ['oom_kill','pswpin','pswpout']}
def cgread(group):
 p=Path('/sys/fs/cgroup')/group.lstrip('/');r={'memory':0,'swap':0,'rss':0,'peak':None,'events':{}}
 if not group or not p.exists():return r
 for key,file in [('memory','memory.current'),('swap','memory.swap.current'),('peak','memory.peak')]:
  if (p/file).exists():r[key]=int((p/file).read_text())
 if (p/'memory.events').exists():r['events']={k:int(v) for k,v in (x.split() for x in (p/'memory.events').read_text().splitlines())}
 for f in p.rglob('cgroup.procs'):
  for pid in f.read_text().split():
   try:r['rss']+=int(Path('/proc',pid,'statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
   except (FileNotFoundError,ProcessLookupError):pass
 return r
def unitinfo(unit):
 assert owned_unit(unit)
 q=cmd(['systemctl','show',unit,'--property=ActiveState,SubState,Result,ExecMainStatus,ExecMainCode,ControlGroup,MemoryCurrent,MemoryPeak,Description,LoadState'],False)
 return dict(x.split('=',1) for x in q['stdout'].splitlines() if '=' in x)
def container(name):
 q=cmd(['docker','inspect',name],False)
 if q['code']:return None
 d=json.loads(q['stdout'])[0];assert d['Config'].get('Labels',{}).get('scilead.task')==LABEL
 return d
def dcgroup(d):
 if not d or not d['State']['Running']:return ''
 return Path('/proc',str(d['State']['Pid']),'cgroup').read_text().strip().split('::',1)[1]
def snapshot(unit,es,group=None):
 info=unitinfo(unit);d=container(es);cg=group or info.get('ControlGroup','')
 m=meminfo();w=cgread(cg);e=cgread(dcgroup(d));v=vmstat()
 return {'utc':utc(),'available':m['MemAvailable'],'free':shutil.disk_usage(BASE).free,'swap_used':m['SwapTotal']-m['SwapFree'],
         'worker':w['memory'],'worker_rss':w['rss'],'worker_peak':w['peak'],'worker_swap':w['swap'],'worker_events':w['events'],
         'es':e['memory'],'es_rss':e['rss'],'es_peak':e['peak'],'es_swap':e['swap'],'es_events':e['events'],**v,'unit':info}
def verify_outputs(run,state):
 files=state.get('output_hashes',{})
 return bool(files) and all((run/x).is_file() and sha(run/x)==h for x,h in files.items())
def outputhashes(run):
 return {str(x.relative_to(run)):sha(x) for folder in ['raw_outputs','scilead_compatible_outputs'] for x in (run/folder).rglob('*') if x.is_file()}
def write_tables(queue):
 rows=[]
 for q in queue:
  p=BASE/'papers'/q['paper_id']/'state.json'
  s=json.loads(p.read_text()) if p.exists() else {'status':'PENDING'}
  rows.append(dict(paper_id=q['paper_id'],tex_version=q['tex_version'],parse_status=q['status'],fragment_count=q.get('fragment_count'),table_count=q.get('table_count'),**s))
 save(BASE/'extraction_manifest.json',{'stage':3,'utc':utc(),'author36_membership':'UNVERIFIED','paid_api_calls':0,'normalization':'NOT_STARTED','rows':rows})
 fields=['paper_id','tex_version','parse_status','status','reused','record_count','seconds','exit_code','error','run_path']
 with (BASE/'extraction_status.csv.tmp').open('w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 (BASE/'extraction_status.csv.tmp').replace(BASE/'extraction_status.csv')
def setup_es(name,data,token):
 data.mkdir(parents=True,exist_ok=False);os.chown(data,1000,0)
 args=['docker','run','-d','--name',name,'--label','scilead.task='+LABEL,'--label','scilead.attempt='+token,'--memory','3g','--memory-swap','3g','--cpus','2',
 '--publish','127.0.0.1:9200:9200','--mount','type=bind,source='+str(data)+',target=/usr/share/elasticsearch/data',
 '--env','ES_JAVA_OPTS=-Xms1g -Xmx1g','--log-opt','max-size=20m','--log-opt','max-file=3','--user','elasticsearch','--entrypoint','elasticsearch',IMAGE,
 '-Ehttp.port=9200','-Etransport.host=localhost','-Ehttp.host=0.0.0.0','-Ebootstrap.system_call_filter=false','-Ehttp.cors.enabled=true','-Ehttp.cors.allow-origin=*','-Ehttp.cors.allow-headers=*','-Ehttp.cors.allow-credentials=true']
 return cmd(args)
def cleanup_command(args,unit,name,run):
 # Continue low-overhead monitoring while waiting, including timeout paths.
 p=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);start=time.monotonic()
 while p.poll() is None:
  sample={'utc':utc(),'available':meminfo()['MemAvailable'],'vmstat':vmstat(),'phase':'cleanup'}
  try:sample['resources']=snapshot(unit,name)
  except Exception as e:sample['monitor_error']=type(e).__name__
  with (run/'cleanup_samples.jsonl').open('a') as f:f.write(json.dumps(sample)+'\n')
  if time.monotonic()-start>10:
   p.kill();p.wait();raise TimeoutError('Cleanup command exceeded 10s')
  time.sleep(.25)
 return p.returncode
def stop_owned(unit,name,run,baseline_oom,token):
 result={'errors':[]};assert owned_unit(unit)
 # Independent cleanup paths: a timeout on one cannot skip the other.
 try:
  info=unitinfo(unit)
  if owns_service(info,token):
   try:result['unit_stop']=cleanup_command(['systemctl','stop',unit],unit,name,run)
   except Exception as e:result['errors'].append('unit_stop:'+repr(e))
   finally:
    info=unitinfo(unit)
    if owns_service(info,token) and info.get('ActiveState') in ['active','activating','deactivating']:
     result['unit_kill']=cmd(['systemctl','kill','--signal=KILL',unit],False,12)
  elif info.get('LoadState') not in [None,'not-found']:result['errors'].append('UNOWNED_UNIT_NOT_STOPPED')
 except Exception as e:result['errors'].append('unit_cleanup:'+repr(e))
 try:
  d=container(name)
  if d:
   assert d['Config']['Labels'].get('scilead.attempt')==token,'Unowned container'
   if d['State']['Running']:
    try:result['es_stop']=cleanup_command(['docker','stop','--time','2',d['Id']],unit,name,run)
    except Exception as e:result['errors'].append('es_stop:'+repr(e))
    finally:
     current=container(name)
     if current and current['Id']==d['Id'] and current['State']['Running']:
      result['es_kill']=cmd(['docker','kill',d['Id']],False,12)
   d=container(name);save(run/'es_final_inspect.json',d)
   log=cmd(['docker','logs',name],False);(run/'es_stdout.log').write_text(log['stdout']);(run/'es_stderr.log').write_text(log['stderr'])
  result['es_running']=bool(d and d['State']['Running'])
 except Exception as e:result['errors'].append('es_cleanup:'+repr(e));result['es_running']=True
 result['post_vmstat']=vmstat();result['unit_remaining']=unitinfo(unit)
 result['new_oom']=result['post_vmstat']['oom_kill']>baseline_oom
 result['clean']=not result['es_running'] and result['unit_remaining'].get('ActiveState') not in ['active','activating','deactivating']
 save(run/'cleanup.json',result);return result
def run_one(q,index,before):
 run=BASE/'papers'/q['paper_id'];run.mkdir(parents=True,exist_ok=True)
 token=uuid.uuid4().hex;unit='axcell-stage3-worker-'+token+'.service';es='axcell-stage3-es-'+token
 state={'status':'RUNNING','started_utc':utc(),'reused':False,'run_path':str(run),'unit':unit,'es_container':es,'ownership_token':token}
 save(run/'state.json',state);start=time.monotonic();baseline=vmstat();samples=[];reason=None;error='';exitcode=None;cleanup=None
 try:
  if meminfo()['MemAvailable']<6*G or shutil.disk_usage(BASE).free<20*G:
   reason='START_RESOURCE_GATE';raise RuntimeError(reason)
  assert not cmd(['docker','ps','-q'])['stdout'].strip(),'Other running container present'
  assert unitinfo(unit).get('LoadState')=='not-found' and container(es) is None,'Resource name conflict'
  sock=socket.socket();sock.bind(('127.0.0.1',9200));sock.close()
  inputs=run/'inputs'/q['tex_version'];shutil.copytree(q['parsed_paper_path'],inputs)
  expected=[x for x in before['parsed_artifacts'] if x['paper_id']==q['paper_id'] and '/papers/' in x['path']]
  assert expected and all(sha(inputs/Path(x['path']).name)==x['sha256'] for x in expected)
  save(run/'input_manifest.json',expected)
  setup_es(es,run/'es_data',token);save(run/'es_initial_inspect.json',container(es))
  es_ready=False
  for _ in range(90):
   s=snapshot(unit,es);s['elapsed']=time.monotonic()-start;s['phase']='es_start';samples.append(s)
   reason=resource_stop(s['available'],s['free'],s['worker'],s['es'],s['oom_kill'],baseline['oom_kill'],s['elapsed'])
   if reason:raise RuntimeError(reason)
   try:
    with urllib.request.urlopen('http://127.0.0.1:9200',timeout=1) as r:response=json.load(r)
    assert response['version']['number']=='6.7.1';es_ready=True;break
   except (OSError,ValueError):time.sleep(1)
  if not es_ready:reason='ES_START_FAILED';raise RuntimeError(reason)
  save(run/'worker_start.json',{'utc':utc(),'unit':unit,'paper_id':q['paper_id'],'attempt':1})
  args=['systemd-run','--quiet','--unit='+unit,'--property=Description=scilead-stage3-'+token,'--property=Type=exec','--property=RemainAfterExit=yes','--property=MemoryAccounting=yes',
        '--property=MemoryMax=18G','--property=MemorySwapMax=0','--property=CPUQuota=600%','--property=KillMode=control-group',
        '--property=TimeoutStopSec=2s','--property=RuntimeMaxSec=1850s','--property=WorkingDirectory='+str(run),
        '--property=StandardOutput=append:'+str(run/'worker.stdout.log'),'--property=StandardError=append:'+str(run/'worker.stderr.log'),
        '--setenv=PYTHONDONTWRITEBYTECODE=1','--setenv=PYTHONPATH='+str(ROOT/'source/axcell'),
        str(PY),'-B',str(BASE/'worker.py'),q['paper_id']]
  save(run/'worker_command.json',args);cmd(args)
  group=unitinfo(unit).get('ControlGroup','')
  while True:
   s=snapshot(unit,es,group);s['elapsed']=time.monotonic()-start;s['phase']='extraction';samples.append(s)
   with (run/'resource_samples.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
   reason=resource_stop(s['available'],s['free'],s['worker'],s['es'],s['oom_kill'],baseline['oom_kill'],s['elapsed'])
   if not reason and len(samples)>45:
    old=samples[-46];eventfile=run/'raw_outputs/pipeline_events.json'
    stale=time.time()-eventfile.stat().st_mtime if eventfile.exists() else s['elapsed']
    if s['worker']-old['worker']>2*G and stale>90:reason='SUSTAINED_MEMORY_GROWTH_NO_PROGRESS'
   if reason:raise RuntimeError(reason)
   info=s['unit']
   if info.get('SubState')=='exited' or info.get('ActiveState') in ['failed','inactive']:
    save(run/'worker_unit_final.json',info);exitcode=int(info.get('ExecMainStatus','-1'));break
   time.sleep(2)
  assert exitcode==0 and info.get('Result')=='success','Worker failed: '+repr(info)
  r=json.loads((run/'extraction_result.json').read_text());w=json.loads((run/'worker_exit.json').read_text())
  raw=json.loads((run/'raw_outputs/records.json').read_text());prov=json.loads((run/'raw_outputs/provenance.json').read_text())
  assert w['exit_code']==0 and r['paper_id']==q['paper_id'] and r['record_count']==len(raw)==len(prov)
  assert all(set(x)=={'task','dataset','metric','model','score'} for x in raw)
  assert all(sha(inputs/Path(x['path']).name)==x['sha256'] for x in expected),'Input copy modified'
  state.update(status=r['status'],record_count=r['record_count'],model_load_seconds=r['model_load_seconds'],inference_seconds=r['inference_seconds'],output_hashes=outputhashes(run),worker_maxrss_bytes=w['maxrss_bytes'])
 except Exception as e:
  error=type(e).__name__+': '+str(e);state.update(status='FAILED',error=error,record_count=None)
  (run/'controller_error.log').write_text(traceback.format_exc())
 finally:
  try:cleanup=stop_owned(unit,es,run,baseline['oom_kill'],token)
  except Exception:
   (run/'cleanup_error.log').write_text(traceback.format_exc());reason=reason or 'CLEANUP_FAILED'
  if cleanup and (not cleanup['clean'] or cleanup['new_oom']):reason=reason or 'CLEANUP_OR_OOM_FAILURE'
  if reason:state.update(status='FAILED',error=error or reason,resource_stop=reason)
  save(run/'all_resource_samples.json',samples)
  summary={'sample_count':len(samples),'peak_worker_cgroup':max([x['worker'] for x in samples] or [0]),'peak_worker_tree_rss':max([x['worker_rss'] for x in samples] or [0]),
           'peak_es_cgroup':max([x['es'] for x in samples] or [0]),'min_host_available':min([x['available'] for x in samples] or [0]),
           'peak_swap':max([x['swap_used'] for x in samples] or [0]),'vmstat_before':baseline,'vmstat_after':vmstat(),'cleanup':cleanup}
  save(run/'resource_summary.json',summary)
  state.update(finished_utc=utc(),seconds=round(time.monotonic()-start,3),exit_code=exitcode,resource=summary)
  save(run/'state.json',state)
 return reason
def main():
 BASE.mkdir(parents=True,exist_ok=True)
 with (BASE/'task.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  queue=json.loads((BASE/'queue.json').read_text());before=json.loads((BASE/'remote_before.json').read_text())
  oldstates=[json.loads(p.read_text()) for p in (BASE/'papers').glob('*/state.json')]
  stopreason=recovered_stop(oldstates);started=utc()
  save(BASE/'batch_state.json',{'status':'RUNNING','started_utc':started})
  for i,q in enumerate(queue):
   run=BASE/'papers'/q['paper_id'];p=run/'state.json'
   if p.exists():
    s=json.loads(p.read_text());good=verify_outputs(run,s)
    if checkpoint_action(s,good)=='SKIP':continue
    if s['status'] in ['EXTRACTION_COMPLETE','VALID_EMPTY','RUNNING']:
     stopreason='CHECKPOINT_UNVERIFIED_OR_UNCERTAIN'
     save(BASE/'checkpoint_block.json',{'paper_id':q['paper_id'],'status':s['status'],'reason':stopreason,'utc':utc()})
    # Failed or uncertain attempts never regenerate; preserve saved state.
    continue
   if q['status']!='PARSE_COMPLETE':
    save(p,{'status':'FAILED','upstream':'PARSE','error':q.get('error','Parse failed'),'reused':False,'record_count':None,'run_path':str(run)});continue
   if q['paper_id']=='1511.08308.pdf':
    run.mkdir(parents=True,exist_ok=True)
    assert sha(SINGLE/'raw_outputs/records.json')=='c7ae025fb281d86eb97d241aafc2b7257763dfad38248bf9fa54362ca8b5005b'
    for folder in ['raw_outputs','scilead_compatible_outputs']:shutil.copytree(SINGLE/folder,run/folder)
    s={'status':'EXTRACTION_COMPLETE','reused':True,'record_count':2,'seconds':0,'exit_code':0,'source_run':str(SINGLE),'run_path':str(run),'output_hashes':outputhashes(run)};save(p,s);continue
   if stopreason:
    save(p,{'status':'BLOCKED','error':stopreason,'reused':False,'record_count':None,'run_path':str(run)});continue
   if run.exists():
    save(p,{'status':'BLOCKED','error':'Orphan artifacts: require manual audit','reused':False,'run_path':str(run)});stopreason='ORPHAN_ATTEMPT';continue
   stopreason=run_one(q,i,before);write_tables(queue)
   print(json.dumps({'paper_id':q['paper_id'],'state':json.loads(p.read_text())['status'],'stop_reason':stopreason}),flush=True)
  write_tables(queue)
  save(BASE/'batch_state.json',{'status':'BLOCKED' if stopreason else 'FINISHED','started_utc':started,'finished_utc':utc(),'stop_reason':stopreason,'paid_api_calls':0})
if __name__=='__main__':main()
