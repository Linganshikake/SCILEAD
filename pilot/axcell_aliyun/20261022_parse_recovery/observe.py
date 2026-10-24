"""Read-only snapshots of only this task's container. No parser instrumentation."""
import hashlib,json,os,time
from pathlib import Path
OUT=Path('/root/scilead/axcell/runs/20261022_parse_recovery/attempt_2203_timeout600/parse_logs/2203.16804.pdf/observations')
def extra_snapshot(pid,inspect):
 d={'processes':[],'partial_outputs':[]};root=Path('/proc')/str(pid)/'root'
 try:
  cg=(Path('/proc')/str(pid)/'cgroup').read_text()
  unified=next((s.split('::',1)[1] for s in cg.splitlines() if s.startswith('0::')),None)
  base=Path('/sys/fs/cgroup')/unified.lstrip('/')
  if (base/'cpu.stat').exists():d['cpu_stat']={k:int(v) for k,v in (s.split() for s in (base/'cpu.stat').read_text().splitlines())}
  pids=[int(x) for x in (base/'cgroup.procs').read_text().split()]
  for p in pids:
   proc=Path('/proc')/str(p)
   try:
    stat=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()
    row={'pid':p,'name':proc.joinpath('comm').read_text().strip(),'state':stat[0],'user_ticks':int(stat[11]),'system_ticks':int(stat[12]),'rss_bytes':int(stat[21])*os.sysconf('SC_PAGE_SIZE'),'wchan':proc.joinpath('wchan').read_text().strip(),'files':[]}
    for fd in proc.joinpath('fd').iterdir():
     try:
      dest=os.readlink(fd)
      if dest.startswith(('/files/','/usr/share/texlive/','/usr/local/share/perl/')):
       row['files'].append({'target':dest,'fdinfo':proc.joinpath('fdinfo',fd.name).read_text()})
     except (OSError,FileNotFoundError):pass
    d['processes'].append(row)
   except (OSError,FileNotFoundError):pass
  partial=root/'files/output'
  if partial.exists():
   OUT.mkdir(parents=True,exist_ok=True)
   for p in partial.rglob('*'):
    if not p.is_file():continue
    n=p.stat().st_size;rel=str(p.relative_to(partial));d['partial_outputs'].append({'path':rel,'bytes':n})
    if p.suffix in ['.html','.xml','.log'] and n<=10*1024*1024:
     target=OUT/'partial'/rel;target.parent.mkdir(parents=True,exist_ok=True)
     b=p.read_bytes();target.write_bytes(b)
  log=Path(inspect.get('LogPath',''))
  if log.is_file():
   d['docker_log_bytes']=log.stat().st_size
   OUT.mkdir(parents=True,exist_ok=True)
   if log.stat().st_size<4*1024*1024:(OUT/'docker_json.log').write_bytes(log.read_bytes())
 except (OSError,StopIteration,ValueError) as e:d['observation_error']=type(e).__name__
 return d
