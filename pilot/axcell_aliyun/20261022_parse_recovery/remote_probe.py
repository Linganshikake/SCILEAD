"""Read-only preflight: no credential contents in output."""
import datetime,hashlib,json,subprocess,shutil
from pathlib import Path
ROOT=Path('/root/scilead/axcell')
FORMAL=ROOT/'runs/20261022_formal'
def cmd(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=30);return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 info={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'data_exists':Path('/data').exists(),'root_exists':ROOT.exists(),'cpu':cmd(['nproc']),'memory':Path('/proc/meminfo').read_text(),'vmstat':{k:int(v) for k,v in (l.split() for l in Path('/proc/vmstat').read_text().splitlines()) if k in ['pswpin','pswpout','oom_kill']},'df':cmd(['df','-hT',str(ROOT)]),'mount':cmd(['findmnt','-T',str(ROOT)]),'disk':shutil.disk_usage(ROOT)._asdict(),'containers':cmd(['docker','ps','-a','--format','{{.Names}} {{.Status}} {{.Image}}']),'running_containers':cmd(['docker','ps','-q']),'tmux':cmd(['tmux','ls']),'images':cmd(['docker','image','inspect','arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6','--format','{{.Id}} {{json .RepoDigests}}']),'frozen_formal':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(FORMAL.rglob('*')) if p.is_file()},'existing_recovery_paths':[str(p) for p in [Path('/data/scilead/axcell_parse_recovery'),ROOT/'runs/20261022_parse_recovery'] if p.exists()]}
 if Path('/data').exists():info['data_mount']=cmd(['findmnt','-T','/data'])
 info['git']=cmd(['git','-C',str(ROOT/'source/axcell'),'rev-parse','HEAD'])
 info['git_status']=cmd(['git','-C',str(ROOT/'source/axcell'),'status','--porcelain'])
 info['failed_output_paths']={str(FORMAL/'stage2/parsed'/kind/version): (FORMAL/'stage2/parsed'/kind/version).exists() for version in ['1905.03197v3','2203.16804v1'] for kind in ['htmls','papers']}
 print(json.dumps(info))
if __name__=='__main__':main()
