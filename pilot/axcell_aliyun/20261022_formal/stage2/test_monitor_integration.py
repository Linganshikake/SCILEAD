"""Linux safety regression: inject owner-write failure and inspect cleanup ordering."""
import importlib.util,json,os,signal,sys
from pathlib import Path
from unittest.mock import patch
revision=Path(sys.argv[1]);mode=sys.argv[2];assert mode in ('owner_failure','cleanup_order')
sys.path.insert(0,str(revision))
spec=importlib.util.spec_from_file_location('audit_monitor',revision/'monitor.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
run=Path('/root/scilead/axcell/runs/20261022_formal/stage2/safety_tests')/revision.name/mode
run.mkdir(parents=True,exist_ok=False)
real_popen=m.subprocess.Popen;real_write=Path.write_text;tracked=[];order=[];error=None
def popen(*args,**kwargs):
    p=real_popen(*args,**kwargs)
    if kwargs.get('start_new_session'):tracked.append(p)
    return p
def write(p,*args,**kwargs):
    if p.name.endswith('_linux_owner.json'):raise OSError('INJECTED_OWNER_WRITE_FAILURE')
    return real_write(p,*args,**kwargs)
real_cleanup=m.cleanup_group
def group(p,*args,**kwargs):order.append('group');return real_cleanup(p,*args,**kwargs)
def containers():order.append('containers');return {'events':[],'remaining_running_task_containers':[]}
argv=['monitor','--run',str(run),'--stage','conversion','--timeout','1','--','python3','-c','import subprocess,time;subprocess.Popen(["sleep","60"]);time.sleep(60)']
try:
    with patch.object(sys,'argv',argv),patch.object(m.subprocess,'Popen',popen),patch.object(m,'container_samples',lambda:[]),patch.object(m,'cleanup_group',group),patch.object(m,'cleanup_containers',containers):
        if mode=='owner_failure':
            with patch.object(Path,'write_text',write):m.main()
        else:m.main()
except (Exception,SystemExit) as e:error=type(e).__name__+':'+str(e)
live=[x for p in tracked for x in m.group_members(p.pid)]
passed=(not live) if mode=='owner_failure' else (order==['group','containers'] and not live)
# The RED run intentionally exposes orphan behavior. Clean up only its recorded PGID.
for p in tracked:
    if m.group_members(p.pid):real_cleanup(p,grace=5)
d={'revision':revision.name,'mode':mode,'passed':passed,'order':order,'surviving_members_before_test_cleanup':live,'caught':error,'all_test_children_cleaned':all(not m.group_members(p.pid) for p in tracked)}
(run/'regression_result.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));raise SystemExit(0 if passed else 3)
