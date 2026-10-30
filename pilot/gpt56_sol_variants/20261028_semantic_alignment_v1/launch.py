"""Launch four approved independent normalization branches once."""
import json,os,subprocess,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def now():return datetime.now(timezone.utc).isoformat()
def main():
 v=ROOT;assert load(v/'reproducibility/offline_tests.json')['status']=='PASS'
 assert load(ROOT/'experiment_manifest.json')['status']=='PREPARED'
 assert not (ROOT/'live_processes.json').exists(),'Existing launch must be inspected, not repeated'
 for path,h in load(ROOT/'protected_hashes.json').items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
 with (ROOT/'launcher.lock').open('x',encoding='utf8') as f:f.write(now())
 env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
 children=[]
 for b in ['partially','cold_default','cold_0','cold_42']:
  d=v/b
  with (d/'runtime.stdout.log').open('x',encoding='utf8') as out,(d/'runtime.stderr.log').open('x',encoding='utf8') as err:
   p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(v/'variant_runtime.py'),'--branch',b],cwd=v,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
  children.append({'branch':b,'pid':p.pid,'started_utc':now(),'runner_sha256':hashlib.sha256((v/'variant_runtime.py').read_bytes()).hexdigest(),'prompt_sha256':hashlib.sha256((ROOT/'prompts_semantic_v1.json').read_bytes()).hexdigest()})
  (ROOT/'live_processes.json').write_text(json.dumps(children,indent=2),encoding='utf8')
 print(json.dumps(children))
if __name__=='__main__':main()
