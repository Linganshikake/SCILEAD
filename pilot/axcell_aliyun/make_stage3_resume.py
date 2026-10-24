from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;old=P/'20261022_stage3';new=P/'20261022_stage3_resume'
assert not new.exists(),'Keep existing resume attempt intact'
new.mkdir()
names=['client.py','preflight.py','controller.py','worker.py','policy.py','test_policy.py','test_cleanup.py','service_test.py','deploy.py','launch.py','status.py','final_audit.py','sync_results.py','inspect_outputs.py','queue.json']
for name in names:
 s=(old/name).read_text(encoding='utf-8')
 s=s.replace('20261022_stage3','20261022_stage3_resume').replace('axcell-stage3-20261022','axcell-stage3-resume-20261022')
 if name=='preflight.py':s=s.replace("[F,REC,S/'attempts/console_progress_compat']","[F,REC,S/'attempts/console_progress_compat',ROOT/'runs/20261022_stage3']")
 if name=='controller.py':
  s=s.replace("'--property=RuntimeMaxSec=1850s'","'--property=RuntimeMaxSec=3650s'")
  start=s.index('   if not reason and len(samples)>45:');end=s.index('   if reason:raise RuntimeError(reason)',start)
  s=s[:start]+"   # Sparse phase events are not evidence of a stall. CPU/memory are recorded, absolute limits remain.\n"+s[end:]
  start=s.index("   if q['paper_id']=='1511.08308.pdf':");end=s.index('   if stopreason:',start)
  s=s[:start]+'''   if q['paper_id'] in ['1911.10390.pdf','2001.04063.pdf','1511.08308.pdf']:
    prior=ROOT/'runs/20261022_stage3/papers'/q['paper_id'];oldstate=json.loads((prior/'state.json').read_text())
    assert oldstate['status']=='EXTRACTION_COMPLETE' and verify_outputs(prior,oldstate),'Reused result failed verification'
    run.mkdir(parents=True,exist_ok=True)
    for folder in ['raw_outputs','scilead_compatible_outputs']:shutil.copytree(prior/folder,run/folder)
    s={'status':'EXTRACTION_COMPLETE','reused':True,'record_count':oldstate['record_count'],'seconds':0,'exit_code':0,'source_run':str(prior),'run_path':str(run),'output_hashes':outputhashes(run)}
    assert s['output_hashes']==oldstate['output_hashes'];save(p,s);continue
'''+s[end:]
  s=s.replace("'peak':None,'events':{}","'peak':None,'events':{},'cpu_usage_usec':0")
  s=s.replace(" if (p/'memory.events').exists():", " if (p/'cpu.stat').exists():r['cpu_usage_usec']=dict((k,int(v)) for k,v in (x.split() for x in (p/'cpu.stat').read_text().splitlines())).get('usage_usec',0)\n if (p/'memory.events').exists():")
  s=s.replace("'worker':w['memory'],'worker_rss'", "'worker':w['memory'],'worker_cpu_usage_usec':w['cpu_usage_usec'],'worker_rss'")
  s=s.replace("  try:sample['resources']=snapshot(unit,name)\n  except Exception as e:sample['monitor_error']=type(e).__name__",'''  try:
   w=cgread('/system.slice/'+unit);e={'memory':0};ip=run/'es_initial_inspect.json'
   if ip.exists():
    initial=json.loads(ip.read_text());pid=initial['State']['Pid'];pf=Path('/proc',str(pid),'cgroup')
    if pf.exists():
     group=pf.read_text().strip().split('::',1)[1]
     if initial['Id'] in group:e=cgread(group)
   sample['resources']={'worker':w['memory'],'es':e['memory']}
   reason=resource_stop(sample['available'],shutil.disk_usage(BASE).free,w['memory'],e['memory'],sample['vmstat']['oom_kill'],json.loads((BASE/'remote_before.json').read_text())['vmstat']['oom_kill'],0)
   if reason:save(run/'cleanup_resource_stop.json',{'reason':reason,'sample':sample})
  except Exception as e:sample['monitor_error']=type(e).__name__''')
  s=s.replace(" result['clean']=not result['es_running']", " if (run/'cleanup_resource_stop.json').exists():result['resource_stop']=json.loads((run/'cleanup_resource_stop.json').read_text())['reason']\n result['clean']=not result['es_running']")
  s=s.replace("  if cleanup and (not cleanup['clean'] or cleanup['new_oom']):", "  if cleanup and cleanup.get('resource_stop'):reason=reason or cleanup['resource_stop']\n  if cleanup and (not cleanup['clean'] or cleanup['new_oom']):")
 if name=='policy.py':s=s.replace('elapsed>1800','elapsed>3600').replace('WALL_TIME_1800S_LIMIT','WALL_TIME_3600S_LIMIT')
 if name=='test_policy.py':s=s.replace("('elapsed',1801)","('elapsed',3601)")
 if name=='launch.py':s=s.replace("'axcell-stage3'","'axcell-stage3-resume'").replace("'started_tmux':'axcell-stage3'","'started_tmux':'axcell-stage3-resume'")
 (new/name).write_text(s,encoding='utf-8')
print(str(new))
