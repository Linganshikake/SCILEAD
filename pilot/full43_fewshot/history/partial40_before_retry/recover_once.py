"""Explicitly authorized, bounded recovery; never remove failed attempt ledgers."""
import argparse, contextlib, shutil
from common import *

TARGETS={'D19-1367.pdf':3,'K19-1036.pdf':3,'N19-1373.pdf':2}

def prepare():
    setup(); verify()
    snapshot=RUN/'history/partial40_before_retry'
    assert not snapshot.exists(), 'Snapshot already exists; do not recreate it'
    index=read(RUN/'artifact_sha256.json')
    for rel,h in index.items():assert sha(RUN/rel)==h,rel
    m=read(RUN/'manifest.json')
    assert len(m['papers'])==43
    for row in m['papers']:
        no=Path(row['normalization_dir']);s=read(no/'summary.json')
        assert s['status']==('FAILED' if row['id'] in TARGETS else 'COMPLETE')
        if row['id'] in TARGETS:
            assert len(read(no/'request_plan.json'))==TARGETS[row['id']]
            assert len(list((no/'api_calls').glob('*/attempt.json')))==1
            assert read(no/'api_calls/0001/state.json')['http_status']==502
    snapshot.mkdir(parents=True)
    for p in RUN.iterdir():
        if p.is_file():shutil.copyfile(p,snapshot/p.name)
    for name in ('evaluation','inspection','leaderboard'):
        shutil.copytree(RUN/name,snapshot/name)
    immutable(RUN/'recovery_preserved_paper_hashes.json',{rel:h for rel,h in index.items() if rel.startswith('papers/')})
    immutable(snapshot/'snapshot_hashes.json',{str(p.relative_to(snapshot)):sha(p) for p in snapshot.rglob('*') if p.is_file()})
    immutable(RUN/'recovery_authorization.json',{
        'user_statement':'允许各补发一次，接受可能重复计费',
        'scope':TARGETS,'maximum_new_requests':8,'maximum_retries_per_failed_request':1,
        'authorized_retry_requests':3,'never_attempted_fields':5,'automatic_retries':0,
        'preserve_all_failed_ledgers':True,'stop_paper_on_another_failure':True,
        'snapshot':str(snapshot),'recorded_epoch':time.time()})
    print('PREPARED: verified existing artifacts, preserved partial40 snapshot, bounded authorization recorded')

def execute():
    setup('normalize');verify();assert os.environ.get('PYTHONHASHSEED')=='0'
    import run as adapter
    auth=read(RUN/'recovery_authorization.json');assert auth['scope']==TARGETS and auth['maximum_new_requests']==8
    original=read(RUN/'history/partial40_before_retry/manifest.json')
    m=read(RUN/'manifest.json');outcomes=[]
    for paper,n in TARGETS.items():
        previous=next(r for r in original['papers'] if r['id']==paper)
        old=Path(previous['normalization_dir']);new=old.parent.parent/'normalization_retry_once/normalization'
        raw=read(Path(previous['extraction_dir'])/'output.json')
        plan,labels=adapter.normalization_plan(paper,json.loads(raw[paper]['output']))
        assert plan==read(old/'request_plan.json') and len(plan)==n
        first=read(old/'api_calls/0001/request.json')
        assert first['messages']==plan[0]['messages']
        assert first['model']==MODEL and first['seed']==0 and first['temperature']==0
        assert not set(first)&{'max_tokens','max_output_tokens','max_completion_tokens'}
        assert read(old/'api_calls/0001/state.json')['http_status']==502
        row=next(r for r in m['papers'] if r['id']==paper)
        new.mkdir(parents=True,exist_ok=True)
        if (new/'summary.json').exists():
            status=read(new/'summary.json')['status']
            print('SKIP_RECORDED_RECOVERY',paper,status,flush=True)
        else:
            print('RECOVERY_START',paper,n,flush=True)
            with (new/'run.log').open('a',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
                try:adapter.normalization(previous,output_override=new)
                except Exception as e:print('STOP',type(e).__name__,scrub(str(e)),flush=True)
            status=read(new/'summary.json')['status'] if (new/'summary.json').exists() else 'INTERRUPTED'
        if (new/'api_calls/0001/request.json').exists():
            assert read(new/'api_calls/0001/request.json')==first,'Retry payload changed'
        assert len(list((new/'api_calls').glob('*/attempt.json')))<=n
        archives=m.setdefault('archived_attempt_stages',[])
        if status=='COMPLETE':
            row['normalization_dir']=str(new);row['normalize_status']='COMPLETE';row['status']='COMPLETE'
            archived={'paper':paper,'stage':'normalize','path':str(old),'reason':'HTTP 502; explicitly authorized one replacement in independent directory'}
        else:
            archived={'paper':paper,'stage':'normalize','path':str(new),'reason':'Authorized recovery failed or interrupted; no further retry authorized'}
        if archived not in archives:archives.append(archived)
        save(RUN/'manifest.json',m)
        outcomes.append({'paper':paper,'status':status,'old_failed_dir':str(old),'recovery_dir':str(new),'requests':len(list((new/'api_calls').glob('*/attempt.json')))})
        save(RUN/'recovery_results.json',{'outcomes':outcomes,'epoch':time.time(),'automatic_retries':0})
        print('RECOVERY_END',paper,status,flush=True)
    assert sum(x['requests'] for x in outcomes)<=8
    for rel,h in read(RUN/'recovery_preserved_paper_hashes.json').items():assert sha(RUN/rel)==h,rel
    print('RECOVERY_FINISHED',json.dumps(outcomes),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','execute']);a=parser.parse_args()
    (prepare if a.action=='prepare' else execute)()
