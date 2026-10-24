"""Linux owner/monitor for one setup process group; no global process termination."""
import argparse,datetime,json,os,resource,signal,subprocess,time
from pathlib import Path

TASK_LABEL='scilead.task=axcell-single-20261022'
CONTAINER_STAGES={'conversion','extraction','elasticsearch_start','elasticsearch_restart_console_fix','extraction_console_fix'}
SERVICE_START_STAGES={'elasticsearch_start','elasticsearch_restart_console_fix'}

def group_members(pgid):
    q=subprocess.run(['ps','-eo','pid=,ppid=,pgid=,rss=,stat=,comm='],capture_output=True,text=True,timeout=5)
    return [{'pid':int(r[0]),'ppid':int(r[1]),'rss_bytes':int(r[3])*1024,'name':r[5]}
            for r in (line.split(None,5) for line in q.stdout.splitlines())
            if len(r)==6 and int(r[2])==pgid and not r[4].startswith('Z')]

def cleanup_group(p,grace=30):
    if not group_members(p.pid):
        p.poll();return {'remaining_live_members':[]}
    try:os.killpg(p.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    start=time.monotonic()
    while group_members(p.pid) and time.monotonic()-start<grace:
        p.poll();time.sleep(.25)
    forced=bool(group_members(p.pid))
    if forced:
        try:os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:pass
    time.sleep(.1)
    return {'forced_kill':forced,'remaining_live_members':group_members(p.pid)}

def cleanup_containers():
    ids=subprocess.run(['docker','ps','-q','--filter','label='+TASK_LABEL],capture_output=True,text=True,timeout=10).stdout.split()
    events=[]
    for cid in ids:
        try:
            d=json.loads(subprocess.check_output(['docker','inspect',cid],text=True,timeout=10))[0]
            assert d['Config']['Labels'].get('scilead.task')=='axcell-single-20261022'
            q=subprocess.run(['docker','stop','--time','30',cid],capture_output=True,text=True,timeout=45)
            events.append({'id':cid,'stop_exit_code':q.returncode})
        except (subprocess.TimeoutExpired,subprocess.CalledProcessError) as e:events.append({'id':cid,'stop_error':type(e).__name__})
    remaining=subprocess.run(['docker','ps','-q','--filter','label='+TASK_LABEL],capture_output=True,text=True,timeout=10).stdout.split()
    return {'events':events,'remaining_running_task_containers':remaining}
def container_samples():
    rows=[]
    try:
        ids=subprocess.run(['docker','ps','--filter','label='+TASK_LABEL,'--format','{{.ID}}'],capture_output=True,text=True,timeout=5).stdout.split()
        for cid in ids:
            q=subprocess.run(['docker','inspect',cid],capture_output=True,text=True,timeout=5)
            if q.returncode:continue
            d=json.loads(q.stdout)[0];pid=d['State']['Pid']
            row={'id':cid,'name':d['Name'],'pid':pid,'limit_bytes':d['HostConfig']['Memory'],'oom_killed':d['State']['OOMKilled']}
            cgfile=Path('/proc')/str(pid)/'cgroup'
            if cgfile.exists():
                unified=next((s.split('::',1)[1] for s in cgfile.read_text().splitlines() if s.startswith('0::')),None)
                if unified is not None:
                    base=Path('/sys/fs/cgroup')/unified.lstrip('/')
                    for key in ['memory.current','memory.peak','memory.swap.current','memory.max']:
                        p=base/key
                        if p.exists():
                            v=p.read_text().strip();row[key]=int(v) if v.isdigit() else v
                    p=base/'memory.events'
                    if p.exists():row['events']={k:int(v) for k,v in (s.split() for s in p.read_text().splitlines())}
            rows.append(row)
    except (subprocess.TimeoutExpired,FileNotFoundError):pass
    return rows
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--timeout',type=int,default=600);ap.add_argument('cmd',nargs=argparse.REMAINDER);a=ap.parse_args()
    cmd=a.cmd[1:] if a.cmd[0]=='--' else a.cmd
    run=Path('/root/scilead/axcell/runs/20261022_single_paper');run.mkdir(exist_ok=True)
    stop=run/(a.stage+'.stop');assert not stop.exists()
    assert not (run/(a.stage+'_linux_owner.json')).exists(),'Never overwrite an existing stage attempt'
    p=subprocess.Popen(cmd,start_new_session=True);start=time.monotonic();reason=None;low_since=None;peak_sum=0;samples=[]
    (run/(a.stage+'_linux_owner.json')).write_text(json.dumps({'pid':p.pid,'pgid':p.pid,'command':cmd,'start':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
    initial_oom=None;container_high_since={};signals=[];cleanup={}
    for sig in [signal.SIGTERM,signal.SIGINT]:signal.signal(sig,lambda num,frame:signals.append(num))
    try:
      while True:
        tick=time.monotonic();mem={}
        for line in Path('/proc/meminfo').read_text().splitlines():
            k,v=line.split(':',1)
            if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']:mem[k]=int(v.strip().split()[0])*1024
        owned=group_members(p.pid)
        peak_sum=max(peak_sum,sum(x['rss_bytes'] for x in owned))
        vm={k:int(v) for k,v in (line.split() for line in Path('/proc/vmstat').read_text().splitlines()) if k in ['oom_kill','pswpin','pswpout']}
        if initial_oom is None:initial_oom=vm['oom_kill']
        containers=container_samples() if a.stage in CONTAINER_STAGES else []
        s={'elapsed_seconds':tick-start,'memory':mem,'vmstat':vm,'owned_processes':owned,'owned_rss_sum':sum(x['rss_bytes'] for x in owned),'containers':containers}
        with (run/(a.stage+'_linux_resources.jsonl')).open('a') as f:f.write(json.dumps(s)+'\n')
        samples.append(s)
        if mem['MemAvailable']<2*2**30:
            if low_since is None:low_since=tick
            elif tick-low_since>=15:reason='ECS_LOW_MEMORY'
        else:low_since=None
        if vm['oom_kill']>initial_oom:reason='ECS_OOM_OBSERVED'
        if any(x['oom_killed'] or x.get('events',{}).get('oom_kill',0)>0 for x in containers):reason='TASK_CONTAINER_OOM'
        for c in containers:
            if c['limit_bytes'] and c.get('memory.current',0)>=.95*c['limit_bytes']:
                container_high_since.setdefault(c['id'],tick)
                if tick-container_high_since[c['id']]>=15:reason='TASK_CONTAINER_NEAR_MEMORY_LIMIT'
            else:container_high_since.pop(c['id'],None)
        if stop.exists():reason='TASK_STOP_REQUEST'
        if signals:reason='MONITOR_SIGNAL_'+str(signals[0])
        if tick-start>a.timeout:reason='OWNED_STAGE_TIMEOUT'
        if reason or p.poll() is not None:break
        time.sleep(3)
    except Exception as e:
        reason='MONITOR_EXCEPTION_'+type(e).__name__
    finally:
        # ES is deliberately retained only after a successful ES-start stage.
        if a.stage in CONTAINER_STAGES and not (a.stage in SERVICE_START_STAGES and not reason and p.poll()==0):
            try:cleanup['containers']=cleanup_containers()
            except Exception as e:cleanup['containers']={'cleanup_error':type(e).__name__}
        try:cleanup['process_group']=cleanup_group(p)
        except Exception as e:cleanup['process_group']={'cleanup_error':type(e).__name__}
        if any(v.get('cleanup_error') or v.get('remaining_live_members') or v.get('remaining_running_task_containers') for v in cleanup.values()):
            reason=reason or 'TASK_CLEANUP_INCOMPLETE'
        (run/(a.stage+'_cleanup.json')).write_text(json.dumps(cleanup,indent=2))
    ru=resource.getrusage(resource.RUSAGE_CHILDREN)
    result={'stage':a.stage,'exit_code':p.returncode,'stop_reason':reason,'seconds':round(time.monotonic()-start,2),'peak_sampled_owned_process_group_rss_bytes':peak_sum,'rusage_maxrss_bytes':ru.ru_maxrss*1024,'rusage_note':'max child RSS, not simultaneous tree sum','min_ecs_available_bytes':min((x['memory']['MemAvailable'] for x in samples),default=None),'swap_growth_bytes':(samples[0]['memory']['SwapFree']-samples[-1]['memory']['SwapFree']) if samples else None,'cleanup':cleanup}
    result['containers']={}
    for s in samples:
        for c in s.get('containers',[]):
            old=result['containers'].setdefault(c['name'],{'limit_bytes':c['limit_bytes'],'peak_sampled_memory_bytes':0,'peak_cgroup_memory_bytes':None,'peak_swap_bytes':0})
            old['peak_sampled_memory_bytes']=max(old['peak_sampled_memory_bytes'],c.get('memory.current',0))
            if 'memory.peak' in c:old['peak_cgroup_memory_bytes']=max(old['peak_cgroup_memory_bytes'] or 0,c['memory.peak'])
            old['peak_swap_bytes']=max(old['peak_swap_bytes'],c.get('memory.swap.current',0))
    (run/(a.stage+'_linux_status.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
    raise SystemExit(p.returncode if not reason else 125)
if __name__=='__main__':main()
