"""Read-only integrity/resource audit of this task's allowlisted assets."""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
root=Path('/root/scilead/axcell');run=root/'runs/20261022_single_paper'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
manifest=json.loads((root/'manifests/transfer_manifest.json').read_text())
checks=[]
for entry in manifest['files']+manifest['model_files']:
 p=root/entry['relative']
 checks.append({'path':entry['relative'],'exists':p.exists(),'size_match':p.exists() and p.stat().st_size==entry['bytes'],'sha256_match':p.exists() and sha(p)==entry['sha256']})
images=[]
for name in ['arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6','docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1']:
 q=subprocess.run(['docker','image','inspect',name],capture_output=True,text=True)
 if q.returncode:images.append({'reference':name,'present':False});continue
 d=json.loads(q.stdout)[0];images.append({'reference':name,'present':True,'id':d['Id'],'repo_digests':d.get('RepoDigests',[]),'size_bytes':d.get('Size')})
containers=[]
ids=subprocess.check_output(['docker','ps','-aq','--filter','label=scilead.task=axcell-single-20261022'],text=True).split()
for cid in ids:
 d=json.loads(subprocess.check_output(['docker','inspect',cid],text=True))[0]
 containers.append({'id':cid,'name':d['Name'],'state':d['State'],'memory_limit':d['HostConfig']['Memory'],'cpu_quota':d['HostConfig']['NanoCpus'],'port_bindings':d['HostConfig']['PortBindings']})
mem={}
for line in Path('/proc/meminfo').read_text().splitlines():
 k,v=line.split(':',1)
 if k in ['MemTotal','MemAvailable','SwapTotal','SwapFree']:mem[k]=int(v.strip().split()[0])*1024
audit={'utc_time':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':checks,'all_original_asset_hashes_match':all(c['size_match'] and c['sha256_match'] for c in checks),'images':images,'containers':containers,'memory':mem,'disk_free_bytes':shutil.disk_usage(root).free,'cpu':os.cpu_count(),'paid_api_calls':0,'paper_count_allowed':1,'author_36_subset_membership':'UNVERIFIED'}
(run/'verification.json').write_text(json.dumps(audit,indent=2))
print(json.dumps({k:v for k,v in audit.items() if k!='checks'}))
