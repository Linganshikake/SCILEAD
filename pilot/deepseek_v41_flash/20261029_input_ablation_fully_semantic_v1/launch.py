"""Launch only approved Fully normalization; no Partially/Cold/Extraction paths."""
import json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf8'))
def main():
    assert read(ROOT/'offline_tests.json')['status']=='PASS'
    import normalize_fully as n
    n.verify()
    assert read(ROOT/'experiment_manifest.json')['normalization_requests']==144
    assert not (ROOT/'live_processes.json').exists(),'Prior launch requires status inspection'
    env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
    children=[]
    with (ROOT/'launcher.lock').open('x') as f:f.write(datetime.now(timezone.utc).isoformat())
    for arm in n.ARMS:
        with (ROOT/arm/'stdout.log').open('x',encoding='utf8') as out,(ROOT/arm/'stderr.log').open('x',encoding='utf8') as err:
            p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(ROOT/'normalize_fully.py'),'--arm',arm],cwd=ROOT,env=env,
                stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        children.append({'arm':arm,'pid':p.pid,'utc':datetime.now(timezone.utc).isoformat()})
        (ROOT/'live_processes.json').write_text(json.dumps(children,indent=2),encoding='utf8')
    print(json.dumps(children))
if __name__=='__main__':main()
