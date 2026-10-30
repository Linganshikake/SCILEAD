"""Launch isolated branches without changing Windows script execution policy."""
import os,sys,subprocess
from pathlib import Path
from transport import ROOT,load,save,now,digest

def main():
 v=ROOT/'variants'
 assert load(v/'fully_cs/execution_status.json')['status']=='COMPLETE'
 assert load(v/'experiment_manifest.json')['status']=='PREPARED'
 assert load(v/'reproducibility/offline_tests.json')['status']=='PASS'
 with (v/'launcher.lock').open('x',encoding='utf8') as f:f.write(now())
 assert not (v/'live_processes.json').exists(),'Inspect existing launch; no automatic relaunch'
 env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1')
 children=[]
 for branch in ('partially','cold_default','cold_0','cold_42'):
  d=v/branch;out=d/'runtime.stdout.log';err=d/'runtime.stderr.log'
  with out.open('x',encoding='utf8') as o,err.open('x',encoding='utf8') as e:
   p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(v/'variant_runtime.py'),'--branch',branch],cwd=v,env=env,stdout=o,stderr=e,stdin=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
  children.append({'branch':branch,'pid':p.pid,'started_utc':now(),'stdout':str(out),'stderr':str(err),'runner_sha256':digest(v/'variant_runtime.py')})
  save(v/'live_processes.json',children)
 print(__import__('json').dumps(children))
if __name__=='__main__':main()
