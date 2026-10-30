"""Normalization-only adapter; original Fully mapping and frozen durable transport."""
import argparse,ast,json,msvcrt,sys,time,csv
from pathlib import Path
import httpx
sys.dont_write_bytecode=True
from transport import ROOT,MODEL,BASE,save,load,digest,now,load_credentials
from frozen_runner import request,resources,ServiceStop,FormatStop
REPO=Path(r'D:\C++\SCILEAD\emnlp2024-leaderboard-generation')
ARMS=('baseline_rag','parsed_full','page_images')

def messages(system,items,value):
    return [{'role':'system','content':system},{'role':'user','content':'\n\nItem list: '+items+'\n\nInput: '+value+'\n\nAnswer: '}]

def normalize_rows(rows,sets,call):
    result=[]
    for i,row in enumerate(rows):
        nr={}
        for key,value in row.items():
            if key!='Result' and value not in sets[key]:
                answer=call(i,key,value)
                nr[key]=answer if answer in sets[key] else None
            else:nr[key]=str(value)
        result.append(nr)
    return result

def verify():
    protected=load(ROOT/'protected_hashes.json')
    changed=[p for p,h in protected.items() if not Path(p).is_file() or digest(p)!=h]
    assert not changed,'FROZEN_FILE_CHANGED: '+str(changed[:3])
    return len(protected)

def summarize(arm,checkpoint):
    root=ROOT/arm;states=[]
    for p in sorted((root/'papers').glob('*/requests/*/state.json')):
        s=load(p);u=s.get('usage') or {};v=load(p.parent/'validation.json') if (p.parent/'validation.json').exists() else {}
        states.append({'paper_id':p.relative_to(root/'papers').parts[0],'request':str(p.parent),'status':s['status'],
            'http_status':s.get('http_status'),'finish_reason':s.get('finish_reason'),'request_model':s.get('request_model'),
            'response_model':s.get('response_model'),'validated':v.get('valid',False),'prompt_tokens':u.get('prompt_tokens'),
            'completion_tokens':u.get('completion_tokens'),'total_tokens':u.get('total_tokens'),
            'elapsed_seconds':s.get('elapsed_seconds'),'request_id':s.get('response_id')})
    usage={k:sum(s.get(k) or 0 for s in states) for k in ('prompt_tokens','completion_tokens','total_tokens','elapsed_seconds')}
    usage.update(attempts=len(states),validated=sum(s['validated'] for s in states),unknown_usage=sum(s['total_tokens'] is None for s in states),automatic_retries=0,new_extractions=0)
    save(root/'api_usage_summary.json',usage);save(root/'request_status.json',states);save(root/'checkpoint.json',checkpoint)
    merged={}
    for pid,s in checkpoint['papers'].items():
        if s['status']=='COMPLETE':merged.update(load(root/'papers'/pid/'normalized_output.json'))
    save(root/'merged/normalized_output.json',merged)
    return usage

def main(arm):
    assert load(ROOT/'offline_tests.json')['status']=='PASS'
    protected_count=verify();root=ROOT/arm
    lock=(root/'process.lock').open('a+b');lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    raw=load(root/'merged/output.json');planned=load(root/'request_manifest.json')
    strings=load(ROOT/'candidate_sets.json');sets={k:ast.literal_eval(v) for k,v in strings.items()}
    system=load(ROOT/'prompts_fully_semantic_v1.json')['normalization-system-prompt']
    cp=load(root/'checkpoint.json') if (root/'checkpoint.json').exists() else {'state':'PENDING','started_utc':now(),
        'papers':{p:{'status':'PENDING','records':len(json.loads(e['output'])),'requests_complete':0,'null_fields':None} for p,e in raw.items()}}
    key,base=load_credentials();assert base==BASE
    cp['state']='RUNNING';stop=None
    try:
        with httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20)) as client:
            for pid,entry in raw.items():
                paper=root/'papers'/pid;s=cp['papers'][pid]
                if s['status']=='COMPLETE':
                    assert all(digest(paper/f)==h for f,h in load(paper/'completion_hashes.json').items())
                    continue
                if s['status'] in ('BLOCKED','FORMAT_FAILED'):continue
                s['status']='RUNNING';save(root/'checkpoint.json',cp);count=0
                try:
                    def call(i,k,v):
                        nonlocal count
                        count+=1;folder=paper/'requests'/f'{count:03d}_record{i}_{k}'
                        plan=next(x for x in planned if x['paper_id']==pid and x['record']==i and x['field']==k)
                        assert plan['input']==v and plan['candidate_serialized']==strings[k]
                        nm=messages(system,strings[k],v)
                        old=load(plan['previous_request_path']);assert old['messages'][1]==nm[1]
                        _,answer=request(client,folder,nm,key,False)
                        accepted=answer if answer in sets[k] else None
                        save(folder/'mapping.json',{'record':i,'field':k,'input':v,'raw_answer':answer,'accepted':accepted,
                            'previous_request_path':plan['previous_request_path'],'reason':'EXACT_CANDIDATE' if accepted is not None else 'OUTSIDE_CANDIDATES'})
                        s['requests_complete']=count;save(root/'checkpoint.json',cp)
                        print(json.dumps({'arm':arm,'paper':pid,'call':count,'field':k,'accepted':accepted is not None}),flush=True)
                        return answer
                    rows=json.loads(entry['output']);normalized=normalize_rows(rows,sets,call)
                    assert len(rows)==len(normalized) and [r['Result'] for r in rows]==[r['Result'] for r in normalized]
                    save(paper/'normalized_output.json',{pid:{'normalized_output':normalized,'source_documents':entry['source_documents']}})
                    s.update(status='COMPLETE',null_fields=sum(v is None for row in normalized for v in row.values()))
                    save(paper/'completion_hashes.json',{str(p.relative_to(paper)):digest(p) for p in paper.rglob('*') if p.is_file() and p.name!='completion_hashes.json'})
                    summarize(arm,cp)
                except FormatStop as e:
                    s.update(status='FORMAT_FAILED',error=str(e));save(paper/'failure.json',{'error':str(e),'raw_retained':True});summarize(arm,cp)
                except ServiceStop as e:
                    s.update(status='BLOCKED',error=str(e));stop={'paper':pid,'error':str(e)};break
        cp['state']='COMPLETE' if all(s['status']=='COMPLETE' for s in cp['papers'].values()) else 'INCOMPLETE'
    except Exception as e:
        cp['state']='ENGINEERING_STOP';stop={'type':type(e).__name__,'reason':str(e).replace(key,'[REDACTED]')[:300]}
    finally:
        cp.update(updated_utc=now(),stop=stop);usage=summarize(arm,cp)
        changed=[p for p,h in load(ROOT/'protected_hashes.json').items() if not Path(p).exists() or digest(p)!=h]
        secret_free=all(key.encode() not in p.read_bytes() for p in root.rglob('*') if p.is_file())
        save(root/'verification.json',{'status':cp['state'],'protected_count':protected_count,'protected_changed':changed,
             'secret_scan_passed':secret_free,'complete_papers':sum(s['status']=='COMPLETE' for s in cp['papers'].values()),'usage':usage,'stop':stop})
        print(json.dumps({'arm':arm,'state':cp['state'],'usage':usage,'stop':stop}),flush=True);lock.close()
    return 0 if cp['state']=='COMPLETE' else 2

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--arm',choices=ARMS,required=True);a=p.parse_args();sys.exit(main(a.arm))
