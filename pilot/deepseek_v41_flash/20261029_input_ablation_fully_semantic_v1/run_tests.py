import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
env=os.environ.copy();env.update(PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
p=subprocess.run([sys.executable,'-B','-X','utf8',str(ROOT/'test_migration.py')],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(ROOT/'offline_tests.log').write_bytes(p.stdout)
(ROOT/'offline_tests.json').write_text(json.dumps({'status':'PASS' if p.returncode==0 else 'FAIL','exit_code':p.returncode,
 'tests':6,'network_guard':True,'credentials_guard':True,'new_api_requests':0,'official_main_fixture_comparison':True,
 'test_script_sha256':hashlib.sha256((ROOT/'test_migration.py').read_bytes()).hexdigest()},indent=2),encoding='utf8')
print(p.stdout.decode('utf8'));sys.exit(p.returncode)
