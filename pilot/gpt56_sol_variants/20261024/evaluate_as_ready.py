"""Offline scheduling only: evaluate each completed branch exactly once."""
import time
from evaluate_variants import *

def main():
    boundary();v.verify();pending=set(BRANCHES);results={};deadline=time.monotonic()+3600
    while pending and time.monotonic()<deadline:
        for branch in BRANCHES:
            if branch not in pending:continue
            run=v.TOP/branch
            summaries=[run/stage/'summary.json' for stage in STAGES]
            if not all(p.exists() and v.read(p).get('status')=='COMPLETE' for p in summaries):continue
            status=run/'evaluation/status.json'
            assert not status.exists(),'Existing evaluation must be audited, not silently overwritten'
            results[branch]=evaluate_branch(branch);pending.remove(branch)
            v.save(v.TOP/'evaluation_status.json',{'status':'RUNNING','branches':results,'pending':sorted(pending),'new_api_requests':0})
            print(json.dumps({'branch':branch,'evaluation':results[branch]['status']}),flush=True)
            if results[branch]['status']!='COMPLETE':return 2
        if pending:time.sleep(5)
    reference=v.read(v.TOP/'evaluation_references/gpt56_fully/status.json')
    complete=not pending and reference['status']=='COMPLETE'
    v.save(v.TOP/'evaluation_status.json',{'status':'COMPLETE' if complete else 'INCOMPLETE','branches':results,'pending':sorted(pending),'gpt56_fully_reference':reference,'new_api_requests':0,'source_integrity':v.verify()})
    return 0 if complete else 2

if __name__=='__main__':sys.exit(main())
