"""Bounded stage1 artifact read and isolated Elasticsearch measurement. No inference."""
import datetime, fcntl, hashlib, json, os, shutil, signal, socket, subprocess, time, urllib.request
from pathlib import Path

ROOT=Path('/root/scilead/axcell'); OUT=ROOT/'runs/20261022_formal/stage1'
PY=ROOT/'envs/axcell-original/bin/python'
NAME='axcell-formal-p1-es'; LABEL='axcell-formal-p1-20261022'
IMAGE='docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1'
IMAGE_ID='sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b'
GIB=2**30; began=time.monotonic(); samples=[]; phases=[]; low_since=None; high_since=None
child=None; created=False; stopped=False; stop_request=None; phase='preflight'; result={}

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(name,obj):
    dest=OUT/name; tmp=dest.with_suffix(dest.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)); tmp.replace(dest)
def cmd(args,timeout=30):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if p.returncode: raise RuntimeError('Command failed: '+args[0]+' '+str(p.returncode)+' '+p.stderr[:500])
    return p.stdout
def memory():
    return {k:int(v.split()[0])*1024 for k,v in (l.split(':',1) for l in Path('/proc/meminfo').read_text().splitlines())}
def vmstat():
    d=dict(l.split() for l in Path('/proc/vmstat').read_text().splitlines())
    return {k:int(d[k]) for k in ['pswpin','pswpout','oom_kill','pgmajfault']}
def tree_rss(root_pid):
    if not root_pid:return 0
    rows={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            fields=p.joinpath('stat').read_text().rsplit(')',1)[1].split()
            rows[int(p.name)]=(int(fields[1]),int(fields[21])*os.sysconf('SC_PAGE_SIZE'))
        except (OSError,ValueError,IndexError): pass
    ids={root_pid}
    for _ in range(30):
        new={pid for pid,(ppid,_) in rows.items() if ppid in ids}-ids
        if not new: break
        ids|=new
    return sum(rows.get(pid,(0,0))[1] for pid in ids)
def container_sample():
    if not created:return {}
    d=json.loads(cmd(['docker','inspect',NAME]))[0]
    pid=d['State']['Pid']; out={'running':d['State']['Running'],'oom_killed':d['State']['OOMKilled'],'limit_bytes':d['HostConfig']['Memory'],'process_tree_rss_bytes':tree_rss(pid)}
    if pid:
        cg=Path('/proc/{}/cgroup'.format(pid)).read_text().split('0::',1)[1].strip()
        cgroot=Path('/sys/fs/cgroup')/cg.lstrip('/')
        for n in ['memory.current','memory.peak','memory.swap.current']:
            p=cgroot/n
            if p.is_file():out[n]=int(p.read_text().strip())
        p=cgroot/'memory.events'
        if p.is_file():out['memory.events']={k:int(v) for k,v in (l.split() for l in p.read_text().splitlines())}
    return out
def sample(enforce=True):
    global low_since,high_since
    now=time.monotonic(); m=memory(); v=vmstat(); c=container_sample()
    d={'utc':utc(),'elapsed_seconds':now-began,'phase':phase,'mem_available_bytes':m['MemAvailable'],
       'committed_as_bytes':m['Committed_AS'],'swap_used_bytes':m['SwapTotal']-m['SwapFree'],
       'disk_free_bytes':shutil.disk_usage(ROOT).free,'vmstat':v,
       'controller_tree_rss_bytes':tree_rss(os.getpid()),'child_tree_rss_bytes':tree_rss(child.pid if child and child.poll() is None else None),
       'container':c}
    samples.append(d)
    with (OUT/'resource_samples.jsonl').open('a') as f:f.write(json.dumps(d)+'\n')
    if not enforce:return d
    low_since=(low_since or now) if m['MemAvailable']<2*GIB else None
    high=c.get('memory.current',0)>=.95*c.get('limit_bytes',3*GIB)
    high_since=(high_since or now) if high else None
    if stop_request:raise RuntimeError(stop_request)
    if d['disk_free_bytes']<20*GIB:raise RuntimeError('Disk reserve below 20 GiB')
    if low_since and now-low_since>=15:raise RuntimeError('MemAvailable below 2 GiB for 15 seconds')
    if high_since and now-high_since>=15:raise RuntimeError('Container above 95 percent for 15 seconds')
    if c.get('oom_killed') or c.get('memory.events',{}).get('oom_kill',0)>0 or v['oom_kill']>initial_oom:raise RuntimeError('OOM observed')
    return d
def phase_done(name,start,exit_code=0):phases.append({'phase':name,'seconds':time.monotonic()-start,'exit_code':exit_code})
def signal_handler(signum,frame):
    global stop_request
    stop_request='Signal '+str(signum)
signal.signal(signal.SIGTERM,signal_handler); signal.signal(signal.SIGINT,signal_handler)
lock=(OUT/'task.lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
assert not (OUT/'attempt_started.json').exists(), 'Existing attempt must be reviewed, never restarted automatically'
write('attempt_started.json',{'utc':utc(),'pid':os.getpid(),'stage':1,'no_inference':True})
initial_oom=vmstat()['oom_kill']
try:
    first=sample()
    assert first['mem_available_bytes']>=6*GIB, 'Start guard: less than 6 GiB available'
    assert not cmd(['docker','ps','-q']).strip(), 'Unexpected running containers; review first'
    assert not cmd(['docker','ps','-aq','--filter','name=^/'+NAME+'$']).strip(), 'Existing P1 container'
    image=json.loads(cmd(['docker','image','inspect',IMAGE]))[0]; assert image['Id']==IMAGE_ID
    s=socket.socket(); s.bind(('127.0.0.1',9200)); s.close()
    phase='saved_artifact_read'; start=time.monotonic()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='6',MKL_NUM_THREADS='6')
    with (OUT/'artifact_read.log').open('w') as log:
        child=subprocess.Popen([str(PY),str(OUT/'verify_saved_artifacts.py')],stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
        while child.poll() is None:
            sample()
            if time.monotonic()-start>120:raise RuntimeError('Artifact read timeout')
            time.sleep(2)
        phase_done(phase,start,child.returncode)
        assert child.returncode==0, 'Saved artifact validation failed; see artifact_read.log'
    phase='service_startup'; start=time.monotonic()
    data=OUT/'elasticsearch_data'; data.mkdir(); os.chown(str(data),1000,0)
    args=['docker','run','-d','--pull','never','--name',NAME,'--label','scilead.task='+LABEL,
          '--memory','3g','--memory-swap','3g','--cpus','2','--publish','127.0.0.1:9200:9200',
          '--mount','type=bind,source='+str(data)+',target=/usr/share/elasticsearch/data',
          '--env','ES_JAVA_OPTS=-Xms1g -Xmx1g','--log-opt','max-size=20m','--log-opt','max-file=3',
          '--user','elasticsearch','--entrypoint','elasticsearch',IMAGE,
          '-Ehttp.port=9200','-Etransport.host=localhost','-Ehttp.host=0.0.0.0',
          '-Ebootstrap.system_call_filter=false','-Ehttp.cors.enabled=true','-Ehttp.cors.allow-origin=*',
          '-Ehttp.cors.allow-headers=*','-Ehttp.cors.allow-credentials=true']
    write('service_launch_config.json',{'argv':args,'image_id':IMAGE_ID,'isolated_data':str(data),'old_data_not_mounted':True})
    # Claim ownership before run so failure after container creation is still cleaned up.
    created=True
    cid=cmd(args).strip(); write('container_id.json',{'id':cid,'name':NAME})
    while time.monotonic()-start<90:
        sample()
        try:
            with urllib.request.urlopen('http://127.0.0.1:9200',timeout=2) as f:version=json.load(f)
            assert version['version']['number']=='6.7.1'
            write('elasticsearch_version.json',version); break
        except OSError:time.sleep(2)
    else:raise RuntimeError('Elasticsearch not ready after 90 seconds')
    phase_done(phase,start)
    phase='service_ready'; start=time.monotonic()
    with urllib.request.urlopen('http://127.0.0.1:9200/_cluster/health',timeout=5) as f:health=json.load(f)
    with urllib.request.urlopen('http://127.0.0.1:9200/_cat/indices?format=json',timeout=5) as f:indices=json.load(f)
    assert health['status']=='green' and indices==[], 'Unexpected index state in isolated test'
    write('elasticsearch_health.json',{'health':health,'indices':indices,'no_inference_or_indexing':True})
    for _ in range(5):sample(); time.sleep(3)
    phase_done(phase,start)
    result={'status':'PASSED','no_conversion':True,'model_generations':0,'paid_api_calls':0}
except Exception as e:
    result={'status':'FAILED','error_type':type(e).__name__,'message':str(e),'failed_phase':phase,'model_generations':0,'paid_api_calls':0}
finally:
    if child and child.poll() is None:
        os.killpg(child.pid,signal.SIGTERM)
        try:child.wait(timeout=15)
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=10)
    phase='service_shutdown'; start=time.monotonic()
    try:
        if created:
            q=subprocess.run(['docker','inspect',NAME],capture_output=True,text=True,timeout=15)
            if q.returncode==0:
                before=json.loads(q.stdout)[0]
                assert before['Config']['Labels'].get('scilead.task')==LABEL
                write('container_before_stop.json',before)
                sample(enforce=False)
                cmd(['docker','stop','-t','30',NAME],timeout=45)
                after=json.loads(cmd(['docker','inspect',NAME]))[0];write('container_after_stop.json',after)
                (OUT/'elasticsearch.log').write_text(cmd(['docker','logs',NAME]))
                stopped=not after['State']['Running'];assert stopped and not after['State']['OOMKilled']
        phase_done(phase,start)
    except Exception as e:
        result.update(status='FAILED',cleanup_error=str(e))
    phase='after_stop'; sample(enforce=False)
    result.update(utc_completed=utc(),elapsed_seconds=time.monotonic()-began,phases=phases,
                  container_started=created,container_stopped=stopped,sample_count=len(samples),
                  disk_free_after_bytes=shutil.disk_usage(ROOT).free,
                  es_data_du_bytes=int(cmd(['du','-sb',str(OUT/'elasticsearch_data')]).split()[0]) if (OUT/'elasticsearch_data').exists() else 0,
                  remaining_running_containers=cmd(['docker','ps','--format','{{.ID}} {{.Names}}']).splitlines())
    write('runtime_result.json',result)
    print(json.dumps(result),flush=True)
if result['status']!='PASSED':raise SystemExit(1)
