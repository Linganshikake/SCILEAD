from pathlib import Path
import subprocess,sys,json,hashlib
ROOT=Path('/root/autodl-tmp/scilead');R=ROOT/'runs/llama3/20261021_formal42'
baseline=(ROOT/'setup/environment/llama_freeze.txt').read_text()
actual=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
assert baseline.splitlines()==actual.splitlines(),'DEPENDENCY_FREEZE_CHANGED'
out=R/'reproducibility';out.mkdir(parents=True,exist_ok=True);(out/'llama_freeze.txt').write_text(actual)
proof={'status':'PASS','full_dependency_freeze_unchanged':True,'packages':len(actual.splitlines()),'baseline_freeze_sha256':hashlib.sha256(baseline.encode()).hexdigest(),'actual_freeze_sha256':hashlib.sha256(actual.encode()).hexdigest(),'python':sys.version,'executable':sys.executable}
(out/'environment_verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
