from pathlib import Path
LOCAL=Path(__file__).resolve().parent
import remote
import paramiko,json,hashlib
t=remote.connect()
try:
 s=paramiko.SFTPClient.from_transport(t)
 for name in ['monitor.py','run_single.py','install_pip.sh','launch_pip_relay.sh','validate_environment.py','validate_conversion.py','run_stage.sh','launch_validation.sh','final_audit.py','test_adapter_guards.py']:
  p=LOCAL/name;destination='/root/scilead/axcell/scripts/'+name
  s.put(str(p),destination)
  with s.open(destination,'rb') as f:actual=hashlib.sha256(f.read()).hexdigest()
  assert actual==hashlib.sha256(p.read_bytes()).hexdigest()
  print(json.dumps({'uploaded':name,'sha256':actual}),flush=True)
 s.close()
finally:t.close()
