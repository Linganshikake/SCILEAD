"""One authorized timeout-only diagnostic, never a batch or retry loop."""
import ast,datetime,fcntl,json,os,shutil,subprocess,time
from pathlib import Path
from policy import sha,start_guard
R=Path(__file__).resolve().parent
FORMAL=Path('/root/scilead/axcell/runs/20261022_formal/stage2')
def save(name,d):(R/name).write_text(json.dumps(d,indent=2))
def main():
 with (R/'task.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  assert not (R/'attempt_started.json').exists(),'Already attempted: never repeat'
  assert R==Path('/root/scilead/axcell/runs/20261022_parse_recovery/attempt_2203_timeout600')
  available=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))*1024
  assert not start_guard(available,shutil.disk_usage(R).free)
  assert not subprocess.check_output(['docker','ps','-q'],text=True).strip(),'Do not start with unrelated live containers'
  assert subprocess.check_output(['docker','image','inspect','arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6','--format','{{.Id}}'],text=True).strip()=='sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e'
  original=Path('/root/scilead/axcell/source/axcell/axcell/scripts');own=R/'converter_scripts'
  for p in original.rglob('*'):
   if not p.is_file():continue
   b=p.read_bytes();a=(own/p.relative_to(original)).read_bytes()
   assert a==(b.replace(b'timeout -s KILL 300 engrafo',b'timeout -s KILL 600 engrafo') if p.name=='latex2html.sh' else b)
  for p in R.glob('*.py'):ast.parse(p.read_text())
  row=json.loads((R/'queue.json').read_text())[0];assert row['paper_id']=='2203.16804.pdf'
  frozen=Path(row['frozen_remote_source']);assert sha(frozen)==row['sha256']
  dest=Path(row['remote_source']);dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copy2(frozen,dest);assert sha(dest)==row['sha256']
  log=R/'parse_logs'/row['paper_id'];log.mkdir(parents=True)
  save('prelaunch.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ram_available_bytes':available,'disk_free_bytes':shutil.disk_usage(R).free,'script_difference':'timeout 300 -> 600 only','source_sha256':sha(dest),'scripts':{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and p.suffix in ['.py','.sh','.patch']},'model_loads':0,'api_calls':0})
  cmd=['python3',str(R/'monitor.py'),'--run',str(log),'--stage','conversion','--timeout','660','--','/root/scilead/axcell/envs/axcell-original/bin/python',str(R/'parse_one.py'),row['paper_id']]
  save('attempt_started.json',{'paper_id':row['paper_id'],'attempt':1,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd})
  start=time.monotonic()
  with (log/'process.log').open('w') as f:
   p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='6',MKL_NUM_THREADS='6'))
  save('attempt_finished.json',{'exit_code':p.returncode,'seconds':time.monotonic()-start,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_extractions':0,'api_calls':0})
  print(json.dumps({'finished':True,'exit_code':p.returncode}),flush=True)
if __name__=='__main__':main()
