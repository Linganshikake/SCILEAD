"""No models: prove transient systemd isolation, process-tree cleanup and monitor visibility."""
import sys,time,json,subprocess
from pathlib import Path
sys.path.insert(0,'/root/scilead/axcell/runs/20261022_stage3')
from controller import cmd,unitinfo,cgread,save,BASE
unit='axcell-stage3-worker-guardtest.service'
code='import subprocess,time; a=bytearray(32*1024*1024); subprocess.Popen(["/usr/bin/python3","-c","import time; a=bytearray(32*1024*1024); time.sleep(60)"]); time.sleep(60)'
try:
 r=cmd(['systemd-run','--quiet','--unit='+unit,'--property=Type=exec','--property=RemainAfterExit=yes','--property=MemoryMax=256M','--property=MemorySwapMax=0','--property=KillMode=control-group','--property=TimeoutStopSec=2s','/usr/bin/python3','-c',code])
 time.sleep(1);info=unitinfo(unit);group=info['ControlGroup'];observed=cgread(group)
 assert observed['memory']>60*1024**2 and observed['rss']>60*1024**2
 started=time.monotonic();stop=cmd(['systemctl','stop',unit]);elapsed=time.monotonic()-started
 final=unitinfo(unit);cg=Path('/sys/fs/cgroup')/group.lstrip('/')
 assert final.get('ActiveState') not in ['active','activating','deactivating']
 assert not cg.exists() or not (cg/'cgroup.procs').read_text().strip()
 result={'passed':True,'observed':observed,'stop_seconds':elapsed,'final':final,'models_loaded':0,'api_calls':0}
 save(BASE/'service_test_result.json',result);print(json.dumps(result))
finally:cmd(['systemctl','stop',unit],False)
