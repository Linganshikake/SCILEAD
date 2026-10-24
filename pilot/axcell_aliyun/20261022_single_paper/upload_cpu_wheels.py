from pathlib import Path
import hashlib,json,time,shlex,sys
LOCAL=Path(__file__).resolve().parent
import remote,paramiko
selection=sys.argv[1] if len(sys.argv)>1 else 'cpu'
assert selection in ['cpu','pypi']
manifest_name='cpu_wheel_artifacts.json' if selection=='cpu' else 'pypi_package_artifacts.json'
rows=json.loads((LOCAL/manifest_name).read_text())
t=remote.connect();s=paramiko.SFTPClient.from_transport(t)
try:
 for row in rows:
  p=Path(row['local_path']);dest='/root/scilead/axcell/cache/public_python_artifacts/'+row['file']
  try:s.stat(dest);raise RuntimeError('Existing final file must be inspected before reuse')
  except FileNotFoundError:pass
  try:s.stat(dest+'.part');raise RuntimeError('Existing partial transfer must not be overwritten')
  except FileNotFoundError:pass
  tick=[time.monotonic()]
  def progress(sent,total):
   if time.monotonic()-tick[0]>30 or sent==total:print(json.dumps({'file':row['file'],'sent':sent,'total':total}),flush=True);tick[0]=time.monotonic()
  s.put(str(p),dest+'.part',callback=progress)
  c=t.open_session();c.exec_command('sha256sum -- '+shlex.quote(dest+'.part'))
  actual=c.makefile('r').read().decode().split()[0];assert c.recv_exit_status()==0 and actual==row['sha256']
  s.rename(dest+'.part',dest);print(json.dumps({'verified':row['file'],'sha256':actual}),flush=True)
 s.put(str(LOCAL/manifest_name),'/root/scilead/axcell/runs/20261022_single_paper/'+manifest_name)
finally:s.close();t.close()
