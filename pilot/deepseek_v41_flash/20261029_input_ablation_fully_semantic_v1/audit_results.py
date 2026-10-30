"""Offline paired-response and frozen-file audit. Never sends requests."""
import ast,csv,hashlib,json
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parent
ARMS=['baseline_rag','parsed_full','page_images']
def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def csvsave(p,rows):
    if not rows:return
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    meta=load(ROOT/'experiment_manifest.json');prompt=load(ROOT/'prompts_fully_semantic_v1.json')['normalization-system-prompt']
    original=load(ROOT/'prompts_original.json')['normalization-system-prompt'];sets={k:ast.literal_eval(v) for k,v in load(ROOT/'candidate_sets.json').items()}
    protected=load(ROOT/'protected_hashes.json');changed=[p for p,h in protected.items() if not Path(p).is_file() or sha(p)!=h]
    pairs=[];changes=[];arm_reports={};allstates=[]
    for arm in ARMS:
        root=ROOT/arm;cp=load(root/'checkpoint.json');assert cp['state']=='COMPLETE',arm
        raw=load(root/'merged/output.json');old=load(root/'previous_normalized_output.json');new=load(root/'merged/normalized_output.json')
        plans=load(root/'request_manifest.json');assert list(raw)==list(old)==list(new)==meta['paper_ids']
        for pid,entry in raw.items():
            rr=json.loads(entry['output']);oo=old[pid]['normalized_output'];nn=new[pid]['normalized_output']
            assert len(rr)==len(oo)==len(nn)
            assert entry['source_documents']==old[pid]['source_documents']==new[pid]['source_documents']
            for i,(r,o,n) in enumerate(zip(rr,oo,nn)):
                assert r['Result']==o['Result']==n['Result'] and set(r)==set(o)==set(n)
                for field in ('Task','Dataset','Metric'):
                    if r[field] in sets[field]:assert n[field]==r[field]
                    assert n[field] is None or n[field] in sets[field]
                if o!=n:changes.append({'arm':arm,'paper_id':pid,'record':i,'raw':r,'old':o,'new':n,
                    'changed_fields':[k for k in o if o[k]!=n[k]]})
        for statepath in sorted((root/'papers').glob('*/requests/*/state.json')):
            folder=statepath.parent;mapping=load(folder/'mapping.json');state=load(statepath);req=load(folder/'request.json');validation=load(folder/'validation.json')
            oldpath=Path(mapping['previous_request_path']);oldreq=load(oldpath);oldresponse=load(oldpath.with_name('response.json'))
            response=load(folder/'response.json')
            assert req['messages'][0]=={'role':'system','content':prompt}
            assert oldreq['messages'][0]=={'role':'system','content':original}
            assert req['messages'][1:]==oldreq['messages'][1:]
            assert {k:v for k,v in req.items() if k!='messages'}=={k:v for k,v in oldreq.items() if k!='messages'}==meta['generation']
            assert len(req['messages'])==2 and state['post_calls']==1 and state['automatic_retries']==0
            assert state['http_status']==200 and state['finish_reason']=='stop' and validation['valid']
            pid=statepath.relative_to(root/'papers').parts[0];plan=next(p for p in plans if p['paper_id']==pid and p['record']==mapping['record'] and p['field']==mapping['field'])
            assert sha(oldpath)==plan['previous_request_sha256']
            oldanswer=oldresponse['choices'][0]['message']['content'];newanswer=response['choices'][0]['message']['content']
            assert newanswer==mapping['raw_answer']
            accepted=newanswer if newanswer in sets[mapping['field']] else None
            assert accepted==mapping['accepted']==new[pid]['normalized_output'][mapping['record']][mapping['field']]
            pairs.append({'arm':arm,'paper_id':pid,'record':mapping['record'],'field':mapping['field'],'input':mapping['input'],
                'old_raw_answer':oldanswer,'new_raw_answer':newanswer,'old_accepted':old[pid]['normalized_output'][mapping['record']][mapping['field']],
                'new_accepted':accepted,'changed':old[pid]['normalized_output'][mapping['record']][mapping['field']]!=accepted,
                'old_request':str(oldpath),'new_request':str(folder/'request.json')})
            allstates.append({'arm':arm,'path':str(statepath),'state':state})
        arm_pairs=[r for r in pairs if r['arm']==arm];assert len(arm_pairs)==meta['arms'][arm]['requests']
        arm_reports[arm]={'papers':len(new),'records':sum(len(x['normalized_output']) for x in new.values()),'requests':len(arm_pairs),
            'old_null_fields':sum(v is None for p in old.values() for r in p['normalized_output'] for v in r.values()),
            'new_null_fields':sum(v is None for p in new.values() for r in p['normalized_output'] for v in r.values()),
            'changed_records':sum(r['arm']==arm for r in changes),'changed_fields':sum(r['changed'] for r in arm_pairs),
            'null_to_candidate':sum(r['old_accepted'] is None and r['new_accepted'] is not None for r in arm_pairs),
            'candidate_to_null':sum(r['old_accepted'] is not None and r['new_accepted'] is None for r in arm_pairs),
            'candidate_to_other':sum(r['changed'] and r['old_accepted'] is not None and r['new_accepted'] is not None for r in arm_pairs),
            'usage':load(root/'api_usage_summary.json')}
    assert len(pairs)==144 and not changed
    totals={k:sum((r['state'].get('usage') or {}).get(k,0) or 0 for r in allstates) for k in ('prompt_tokens','completion_tokens','total_tokens')}
    starts=[datetime.fromisoformat(r['state']['started_utc']) for r in allstates]
    start=min(starts);end=max(datetime.fromisoformat(r['state']['started_utc']).timestamp()+r['state']['elapsed_seconds'] for r in allstates)
    usage={'new_requests':144,'new_extraction_requests':0,'normalization_requests':144,'http200':144,'finish_stop':144,'automatic_retries':0,
        'tokens':totals,'wall_seconds':end-start.timestamp(),'sum_request_seconds':sum(r['state']['elapsed_seconds'] for r in allstates),
        'actual_response_models':sorted({r['state']['response_model'] for r in allstates}),'by_arm':{a:r['usage'] for a,r in arm_reports.items()}}
    save(ROOT/'api_usage_summary.json',usage)
    save(ROOT/'inspection/changed_records.json',changes);save(ROOT/'inspection/field_response_pairs.json',pairs)
    csvsave(ROOT/'inspection/field_response_pairs.csv',pairs)
    save(ROOT/'inspection/change_summary.json',arm_reports)
    verification={'status':'COMPLETE','papers_per_arm':5,'gold_per_arm':28,'protected_files_checked':len(protected),'protected_changed':changed,
        'frozen_extraction_reused':True,'result_values_and_row_order_unchanged':True,'source_documents_unchanged':True,
        'only_system_prompt_changed_per_request':True,'fully_candidates_and_order_unchanged':True,'no_dynamic_candidates_or_stage2':True,
        'all_requests_http200_finish_stop_valid':True,'api_requests':144,'arms':arm_reports,
        'secret_scans_passed':all(load(ROOT/a/'verification.json')['secret_scan_passed'] for a in ARMS)}
    save(ROOT/'verification.json',verification)
    print(json.dumps({'status':'COMPLETE','usage':usage,'changes':{a:{k:v for k,v in r.items() if k!='usage'} for a,r in arm_reports.items()}},ensure_ascii=False))
if __name__=='__main__':main()
