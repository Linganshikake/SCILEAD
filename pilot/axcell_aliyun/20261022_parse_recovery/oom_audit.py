import json,subprocess
from pathlib import Path
d={}
for name,cmd in [('kernel_journal',['journalctl','-k','--since','2026-10-22 17:24:00','--until','2026-10-22 17:36:00','--no-pager']),('dmesg',['dmesg','--ctime'])]:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
 lines=p.stdout.splitlines();hit=[i for i,l in enumerate(lines) if any(x in l.lower() for x in ['oom','killed process','out of memory','c31b0592c630'])]
 selected=sorted({j for i in hit for j in range(max(0,i-5),min(len(lines),i+10))})
 d[name]={'exit_code':p.returncode,'stderr':p.stderr,'matching_context':[lines[i] for i in selected]}
d['vmstat']={k:int(v) for k,v in (l.split() for l in Path('/proc/vmstat').read_text().splitlines()) if k in ['oom_kill','pswpin','pswpout']}
print(json.dumps(d))
