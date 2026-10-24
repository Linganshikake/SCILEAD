"""Read-only ECS preflight; pinned artifacts and task history only."""
import datetime,hashlib,json,subprocess,shutil,socket
from pathlib import Path
ROOT=Path('/root/scilead/axcell');F=ROOT/'runs/20261022_formal';REC=ROOT/'runs/20261022_parse_recovery';S=ROOT/'runs/20261022_single_paper'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def cmd(a,timeout=60):
 p=subprocess.run(a,capture_output=True,text=True,timeout=timeout);return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def main():
 d={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cpu':cmd(['nproc']),'memory':Path('/proc/meminfo').read_text(),'vmstat':{k:int(v) for k,v in (l.split() for l in Path('/proc/vmstat').read_text().splitlines()) if k in ['oom_kill','pswpin','pswpout']},'disk':shutil.disk_usage(ROOT)._asdict(),'mount':cmd(['findmnt','-T',str(ROOT)]),'containers':cmd(['docker','ps','-a','--format','{{.Names}} {{.Status}} {{.Image}}']),'running_containers':cmd(['docker','ps','-q']),'tmux':cmd(['tmux','ls']),'systemd':cmd(['systemctl','--version']),'cgroup_version':Path('/proc/self/cgroup').read_text(),'active_units':cmd(['systemctl','list-units','--no-pager','--plain','--no-legend','axcell*']),'processes':cmd(['ps','-eo','pid,ppid,pgid,comm,rss,etimes']), 'existing_stage3':(ROOT/'runs/20261022_stage3_resume').exists()}
 sock=socket.socket()
 try:sock.bind(('127.0.0.1',9200));d['loopback_9200_free']=True
 except OSError:d['loopback_9200_free']=False
 finally:sock.close()
 manifest=json.loads((F/'stage2/parse_manifest.json').read_text());d['parse_counts']={};d['parsed_artifacts']=[]
 for row in manifest['papers']:
  d['parse_counts'][row['status']]=d['parse_counts'].get(row['status'],0)+1
  if row['status']=='PARSE_COMPLETE':
   result=json.loads((F/'stage2/parse_logs'/row['paper_id']/'parser_result.json').read_text())
   for x in result['artifacts']:
    p=Path(x['path']);d['parsed_artifacts'].append({'paper_id':row['paper_id'],'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'match':sha(p)==x['sha256'] and p.stat().st_size==x['bytes']})
 d['assets']=[]
 for x in json.loads((F/'stage2/configuration.json').read_text())['expected_assets']:
  p=ROOT/x['path'];d['assets'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'match':sha(p)==x['expected_sha256']})
 d['frozen_files']={str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for folder in [F,REC,S/'attempts/console_progress_compat',ROOT/'runs/20261022_stage3'] for p in sorted(folder.rglob('*')) if p.is_file()}
 d['single_records']=json.loads((S/'attempts/console_progress_compat/raw_outputs/records.json').read_text())
 d['single_result']=json.loads((S/'attempts/console_progress_compat/extraction_result.json').read_text())
 d['single_scripts']={str(p):sha(p) for p in (ROOT/'scripts').glob('*.py')}
 d['images']={image:cmd(['docker','image','inspect',image,'--format','{{.Id}} {{json .RepoDigests}}']) for image in ['arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6','docker.elastic.co/elasticsearch/elasticsearch-oss:6.7.1']}
 d['pip_check']=cmd([str(ROOT/'envs/axcell-original/bin/python'),'-m','pip','check'])
 d['pip_freeze']=cmd([str(ROOT/'envs/axcell-original/bin/python'),'-m','pip','freeze'])
 print(json.dumps(d))
if __name__=='__main__':main()
