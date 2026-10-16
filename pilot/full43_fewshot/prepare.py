from common import *
import subprocess
from concurrent.futures import ThreadPoolExecutor
def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0'
    assert not (RUN/'manifest.json').exists(),'Already prepared: never overwrite'
    manifest=read(BASE/'manifest.json');gold=read(manifest['gold_path']);raw=read(BASE/'merged/output.json');prompts=read(REPO/'prompts.json')
    assert len(raw)==len(gold)==43 and set(raw)==set(gold) and sum(len(v['TDMs']) for v in gold.values())==295
    assert sum(len(json.loads(v['output'])) for v in raw.values())==284
    labels={k:set() for k in ('Task','Dataset','Metric')}
    for p in gold.values():
        for r in p['TDMs']:
            for k in labels:labels[k].add(r[k])
    assert [len(x) for x in labels.values()]==[23,71,26]
    commit=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'rev-parse','HEAD'],text=True).strip();assert commit=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    roots=[RUN.parent/x for x in ('full43_uncapped','full43_cs','full43_partially','full43_cold_start','leaderboard_eval_full43_uncapped')]
    dirs={}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for root in roots:
            files=[str(p) for p in root.rglob('*') if p.is_file()]
            dirs[str(root)]=dict(zip(files,pool.map(sha,files)));print('FROZEN',root.name,len(dirs[str(root)]),flush=True)
    sources={str(REPO/p):sha(REPO/p) for p in ('prompts.json','prompting.py','pdf_loader.py','retriever.py','tdm_extraction.py','tdm_llm_normalization.py','tdm_eval.py','leaderboard_eval.py','utils.py','model_init.py','requirements.txt') if (REPO/p).exists()}
    board=Path(manifest['gold_path']).parent/'leaderboards.json';assert len(read(board))==27
    sources.update({manifest['gold_path']:sha(manifest['gold_path']),str(board):sha(board)})
    save(RUN/'freeze_before.json',{'directories':dirs,'sources_gold':sources,'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'git_commit':commit,'git_status':subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'status','--porcelain'],text=True),'epoch':time.time()})
    from prompting import TDMPrompt
    few=TDMPrompt(prompts['few-shot-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    zero=TDMPrompt(prompts['tdm-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    system=few.format_messages(question='',context='')[0].content
    example=system.split('[Start of the Example]\n',1)[1].split('[End of the Example]',1)[0]
    demo_input,demo_output=example.rsplit('Output json: ',1);demo_rows=json.loads(demo_output.strip());assert len(demo_rows)==18
    (RUN/'author_example_input.txt').write_text(demo_input,encoding='utf-8');(RUN/'author_example_output.txt').write_text(demo_output,encoding='utf-8');(RUN/'fewshot_system_prompt.txt').write_text(prompts['few-shot-extraction-system-prompt'],encoding='utf-8')
    save(RUN/'prompt_hash.json',{'file':str(REPO/'prompts.json'),'file_sha256':sha(REPO/'prompts.json'),'key':'few-shot-extraction-system-prompt','raw_template_sha256':hashlib.sha256(prompts['few-shot-extraction-system-prompt'].encode()).hexdigest(),'rendered_system_sha256':hashlib.sha256(system.encode()).hexdigest(),'example_input_sha256':sha(RUN/'author_example_input.txt'),'example_output_sha256':sha(RUN/'author_example_output.txt'),'example_records':18,'example_model':'MATCHSUM','example_outside_dataset_source':'SCILEAD Section 6.3, local reference/page-08.txt states held-out paper','author_anomalies_preserved':['ROGUE spelling','Final three demonstration outputs say WikiHow although input table places these scores under Multi-News'],'example_placement':'embedded once in System, not an extra assistant/user pair'})
    records=[]
    for row in manifest['papers']:
        paper=row['id'];docs=raw[paper]['source_documents'];context='\n\n'.join(d['content'] for d in docs)
        messages=wire(few.format_messages(question=prompts['query'],context=context));old=wire(zero.format_messages(question=prompts['query'],context=context))
        d=Path(row['extraction_dir']);fs=sorted((d/'api_calls').glob('*/request.json')) or [d/'request_payload.json'];payload=read(fs[0]);assert payload['messages']==old,paper
        assert messages[1]==old[1] and messages[0]['content']==system
        assert read(Path(row['normalization_dir'])/'candidate_sets.json')=={k:str(v) for k,v in labels.items()},paper
        out=RUN/'papers'/Path(paper).stem
        save(out/'evidence.json',{'paper':paper,'source_documents':docs})
        plan=[{'paper':paper,'record':0,'field':'Extraction','candidate_sha256':None,'messages':messages,'prompt_sha256':digest(messages),'estimated_prompt_tokens':estimate(messages)}]
        save(out/'extraction/request_plan.json',plan)
        records.append({'id':paper,'gold_count':len(gold[paper]['TDMs']),'source_documents_sha256':digest(docs),'evidence_count':len(docs),'evidence_path':str(out/'evidence.json'),'baseline_extraction_dir':row['extraction_dir'],'baseline_normalization_dir':row['normalization_dir'],'extraction_dir':str(out/'extraction'),'normalization_dir':str(out/'normalization_input/normalization'),'estimated_input_tokens':plan[0]['estimated_prompt_tokens'],'status':'PENDING'})
    save(RUN/'manifest.json',{'papers':records,'gold_path':manifest['gold_path'],'gold_sha256':sha(manifest['gold_path']),'gold_leaderboards_path':str(board),'scope':'43 papers / 295 Gold; 284 historical predictions, not evidence/request count'})
    save(RUN/'config.json',{'model':MODEL,'base_url':URL,'temperature':0,'seed':0,'stream':False,'output_limit_policy':'all client output limit parameters omitted','retries':0,'input_limit':None,'retrieval':'frozen source_documents, no parsing/indexing/retrieval execution','extraction_prompt':'few-shot-extraction-system-prompt','normalization_prompt':'normalization-system-prompt','normalization':'Fully predefined LLM; original main; no cache','candidate_counts':{k:len(v) for k,v in labels.items()},'python_hash_seed':'0','candidate_order_identical_to_all_43_baseline_papers':True,'source_run':str(BASE),'git_commit':commit,'normalization_dispatch_note':'Separate input config is_few_shot=False avoids upstream coupling to few-shot normalization; only extraction prompt varies.'})
    save(RUN/'candidate_sets.json',{k:str(v) for k,v in labels.items()});print('PREPARED',len(records),'max_input',max(r['estimated_input_tokens'] for r in records))
if __name__=='__main__':main()
