"""Pinned SSH; capture remote stdout into a designated report, never credentials."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'20261022_single_paper'))
import remote,paramiko
def execute(t,command,stdin=None,timeout=90):
 c=t.open_session(timeout=20);c.exec_command(command)
 if stdin is not None:c.sendall(stdin)
 c.shutdown_write();start=time.monotonic();out=[];err=[]
 while True:
  if c.recv_ready():out.append(c.recv(65536))
  if c.recv_stderr_ready():err.append(c.recv_stderr(65536))
  if c.exit_status_ready() and c.eof_received and not c.recv_ready() and not c.recv_stderr_ready():break
  if time.monotonic()-start>timeout:raise TimeoutError('Remote status unknown; inspect before retry')
  time.sleep(.05)
 return c.recv_exit_status(),b''.join(out),b''.join(err)
def main():
 p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('report');a=p.parse_args()
 t=remote.connect()
 try:
  code,out,err=execute(t,'PYTHONDONTWRITEBYTECODE=1 python3 -',(ROOT/a.script).read_bytes(),120)
  (ROOT/a.report).write_bytes(out);(ROOT/(a.report+'.stderr')).write_bytes(err)
  print(json.dumps({'exit_code':code,'stdout_bytes':len(out),'stderr_bytes':len(err),'saved':str(ROOT/a.report)}))
 finally:t.close()
if __name__=='__main__':main()
