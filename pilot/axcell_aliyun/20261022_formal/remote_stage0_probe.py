"""Read-only ECS stage-0 audit. Never starts containers, installs packages or loads models."""
import datetime,hashlib,json,os,shutil,socket,subprocess,time
from pathlib import Path
ROOT=Path('/root/scilead/axcell');OLD=ROOT/'runs/20261022_single_paper'
def command(args,timeout=30):
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
  return {'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except subprocess.TimeoutExpired:return {'error':'TIMEOUT','timeout_seconds':timeout}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def memory():
 keep=['MemTotal','MemAvailable','SwapTotal','SwapFree','CommitLimit','Committed_AS']
 return {k:int(v.split()[0])*1024 for k,v in (l.split(':',1) for l in Path('/proc/meminfo').read_text().splitlines()) if k in keep}
manifest=json.loads((ROOT/'manifests/transfer_manifest.json').read_text())
assets=[]
for e in manifest['files']+manifest['model_files']:
 p=ROOT/e['relative'];actual=sha(p) if p.is_file() else None
 assets.append({'path':e['relative'],'expected_sha256':e['sha256'],'actual_sha256':actual,'expected_bytes':e['bytes'],'actual_bytes':p.stat().st_size if p.is_file() else None,'match':actual==e['sha256']})
protected=[]
for e in json.loads((OLD/'task_artifact_hashes.json').read_text()):
 p=ROOT/e['path'];protected.append({'path':e['path'],'sha256_match':p.is_file() and sha(p)==e['sha256']})
original_run=[]
for e in json.loads((OLD/'delivery_hashes.json').read_text()):
 p=OLD/e['path'];original_run.append({'path':e['path'],'sha256_match':p.is_file() and sha(p)==e['sha256']})
images=[]
for name in ['arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6','docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1']:
 q=command(['docker','image','inspect',name])
 if q.get('exit_code')==0:
  d=json.loads(q['stdout'])[0];images.append({'reference':name,'id':d['Id'],'digests':d.get('RepoDigests',[]),'size':d['Size']})
 else:images.append({'reference':name,'present':False,'error':q})
containers=[]
q=command(['docker','ps','-aq','--filter','label=scilead.task=axcell-single-20261022'])
for cid in q.get('stdout','').split():
 d=json.loads(command(['docker','inspect',cid])['stdout'])[0]
 containers.append({'id':cid,'name':d['Name'],'state':d['State'],'memory_limit':d['HostConfig']['Memory'],'memory_swap_limit':d['HostConfig']['MemorySwap'],'nano_cpus':d['HostConfig']['NanoCpus'],'port_bindings':d['HostConfig']['PortBindings'],'image':d['Config']['Image']})
try:
 with socket.create_connection(('127.0.0.1',9200),timeout=2):es_port=True
except OSError:es_port=False
cg={}
for p in [Path('/sys/fs/cgroup/memory.max'),Path('/sys/fs/cgroup/memory.current'),Path('/sys/fs/cgroup/memory.swap.max'),Path('/sys/fs/cgroup/cpu.max')]:
 cg[str(p)]=p.read_text().strip() if p.is_file() else None
samples=[]
for i in range(3):
 samples.append({'utc_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memory':memory()})
 if i<2:time.sleep(2)
py=str(ROOT/'envs/axcell-original/bin/python')
package_check=command([py,'-c','import sys,json,pkg_resources; print(json.dumps({"python":sys.version,"prefix":sys.prefix,"packages":{d.project_name.lower():d.version for d in pkg_resources.working_set}}))'])
packages=json.loads(package_check['stdout']) if package_check.get('exit_code')==0 else package_check
previous={x['name'].lower():x['version'] for x in json.loads((OLD/'final_python_packages.json').read_text())}
actual=packages.get('packages',{})
diff={k:{'previous':v,'current':actual.get(k)} for k,v in previous.items() if actual.get(k)!=v}
result={'utc_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(ROOT),'os_release':Path('/etc/os-release').read_text(),'cpu_count':os.cpu_count(),'nproc':command(['nproc']),'cgroup':cg,'cgroup_membership':Path('/proc/self/cgroup').read_text(),'memory_samples':samples,'disk':command(['df','-B1','-T',str(ROOT)]),'inodes':command(['df','-i',str(ROOT)]),'disk_free_bytes':shutil.disk_usage(ROOT).free,'mount':command(['findmnt','-T',str(ROOT),'-o','TARGET,SOURCE,FSTYPE,OPTIONS']),'docker_active':command(['systemctl','is-active','docker']),'docker_version':command(['docker','version','--format','{{json .Server}}']),'images':images,'owned_containers':containers,'running_containers':command(['docker','ps','--format','{{.ID}} {{.Names}} {{.Status}}']),'elasticsearch_port_open':es_port,'elasticsearch_readiness':'STOPPED_NOT_PROBED_BY_START' if not es_port else 'PORT_OPEN_UNVERIFIED_APPLICATION','task_tmux':command(['tmux','list-sessions','-F','#{session_name}']),'top_rss':command(['ps','-eo','pid=,ppid=,comm=,rss=','--sort=-rss']),'pip_check':command([py,'-m','pip','check']),'packages':packages,'package_diff_from_single_paper':diff,'original_assets':assets,'original_assets_match':all(x['match'] for x in assets),'single_paper_script_and_parsed_checks':protected,'single_paper_script_and_parsed_match':all(x['sha256_match'] for x in protected),'single_paper_run_checks':original_run,'single_paper_run_unchanged':all(x['sha256_match'] for x in original_run),'source_files_on_server':[p.name for p in sorted((ROOT/'data/sources').iterdir()) if p.is_file()],'read_only':True,'containers_started':0,'model_loads':0,'api_calls':0}
print(json.dumps(result))
