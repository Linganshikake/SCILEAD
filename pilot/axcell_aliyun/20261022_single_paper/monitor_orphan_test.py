import subprocess,sys,json,time,os,signal
from pathlib import Path
run=Path('/root/scilead/axcell/runs/20261022_single_paper')
stage=sys.argv[1]
parent="import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)']); time.sleep(.5); raise SystemExit(1)"
monitor=['python3','/root/scilead/axcell/scripts/monitor.py','--stage',stage,'--timeout','15','--','python3','-c',parent]
q=subprocess.run(monitor)
owner=json.loads((run/(stage+'_linux_owner.json')).read_text())
rows=subprocess.check_output(['ps','-eo','pid=,pgid=,stat=,comm='],text=True).splitlines()
left=[s for s in rows if len(s.split())==4 and int(s.split()[1])==owner['pgid'] and not s.split()[2].startswith('Z')]
print(json.dumps({'test':stage,'monitor_returncode':q.returncode,'live_owned_descendants':left}),flush=True)
if left:
 os.killpg(owner['pgid'],signal.SIGKILL)
 raise SystemExit(1)
print('Exited-parent cleanup: PASS')
