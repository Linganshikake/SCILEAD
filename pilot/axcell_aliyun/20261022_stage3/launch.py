from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));from client import remote,execute,paramiko
B='/root/scilead/axcell/runs/20261022_stage3'
t=remote.connect()
try:
 payload='''import json,hashlib,pathlib,subprocess
b=pathlib.Path("%s")
assert not (b/'batch_state.json').exists(), 'Already started; inspect checkpoint instead'
c=json.loads((b/'configuration.json').read_text())
for name,h in c['scripts'].items():assert hashlib.sha256((b/name).read_bytes()).hexdigest()==h
assert hashlib.sha256((b/'queue.json').read_bytes()).hexdigest()==c['queue_sha256']
assert json.loads((b/'service_test_result.json').read_text())['passed']
assert not subprocess.check_output(['docker','ps','-q'],text=True).strip()
subprocess.run(['tmux','new-session','-d','-s','axcell-stage3','cd '+str(b)+' && PYTHONDONTWRITEBYTECODE=1 python3 -u -B controller.py > controller.log 2>&1'],check=True)
print(json.dumps({'started_tmux':'axcell-stage3','no_duplicate_launch':True}))
''' % B
 code,out,err=execute(t,'python3 -',payload.encode(),30)
 (R/'launch_result.json').write_bytes(out);(R/'launch_stderr.txt').write_bytes(err)
 print(out.decode());assert code==0,err.decode()
finally:t.close()
