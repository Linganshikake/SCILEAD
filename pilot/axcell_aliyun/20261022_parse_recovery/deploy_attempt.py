import json,shlex,sys
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));import client
REMOTE='/root/scilead/axcell/runs/20261022_parse_recovery/attempt_2203_timeout600'
def mkdirs(s,path):
 try:s.stat(path);return
 except FileNotFoundError:pass
 mkdirs(s,str(Path(path).parent).replace('\\','/'));s.mkdir(path)
def main():
 t=client.remote.connect()
 try:
  s=client.paramiko.SFTPClient.from_transport(t)
  try:s.stat(REMOTE);raise RuntimeError('Attempt already exists; inspect, do not relaunch')
  except FileNotFoundError:pass
  mkdirs(s,REMOTE)
  files={str(p.relative_to(R/'attempt_2203_timeout600')).replace('\\','/'):p for p in (R/'attempt_2203_timeout600').rglob('*') if p.is_file()}
  files.update({n:R/n for n in ['observe.py','driver.py']})
  for rel,p in files.items():
   dest=REMOTE+'/'+rel;mkdirs(s,dest.rsplit('/',1)[0]);s.put(str(p),dest)
   if p.suffix=='.sh':s.chmod(dest,0o755)
  command='cd '+shlex.quote(REMOTE)+' && PYTHONDONTWRITEBYTECODE=1 python3 driver.py > driver.log 2>&1'
  code,out,err=client.execute(t,'tmux new-session -d -s axcell-recovery-2203-600 '+shlex.quote(command),timeout=20)
  (R/'launch.json').write_text(json.dumps({'exit_code':code,'stdout':out.decode(),'stderr':err.decode(),'session':'axcell-recovery-2203-600','remote':REMOTE},indent=2))
  print(json.dumps({'launch_exit':code,'uploaded_files':len(files),'remote':REMOTE}))
 finally:t.close()
if __name__=='__main__':main()
