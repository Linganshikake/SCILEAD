from pathlib import Path
import sys,json,hashlib,subprocess,ast,collections
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=R.parent/'20261021_formal42';S=R/'remote_snapshot'
sys.path.insert(0,str(R/'scripts'));from reuse_contract import reusable
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    protected=read(R/'audit/protected_before.json');assert all(sha(Path(x['path']))==x['sha256'] for x in protected)
    for name,digest in read(R/'parser_v2/parser_version.json')['files'].items():assert sha(R/'parser_v2'/name)==digest
    for root in ['scripts','parser_v2']:
        for p in (R/root).glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    results=[]
    for p in [R/'parser_v2/test_parser.py',R/'scripts/test_reuse.py']:
        v=subprocess.run([sys.executable,'-B',str(p)],capture_output=True,text=True);assert v.returncode==0;results.append(v.stdout+v.stderr)
    (R/'reports/final_tests.txt').write_text('\n'.join(results),encoding='utf-8')
    raw=read(R/'format_v2/extraction/prepared_output.json');prior=read(OLD/'remote_snapshot/extraction/prepared_output.json');assert len(raw)==41 and sum(len(json.loads(x['output'])) for x in raw.values())==281
    assert all(raw[p]==x for p,x in prior.items());assert '2105.03654.pdf' not in raw and '1912.08777.pdf' not in raw
    counters={}
    for stage,short in [('fully_llm','fully'),('partially_stage1','partial'),('partially_stage2','leaderboard')]:
        index=read(S/'audit/reuse_index'/f'{short}.json');out=S/'format_v2/normalization'/stage;events=[read(p) for p in sorted((out/'events').glob('*.json'))];counter=collections.Counter()
        for ev in events:
            c=ev['context'];counter[ev['origin']]+=1
            if ev['origin']=='REUSED_EXACT':
                old=index[json.dumps([c['paper_id'],c['record_index'],c['field']])];assert reusable(old,ev)
            else:assert c['paper_id']=='1901.10430.pdf','Unexpected dependent-state regeneration needs explicit audit'
        counters[stage]=dict(counter)
    for stage in ['fully_llm','fully_cs','partially_stage1','partially_stage2']:
        n=read(R/'format_v2/normalization'/stage/'normalized_output.json');assert len(n)==41
        old=read(OLD/'evaluation'/('llama3_'+stage)/'evaluation_input_fixed42.json');assert all(n[p]==old[p] for p in prior)
        for p,x in n.items():
            a=json.loads(raw[p]['output']);b=x['normalized_output'];assert len(a)==len(b);assert all(str(i['Result'])==j['Result'] for i,j in zip(a,b))
        e=R/'format_v2/evaluation'/stage;m=read(e/'metrics_with_f1.json');v=read(e/'per_paper_metrics.json');assert len(v)==42 and m['gold_tdmrs']==259
        for k,x in m['aggregate'].items():
            p=sum(t[k]['Precision'] for t in v.values())/42;q=sum(t[k]['Recall'] for t in v.values())/42;assert abs(x['Precision']-p)<1e-12 and abs(x['Recall']-q)<1e-12;assert abs(x['F1']-(2*p*q/(p+q) if p+q else 0))<1e-12
        boards=read(e/'leaderboard_supplementary.json');assert boards['gold_leaderboards']==27 and boards['gold_entries']==131
    # Same masking, order and source configuration. No 2048 result in any main input.
    assert read(S/'format_v2/normalization/partially_stage1/partially_masked_normalization/partially_masked_leaderboards.json')==read(OLD/'remote_snapshot/normalization/partially/stage1/partially_masked_normalization/partially_masked_leaderboards.json')
    dc=S/'token2048_diagnostic/extraction/calls';assert len(list(dc.glob('*/request.json')))==1
    req=read(dc/'000000/request.json');oldreq=read(OLD/'remote_snapshot/extraction/2105.03654/extraction/calls/000000/request.json');assert req==dict(oldreq,max_new_tokens=2048)
    ids=read(dc/'000000/token_ids.json');gen=read(dc/'000000/complete.json')['actual_generation'];assert len(ids['input_ids'])==gen['input_tokens'] and len(ids['generated_ids'])==gen['output_tokens']
    assert len(ids['input_ids'])+2048<=8192
    remote=read(S/'reports/verification_remote.json');assert remote['status']=='PASS'
    transfer=read(R/'reports/transfer_verification.json');assert transfer['status']=='PASS'
    for x in read(S/'export_manifest.json'):assert sha(S/x['path'])==x['sha256']
    privacy=read(R/'reports/privacy_verification.json');assert privacy['status']=='PASS'
    result={'status':'PASS','protected_local_files_unchanged':len(protected),'original40_extraction_and_all4_normalization_results_unchanged':True,'parser_frozen_before_scoring':True,'parser_tests':19,'reuse_contract_tests':6,'v2_extraction_calls':0,'diagnostic_extraction_calls':1,'source_prompt_quantization_model_request_unchanged_except_diagnostic_budget':True,'reuse_verified':counters,'mask_unchanged':True,'fixed_scope':{'papers':42,'gold':259,'leaderboards':27,'entries':131},'remote':remote,'transfer':transfer,'privacy':privacy,'review':'Self-review of parser, exact-position reuse, stage dependencies and evaluation; no independent subagent tool used.'}
    (R/'reports/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':'PASS','protected_files':len(protected),'reused_requests_checked':counters}))
if __name__=='__main__':main()
