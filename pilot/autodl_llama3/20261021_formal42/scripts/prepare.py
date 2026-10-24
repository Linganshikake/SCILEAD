from pathlib import Path
import json,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[1];D=R.parent/'20261021_diagnostic'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'approval.json').exists(),'Preparation is single-use'
for rel in ['scripts/format_candidate.py','scripts/test_format_candidate.py','generation_config.json','preflight.json','integrity_before.json','config/remote_expected_hashes.json']:
    p=R/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(D/rel,p)
scope=read(D/'config/scope42.json');scope['formal_scope_approved']=True;save(R/'config/scope42.json',scope)
for name in ['gold_subset.json','gold_leaderboards_subset.json']:
    p=R/'evaluation'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(D/'evaluation/gpt41_reference_scope42'/name,p)
save(R/'approval.json',{'approved_at_recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'format_response':'批准此格式规则','scope_response':'批准范围和评价口径并启动','parser_sha256':sha(R/'scripts/format_candidate.py'),'diagnostic_root':str(D),'eligible_papers':42,'gold_tdmrs':259,'leaderboards':27,'leaderboard_entries':131,'new_extraction_calls':38,'reused_extractions':4,'fixed_denominator_failures_empty_in_evaluation_only':True,'paid_api_allowed':False,'stages':['extraction','fully_llm','fully_cs','partially_stage1','partially_stage2','evaluation']})
index=read(D/'extraction/output_index.json');reuse={}
for x in index:
    pid=x['paper_id'];remote='/root/autodl-tmp/scilead/runs/smoke/llama3-20261021/extraction' if x['historical'] else '/root/autodl-tmp/scilead/runs/llama3/20261021_diagnostic/extraction/'+pid.removesuffix('.pdf')+'/extraction'
    reuse[pid]={'remote_extraction':remote,'output_sha256':x['source_output_sha256'],'response_sha256':x['response_sha256'],'prompt_sha256':x['prompt_sha256']}
save(R/'config/reuse.json',reuse)
audit={x['paper_id']:x for x in read(D/'preflight.json')['audit']}
queue=[audit[p] for p in scope['eligible_ids'] if p not in reuse];assert len(queue)==38;save(R/'config/extraction_queue.json',queue)
gold=read(R/'evaluation/gold_subset.json')
save(R/'experiment_manifest.json',{'scope':scope,'papers':[{'paper_id':p,'gold_tdmrs':len(gold[p]['TDMs']),'generation_status':'PENDING','parse_status':'PENDING','normalization_status':'PENDING','evaluation_status':'PENDING','reused_generation':p in reuse} for p in scope['eligible_ids']]+[{'paper_id':'1912.08777.pdf','gold_tdmrs':36,'generation_status':'BLOCKED','reason':'55324 input tokens exceeds native8192; no input modification'}]})
save(R/'protected_diagnostics.json',[{'path':str(p),'sha256':sha(p)} for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts])
(R/'plan.md').write_text('# Approved Llama-3 formal42\n\n- [x] Format v1 and 42/259 scope approved\n- [x] Fixed 38-call queue and four reuse sources\n- [ ] Extraction\n- [ ] Fully LLM\n- [ ] CS\n- [ ] Partially stages1/2\n- [ ] Official tuple / leaderboard evaluation\n- [ ] Paired GPT42 comparison, verification and report\n',encoding='utf-8')
print(json.dumps({'prepared':str(R),'new_calls':len(queue),'reused':len(reuse)}))
