import json,subprocess
from pathlib import Path
R=Path('/root/scilead/axcell/runs/20261022_parse_recovery/attempt_2203_timeout600')
L=R/'parse_logs/2203.16804.pdf'
d={'containers':subprocess.check_output(['docker','ps','--format','{{.Names}} {{.Status}}'],text=True),'files':{}}
for name in ['driver.log','attempt_started.json','attempt_finished.json','prelaunch.json']:
 p=R/name
 if p.exists():d['files'][name]=p.read_text()[-2000:]
for name in ['process.log','conversion_linux_status.json','parser_result.json']:
 p=L/name
 if p.exists():d['files'][name]=p.read_text()[-3500:]
p=L/'conversion_linux_resources.jsonl'
if p.exists():
 rows=p.read_text().splitlines();d['sample_count']=len(rows);d['last_sample']=json.loads(rows[-1]);d['max_container_bytes']=max(c.get('memory.current',0) for line in rows for c in json.loads(line)['containers'])
print(json.dumps(d))
