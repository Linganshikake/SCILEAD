import sys,json,pathlib,posixpath
R=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R));from client import remote,paramiko,execute
DEST='/root/scilead/axcell/runs/20261022_stage3'
t=remote.connect()
try:
 s=paramiko.SFTPClient.from_transport(t)
 try:s.stat(DEST+'/batch_state.json');raise RuntimeError('Batch started: deployment frozen')
 except FileNotFoundError:pass
 try:s.mkdir(DEST)
 except IOError:s.stat(DEST)
 files=['controller.py','worker.py','policy.py','test_policy.py','test_cleanup.py','queue.json','configuration.json','remote_before.json','service_test.py']
 for name in files:s.put(str(R/name),DEST+'/'+name)
 code,out,err=execute(t,'cd '+DEST+' && PYTHONDONTWRITEBYTECODE=1 python3 -B test_policy.py',timeout=30)
 (R/'remote_policy_tests.txt').write_bytes(out+err);assert code==0
 code,out,err=execute(t,'cd '+DEST+' && PYTHONDONTWRITEBYTECODE=1 python3 -B test_cleanup.py',timeout=30)
 (R/'remote_cleanup_tests.txt').write_bytes(out+err);assert code==0
 print(json.dumps({'uploaded':files,'policy_tests_exit':code}))
finally:t.close()
