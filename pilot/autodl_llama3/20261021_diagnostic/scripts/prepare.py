from pathlib import Path
import json,csv,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[1]
PRE=Path(r'D:\C++\SCILEAD\pilot\autodl_setup\20261021')
REMOTE='/root/autodl-tmp/scilead/runs/llama3/20261021_diagnostic'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    existing=json.loads((R/'experiment_manifest.json').read_text(encoding='utf-8')) if (R/'experiment_manifest.json').exists() else None
    for name in ['scripts','config','references','extraction','diagnostics/candidates','normalization/fully_llm','normalization/fully_cs','normalization/partially','evaluation']:(R/name).mkdir(parents=True,exist_ok=True)
    shutil.copyfile(next(Path(r'C:\Users\Administrator\.codex\attachments\993bbecc-71c1-4315-b863-5d607d4b0480').glob('*.txt')),R/'references/user_request.txt')
    rows=[x for x in csv.DictReader((PRE/'input_length_audit.csv').open(encoding='utf-8')) if x['model_type']=='llama-3-instruct-70b']
    gold=json.loads((PRE/'stage/data/gold/tdm_annotations.json').read_text(encoding='utf-8'))
    info=json.loads((PRE/'model_manifest.json').read_text(encoding='utf-8'))['llama3']
    papers=[]
    for x in rows:
        pid=x['paper_id'];p=PRE/'stage/data/evidence'/(pid+'.json');docs=json.loads(p.read_text(encoding='utf-8'))[pid]
        papers.append({'paper_id':pid,'input_tokens':int(x['input_tokens']),'prompt_sha256':x['prompt_sha256'],'evidence_sha256':sha(p),'evidence_count':len(docs),'tables':sum(d['metadata'].get('type')=='Table' for d in docs),'gold_count_for_scope_only':len(gold[pid]['TDMs']),'eligible':x['overlength']=='False','generation_status':'PENDING' if x['overlength']=='False' else 'BLOCKED','parse_status':'PENDING','normalization_status':'BLOCKED','evaluation_status':'BLOCKED'})
    eligible=[x for x in papers if x['eligible'] and x['paper_id']!='2020.findings-emnlp.378.pdf']
    short=min(eligible,key=lambda x:(x['input_tokens'],x['paper_id']))
    tables=max(eligible,key=lambda x:(x['tables'],-x['input_tokens'],x['paper_id']))
    longest=max(eligible,key=lambda x:(x['input_tokens'],x['paper_id']))
    selected=[{**x,'selection_reason':reason} for x,reason in [(short,'shortest eligible evidence'),(tables,'most Table evidence among eligible'),(longest,'longest eligible evidence; no genuinely near-limit eligible input')]]
    assert len(set(x['paper_id'] for x in selected))==3
    manifest={'created_at':datetime.datetime.now().astimezone().isoformat(),'status':'DIAGNOSTICS_AUTHORIZED_FORMAL_PROTOCOL_PENDING','remote_root':REMOTE,'model_id':info['model_id'],'model_revision':info['revision'],'official_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532','papers':papers,'diagnostic_papers':selected,'selection_uses_gold_answers':False,'max_new_extraction_calls':3,'formal_scope_approval':False,'custom_format_policy_approval':False,'paid_api_calls':0}
    if existing:
        assert [x['paper_id'] for x in existing['diagnostic_papers']]==[x['paper_id'] for x in selected]
        manifest=existing
    save(R/'experiment_manifest.json',manifest)
    # Remote generation queue contains no Gold fields or answers.
    save(R/'config/diagnostic_queue.json',[{k:v for k,v in x.items() if not k.startswith('gold_')} for x in selected])
    cfg={'model_id':info['model_id'],'model_revision':info['revision'],'model_type':info['model_type'],'model_path':'/root/autodl-tmp/scilead/models/llama3','load_in_4bit':True,'device_map':'auto','model_dtype':'bfloat16','quant_type':'fp4 (author default)','compute_dtype':'float32 (author default)','do_sample':False,'seed':0,'extraction_max_new_tokens':1024,'normalization_max_new_tokens':15,'leaderboard_stage2_max_new_tokens':100,'context_limit':8192,'add_special_tokens_in_pipeline':False,'truncation':False,'is_few_shot':False,'paid_api_calls':0}
    save(R/'generation_config.json',cfg)
    critical=[]
    for p in (PRE/'stage/source').iterdir():
        if p.is_file():critical.append(p)
    critical.extend(PRE/'stage/adapters'/n for n in ['run_llama.py','author_hf_pipeline.py','input_audit.py','evaluate.py'])
    critical.extend((PRE/'stage/data').rglob('*.json'))
    critical.extend(p for p in (PRE/'remote_snapshot/runs/smoke/llama3-20261021').rglob('*') if p.is_file())
    for branch in ['full43_uncapped','full43_cs','full43_partially','full43_cold_start']:
        folder=Path(r'D:\C++\SCILEAD\pilot')/branch
        # Explicit frozen inputs/reports, not unrelated historical caches or every request log.
        for rel in ['*.json','*.md','merged/*.json','evaluation/*.json','leaderboard/*.json']:
            critical.extend(p for p in folder.glob(rel) if p.is_file())
    original=json.loads((PRE/'source_integrity.json').read_text(encoding='utf-8'))
    critical.extend(Path(x['path']) for x in original['originals'])
    files=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in dict.fromkeys(critical)]
    save(R/'integrity_before.json',files)
    small={p.relative_to(PRE/'stage').as_posix():sha(p) for p in (PRE/'stage/source').iterdir() if p.is_file()}
    small.update({f'adapters/{n}':sha(PRE/'stage/adapters'/n) for n in ['run_llama.py','author_hf_pipeline.py','input_audit.py','evaluate.py']})
    small.update({p.relative_to(PRE/'stage').as_posix():sha(p) for p in (PRE/'stage/data').rglob('*.json')})
    save(R/'config/remote_expected_hashes.json',small)
    print(json.dumps({'selected':[(x['paper_id'],x['input_tokens'],x['tables']) for x in selected],'eligible':sum(x['eligible'] for x in papers),'gold_eligible':sum(x['gold_count_for_scope_only'] for x in papers if x['eligible']),'integrity_files':len(files)}))
if __name__=='__main__':main()
