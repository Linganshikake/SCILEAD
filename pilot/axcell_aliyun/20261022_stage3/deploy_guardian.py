from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from client import remote,paramiko,execute
B='/root/scilead/axcell/runs/20261022_stage3'
t=remote.connect()
try:
 s=paramiko.SFTPClient.from_transport(t)
 try:s.stat(B+'/guardian.py');raise RuntimeError('Guardian already deployed')
 except FileNotFoundError:pass
 s.put(str(R/'guardian.py'),B+'/guardian.py')
 code,out,err=execute(t,'tmux new-session -d -s axcell-stage3-guardian "cd '+B+' && PYTHONDONTWRITEBYTECODE=1 python3 -u -B guardian.py > guardian.log 2>&1"',timeout=20)
 assert code==0,err.decode()
 (R/'guardian_deployment.json').write_text(json.dumps({'sha256':hashlib.sha256((R/'guardian.py').read_bytes()).hexdigest(),'purpose':'Additional procfs monitor for cleanup-period low-memory/ES threshold; no model rerun'},indent=2),encoding='utf-8')
 print('Independent kernel resource guardian started')
finally:t.close()
