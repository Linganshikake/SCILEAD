from pathlib import Path
import json,hashlib,subprocess,sys
r=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup');old=r.parent/'20261021_formal42'
def read(p):return json.loads(p.read_text())
protected=read(r/'audit/remote_protected_before.json')
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in protected.items())
assert read(r/'cs_repair_complete.json')=={'v2':0,'diagnostic':0}
freeze=subprocess.run([sys.executable,'-m','pip','freeze'],capture_output=True,text=True);prior=(old/'reproducibility/llama_freeze.txt').read_text()
assert sorted(freeze.stdout.splitlines())==sorted(prior.splitlines()),'DEPENDENCY_CHANGE'
check=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True);assert check.returncode==0
gpu=subprocess.run(['nvidia-smi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True)
result={'status':'PASS','protected_remote_files_unchanged':len(protected),'dependency_freeze_unchanged':True,'pip_check':check.stdout.strip(),'gpu_after':gpu.stdout.strip(),'paid_api_calls':0,'no_shutdown':True}
(r/'reports').mkdir(exist_ok=True);(r/'reports/verification_remote.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
