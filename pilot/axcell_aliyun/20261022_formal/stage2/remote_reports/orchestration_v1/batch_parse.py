"""Serial authorized conversion/parse only; durable per-paper checkpoints, stop at P2."""
import csv, datetime, fcntl, json, os, shutil, signal, subprocess, time
from pathlib import Path
from policy import sha, start_guard, reusable
ROOT=Path('/root/scilead/axcell'); RUN=ROOT/'runs/20261022_formal/stage2'; OLD=ROOT/'runs/20261022_single_paper'
PY=ROOT/'envs/axcell-original/bin/python'; stop_signal=None
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2));tmp.replace(path)
def read(p):return json.loads(p.read_text())
def mem_available():return int(next(l for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')).split()[1])*1024
def sig(sig,frame):
    global stop_signal
    stop_signal=sig
def refresh(rows):
    save(RUN/'parse_manifest.json',{'utc_updated':now(),'stage':2,'papers':rows,'author36':'UNVERIFIED','new_extractions':0,'api_calls':0})
    fields=['paper_id','tex_version','status','reused','gold_tdmr_count','fragment_count','table_count','seconds','error','parsed_paper_path','html_path']
    tmp=RUN/'parse_status.csv.tmp'
    with tmp.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    tmp.replace(RUN/'parse_status.csv')

def main():
    lock=(RUN/'task.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for s in [signal.SIGTERM,signal.SIGINT]:signal.signal(s,sig)
    config=read(RUN/'configuration.json'); queue=read(RUN/'queue.json')
    assert sha(RUN/'queue.json')==config['input_queue_sha256']
    for name,h in config['scripts'].items():assert sha(RUN/name)==h
    assert len(queue)==39
    for e in config['expected_assets']:assert sha(ROOT/e['path'])==e['actual_sha256']
    for r in queue:assert sha(r['remote_source'])==r['sha256']
    assert not subprocess.check_output(['docker','ps','-q'],text=True).strip(), 'Unexpected running container'
    assert not start_guard(mem_available(),shutil.disk_usage(RUN).free), 'Start resource guard'
    rows=read(RUN/'parse_manifest.json')['papers'] if (RUN/'parse_manifest.json').exists() else [dict(paper_id=r['paper_id'],tex_version=r['tex_version'],status='PENDING',reused=False,gold_tdmr_count=r['gold_tdmr_count']) for r in queue]
    assert [r['paper_id'] for r in rows]==[r['paper_id'] for r in queue]
    refresh(rows);start=time.monotonic(); disk_before=shutil.disk_usage(RUN).free
    save(RUN/'batch_owner.json',{'pid':os.getpid(),'utc':now(),'stage':2,'model_inference':False})
    for r,state in zip(queue,rows):
        log=RUN/'parse_logs'/r['paper_id'];log.mkdir(parents=True,exist_ok=True)
        if state['status']=='PARSE_COMPLETE':
            result=read(log/'parser_result.json')
            if not reusable(result,r['sha256'],config['configuration_sha256']):
                state.update(status='BLOCKED',error='COMPLETED_ARTIFACT_INTEGRITY_CHANGED');refresh(rows);break
            continue
        if state['status']!='PENDING':continue
        if (log/'attempt.json').exists():
            state.update(status='BLOCKED',error='PRIOR_ATTEMPT_REQUIRES_REVIEW');refresh(rows);continue
        guard=start_guard(mem_available(),shutil.disk_usage(RUN).free)
        if guard or stop_signal or (RUN/'STOP').exists():
            state.update(status='BLOCKED',error=guard or 'TASK_STOP_REQUEST');refresh(rows);break
        save(log/'attempt.json',{'utc':now(),'paper_id':r['paper_id'],'input_sha256':r['sha256'],'reused':r['reuse_original_single']})
        state.update(status='RUNNING',started_utc=now());refresh(rows)
        if r['reuse_original_single']:
            result=read(OLD/'parsed_artifacts.json')
            artifacts=[]
            for directory in [ROOT/'data/papers'/r['tex_version'],ROOT/'data/htmls'/r['tex_version']]:
                for p in sorted(directory.rglob('*')):
                    if p.is_file():artifacts.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
            expected=read(OLD/'task_artifact_hashes.json')
            assert artifacts and all(sha(ROOT/e['path'])==e['sha256'] for e in expected)
            result.update(input_sha256=r['sha256'],configuration_sha256=config['configuration_sha256'],artifacts=artifacts,
                          official_status='success',reused_from=str(OLD),seconds=0,
                          parsed_paper_path=str(ROOT/'data/papers'/r['tex_version']),html_path=str(ROOT/'data/htmls'/r['tex_version']/'index.html'))
            # Cell values remain in the original files; the new index stores only table metadata.
            result['tables']=[{k:v for k,v in t.items() if k!='cells'} for t in result['tables']]
            save(log/'parser_result.json',result);code=0;resource=None;state['reused']=True
        else:
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='6',MKL_NUM_THREADS='6')
            args=['python3',str(RUN/'monitor.py'),'--run',str(log),'--stage','conversion','--timeout',str(config['per_paper_timeout_seconds']),
                  '--',str(PY),str(RUN/'parse_one.py'),r['paper_id']]
            with (log/'process.log').open('x') as output:
                proc=subprocess.Popen(args,stdout=output,stderr=subprocess.STDOUT,env=env)
                while proc.poll() is None:
                    if stop_signal or (RUN/'STOP').exists():proc.send_signal(signal.SIGTERM)
                    time.sleep(1)
                code=proc.returncode
            resource=read(log/'conversion_linux_status.json') if (log/'conversion_linux_status.json').exists() else {'stop_reason':'MONITOR_STATUS_MISSING'}
            result=read(log/'parser_result.json') if (log/'parser_result.json').exists() else None
        if code==0 and result and reusable(result,r['sha256'],config['configuration_sha256']):
            state.update(status='PARSE_COMPLETE',fragment_count=result['fragment_count'],table_count=result['table_count'],
                         seconds=result['seconds'],parsed_paper_path=result['parsed_paper_path'],html_path=result['html_path'],
                         result_path=str(log/'parser_result.json'),warnings=result.get('warnings',[]),error='')
        else:
            reason=(resource or {}).get('stop_reason') or (result or {}).get('official_status') or 'PARSER_EXCEPTION'
            state.update(status='FAILED',error=reason,seconds=(resource or {}).get('seconds'),exit_code=code)
        if resource:state['resource']=resource
        state['finished_utc']=now();refresh(rows)
        print(json.dumps({'paper':r['paper_id'],'status':state['status'],'fragments':state.get('fragment_count'),'tables':state.get('table_count'),'completed':sum(x['status']=='PARSE_COMPLETE' for x in rows),'failed':sum(x['status']=='FAILED' for x in rows)},ensure_ascii=False),flush=True)
        reason=(resource or {}).get('stop_reason')
        if reason and reason!='OWNED_STAGE_TIMEOUT':break
    remaining=subprocess.check_output(['docker','ps','-q','--filter','label=scilead.task=axcell-formal-parse-20261022'],text=True).split()
    assert not remaining, 'Task containers remain; manual inspection required'
    counts={s:sum(r['status']==s for r in rows) for s in ['PENDING','RUNNING','PARSE_COMPLETE','FAILED','BLOCKED']}
    summary={'stage':2,'status':'P2_AWAITING_CONFIRMATION' if not counts['PENDING'] and not counts['RUNNING'] else 'P2_CHECKPOINT_STOPPED',
             'counts':counts,'seconds_this_invocation':time.monotonic()-start,'disk_free_before':disk_before,'disk_free_after':shutil.disk_usage(RUN).free,
             'remaining_task_containers':remaining,'new_model_generations':0,'api_calls':0,'author36':'UNVERIFIED','utc':now()}
    save(RUN/'batch_result.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:
        save(RUN/'batch_error.json',{'utc':now(),'type':type(e).__name__,'message':str(e)});raise
