import datetime,json,subprocess
from pathlib import Path
R=Path('/root/scilead/axcell/runs/20261022_parse_recovery')
p=Path('/root/scilead/axcell/source/axcell/axcell/scripts/__pycache__/guess_main.cpython-310.pyc')
d={'generated_bytecode':None}
if p.exists():
 st=p.stat();d['generated_bytecode']={'path':str(p),'bytes':st.st_size,'mtime_utc':datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),'stat':subprocess.check_output(['stat','-c','%w %y',str(p)],text=True)}
q=R/'attempt_2203_timeout600/parse_logs/2203.16804.pdf/observations/docker_json.log'
if q.exists():
 logs=[json.loads(l) for l in q.read_text().splitlines()];d['docker_stdout']=''.join(x['log'] for x in logs if x.get('stream')=='stdout');d['last_stderr_lines']=''.join(x['log'] for x in logs if x.get('stream')=='stderr')[-3000:]
print(json.dumps(d))
