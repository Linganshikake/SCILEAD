"""Linux owner/monitor for one setup process group; no global process termination."""
import argparse,datetime,json,os,resource,signal,subprocess,time
from pathlib import Path

TASK_LABEL='scilead.task=axcell-single-20261022'
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
    p=subprocess.Popen(cmd,start_new_session=True);start=time.monotonic();reason=None;low_since=None;peak_sum=0;samples=[]
    (run/(a.stage+'_linux_owner.json')).write_text(json.dumps({'pid':p.pid,'pgid':p.pid,'command':cmd,'start':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
    initial_oom=None;container_high_since={}
    while True:
        tick=time.monotonic();mem={}
        for line in Path('/proc/meminfo').read_text().splitlines():
            k,v=line.split(':',1)
            if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']:mem[k]=int(v.strip().split()[0])*1024
        ps=subprocess.run(['ps','-eo','pid=,ppid=,pgid=,rss=,comm='],capture_output=True,text=True)
        owned=[]
        for line in ps.stdout.splitlines():
            row=line.split(None,4)
            if len(row)==5 and int(row[2])==p.pid:owned.append({'pid':int(row[0]),'ppid':int(row[1]),'rss_bytes':int(row[3])*1024,'name':row[4]})
        peak_sum=max(peak_sum,sum(x['rss_bytes'] for x in owned))
        vm={k:int(v) for k,v in (line.split() for line in Path('/proc/vmstat').read_text().splitlines()) if k in ['oom_kill','pswpin','pswpout']}
        if initial_oom is None:initial_oom=vm['oom_kill']
        containers=container_samples() if a.stage in ['conversion','extraction','elasticsearch_start'] else []
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
        if tick-start>a.timeout:reason='OWNED_STAGE_TIMEOUT'
        if reason and p.poll() is None:
            if containers:
                try:subprocess.run(['docker','stop','--time','30']+[x['id'] for x in containers],capture_output=True,timeout=45)
                except subprocess.TimeoutExpired:
                    with (run/(a.stage+'_cleanup_events.jsonl')).open('a') as f:f.write(json.dumps({'container_stop':'TIMEOUT','container_ids':[x['id'] for x in containers]})+'\n')
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:p.wait(timeout=30)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
        if p.poll() is not None:break
        time.sleep(3)
    ru=resource.getrusage(resource.RUSAGE_CHILDREN)
    result={'stage':a.stage,'exit_code':p.returncode,'stop_reason':reason,'seconds':round(time.monotonic()-start,2),'peak_sampled_owned_process_group_rss_bytes':peak_sum,'rusage_maxrss_bytes':ru.ru_maxrss*1024,'rusage_note':'max child RSS, not simultaneous tree sum','min_ecs_available_bytes':min(x['memory']['MemAvailable'] for x in samples),'swap_growth_bytes':(samples[0]['memory']['SwapFree']-samples[-1]['memory']['SwapFree'])}
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
