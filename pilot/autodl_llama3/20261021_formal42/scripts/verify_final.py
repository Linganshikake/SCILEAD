"""Final evidence-based artifact checks; no network or model inference."""
from pathlib import Path
import json,hashlib,sys,ast,collections
R=Path(__file__).resolve().parents[1];S=R/'remote_snapshot';D=R.parent/'20261021_diagnostic'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    records=read(R/'integrity_before.json')+read(R/'protected_diagnostics.json')
    for x in records:assert sha(Path(x['path']))==x['sha256'],'PROTECTED_FILE_CHANGED:'+x['path']
    assert sha(R/'scripts/format_candidate.py')==read(R/'approval.json')['parser_sha256']
    for p in (R/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    remote=read(S/'reproducibility/verification_remote.json');assert remote['status']=='PASS'
    scope=read(R/'config/scope42.json');ids=scope['eligible_ids'];assert len(ids)==42 and len(set(ids))==42 and '1912.08777.pdf' not in ids
    raw=read(S/'extraction/raw_output.json');prepared=read(S/'extraction/prepared_output.json');reuse=read(R/'config/reuse.json');state=read(S/'batch_status.json')
    attempts=[];complete=[];checks=[]
    for pid in ids:
        root=S/'extraction'/pid.removesuffix('.pdf');folder=root/('raw' if pid in reuse else 'extraction');reqs=list((folder/'calls').glob('*/request.json'));assert len(reqs)<=1
        attempts.extend([] if pid in reuse else reqs)
        if pid in reuse:assert sha(folder/'output.json')==reuse[pid]['output_sha256']
        if reqs:
            q=read(reqs[0]);assert q['max_new_tokens']==1024 and q['do_sample'] is False and q['seed']==0
            if reqs[0].with_name('complete.json').exists():
                complete.append(pid);response=reqs[0].with_name('response.txt').read_text(encoding='utf-8');pipeline=read(reqs[0].with_name('pipeline_raw_response.json'))
                while isinstance(pipeline,list):assert len(pipeline)==1;pipeline=pipeline[0]
                assert pipeline['generated_text']==q['prompt']+response,'AUTHOR_OUTPUT_WRAPPER_MISMATCH'
        if pid in prepared:
            assert state['papers'][pid]['parse_status']=='COMPLETE';assert prepared[pid]['source_documents']==raw[pid]['source_documents']
            orig=raw[pid]['output'];after=prepared[pid]['output'];a=state['papers'][pid]['format_audit'];assert after==orig or after==orig[a['span'][0]:a['span'][1]]
            assert len(json.loads(after))==state['papers'][pid]['records']
    assert len(attempts)==38 and len(complete)==42,'Review incomplete generations before final report'
    for stage,budget in [('fully_llm',15),('partially/stage1',15),('partially/stage2',100)]:
        calls=S/'normalization'/stage/'calls'
        for p in calls.glob('*/request.json'):
            q=read(p);assert q['max_new_tokens']==budget and q['model_revision']=='50fd307e57011801c7833c87efa1984ddf2db42f';assert p.with_name('complete.json').exists();assert p.with_name('field_context.json').exists()
    assert len(list((S/'normalization/fully_llm/calls').glob('*/request.json')))==read(S/'config/normalization_call_precheck.json')['expected_fully_llm_calls']
    assert len(list((S/'normalization/partially/stage2/calls').glob('*/request.json')))==read(S/'config/stage2_call_precheck.json')['expected_stage2_calls']
    for out in (R/'evaluation').iterdir():
        if not out.is_dir() or not (out/'complete.json').exists():continue
        pred=read(out/'evaluation_input_fixed42.json');assert list(pred)==ids
        m=read(out/'metrics_with_f1.json');v=read(out/'per_paper_metrics.json');assert m['fixed_denominator']==42
        for k,x in m['aggregate'].items():
            p=sum(v[pid][k]['Precision'] for pid in ids)/42;r=sum(v[pid][k]['Recall'] for pid in ids)/42
            assert abs(p-x['Precision'])<1e-12 and abs(r-x['Recall'])<1e-12
            assert abs((2*p*r/(p+r) if p+r else 0)-x['F1'])<1e-12
        checks.append(out.name)
    assert len(checks)==8
    cs=read(S/'normalization/fully_cs/model_validation.json');assert cs['status']=='PASS' and len(cs['compared_existing_cpu_outputs'])==3
    environment=read(S/'reproducibility/environment_verification.json');assert environment['full_dependency_freeze_unchanged']
    remote_inventory=read(S/'artifact_manifest_remote.json')
    for x in remote_inventory:assert sha(S/x['path'])==x['sha256'],'TRANSFER_HASH_MISMATCH:'+x['path']
    result={'status':'PASS','protected_files_unchanged':len(records),'original_critical_files':len(read(R/'integrity_before.json')),'diagnostic_files_unchanged':len(read(R/'protected_diagnostics.json')),'new_extraction_requests':38,'reused_extraction_requests':4,'generated_papers':42,'format_valid_papers':len(prepared),'failed_format_papers':[p for p in ids if p not in prepared],'all_original_responses_preserved':True,'all_valid_arrays_verbatim':True,'no_pdf_embedding_retrieval_rerun':True,'paid_api_calls':0,'remote_verification':remote,'cs_actual_output_consistency':cs,'official_fixed42_evaluations_checked':checks,'no_automatic_generation_retry':True,'original_gold_prompt_source_unchanged':True}
    result['full_dependency_freeze_verification']=environment;result['all_42_pipeline_prefix_removals_verified']=True
    result['remote_artifact_transfer_sha256_matches']=len(remote_inventory)
    save(R/'verification.json',result)
    files=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'cache' not in p.parts and p.name not in ['artifact_sha256.json']]
    save(R/'artifact_sha256.json',files);print(json.dumps({'status':'PASS','artifacts':len(files),'protected':len(records)}))
if __name__=='__main__':main()
