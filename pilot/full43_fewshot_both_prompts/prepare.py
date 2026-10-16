from common import *
import subprocess,collections
from concurrent.futures import ThreadPoolExecutor

def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0'
    assert not (RUN/'input_manifest.json').exists(),'Already prepared; do not overwrite frozen input'
    prior=read(PREVIOUS/'manifest.json');gold=read(prior['gold_path']);prompts=read(REPO/'prompts.json')
    assert len(prior['papers'])==len(gold)==43 and sum(len(x['TDMs']) for x in gold.values())==295
    assert read(PREVIOUS/'verification.json')['coverage']['completed_papers']==43
    oldfreeze=read(PREVIOUS/'freeze_before.json');dirs={}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for root,expected in oldfreeze['directories'].items():
            paths=[str(p) for p in Path(root).rglob('*') if p.is_file()];assert set(paths)==set(expected)
            actual=dict(zip(paths,pool.map(sha,paths)));assert actual==expected,root;dirs[root]=actual
            print('FROZEN',Path(root).name,len(paths),flush=True)
        paths=[str(p) for p in PREVIOUS.rglob('*') if p.is_file()];dirs[str(PREVIOUS)]=dict(zip(paths,pool.map(sha,paths)))
    for rel,h in read(PREVIOUS/'artifact_sha256.json').items():assert dirs[str(PREVIOUS)][str(PREVIOUS/rel)]==h
    assert all(sha(p)==h for p,h in oldfreeze['sources_gold'].items())
    deps={d.metadata['Name']:d.version for d in importlib.metadata.distributions()};assert deps==oldfreeze['dependencies']
    commit=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'rev-parse','HEAD'],text=True).strip();assert commit=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    status=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'status','--porcelain'],text=True)
    immutable(RUN/'freeze_before.json',dict(oldfreeze,directories=dirs,dependencies=deps,git_status=status,git_commit=commit,epoch=time.time()))
    labels={k:set() for k in ('Task','Dataset','Metric')}
    for value in gold.values():
        for r in value['TDMs']:
            for k in labels:labels[k].add(r[k])
    assert [len(v) for v in labels.values()]==[23,71,26]
    assert {k:str(v) for k,v in labels.items()}==read(PREVIOUS/'candidate_sets.json')
    immutable(RUN/'candidate_sets.json',{k:str(v) for k,v in labels.items()})
    from prompting import TDMPrompt,NormalizationPrompt
    extraction_template=TDMPrompt(prompts['few-shot-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    raw={};papers=[]
    for row in prior['papers']:
        p=row['id'];ex=Path(row['extraction_dir']);value=read(ex/'output.json');assert list(value)==[p]
        assert read(ex/'summary.json')['status']=='COMPLETE' and validate(value[p]['output'])['schema_valid']
        docs=value[p]['source_documents'];assert digest(docs)==row['source_documents_sha256']
        messages=wire(extraction_template.format_messages(question=prompts['query'],context='\n\n'.join(x['content'] for x in docs)))
        request=read(ex/'api_calls/0001/request.json');state=read(ex/'api_calls/0001/state.json')
        assert request['messages']==messages and state['status']=='COMPLETE' and state['finish_reason']=='stop'
        assert state['raw_answer']==value[p]['output'];assert state['returned_model']==MODEL
        assert messages[0]['content'].count('[Start of the Example]')==1
        assert read(Path(row['normalization_dir'])/'candidate_sets.json')=={k:str(v) for k,v in labels.items()}
        raw.update(value);new=RUN/'papers'/Path(p).stem/'normalization_input/normalization'
        papers.append({'id':p,'gold_count':len(gold[p]['TDMs']),'records':validate(value[p]['output'])['records'],'source_documents_sha256':digest(docs),'source_documents_count':len(docs),'extraction_dir':str(ex),'extraction_file':str(ex/'output.json'),'extraction_sha256':sha(ex/'output.json'),'extraction_request_sha256':sha(ex/'api_calls/0001/request.json'),'previous_normalization_dir':row['normalization_dir'],'normalization_dir':str(new),'calls_dir':str(RUN/'normalization/api_calls'/Path(p).stem),'status':'PENDING'})
    assert set(raw)==set(gold) and sum(x['records'] for x in papers)==293
    assert raw==read(PREVIOUS/'fewshot_output.json')==read(PREVIOUS/'merged/output.json')
    immutable(RUN/'input/output.json',raw);immutable(RUN/'merged/output.json',raw)
    m={'papers':papers,'gold_path':prior['gold_path'],'gold_sha256':sha(prior['gold_path']),'gold_leaderboards_path':prior['gold_leaderboards_path'],'input_origin':'Per-paper extraction directories resolved from full43_fewshot/manifest.json; equal to both historical merged files','frozen_raw_file':str(RUN/'input/output.json'),'frozen_raw_sha256':sha(RUN/'input/output.json'),'scope':'43 papers, 293 raw Few-shot predictions, 295 Gold; Extraction reused, no requests'}
    immutable(RUN/'input_manifest.json',m)
    from normalize import labels_and_plan
    counts=collections.Counter();exact=collections.Counter();estimate_total=0;unique=set();example=None
    for row in papers:
        rr=json.loads(raw[row['id']]['output']);ll,plan=labels_and_plan(row['id'],rr)
        previous_plan=read(Path(row['previous_normalization_dir'])/'request_plan.json')
        assert len(plan)==len(previous_plan)
        for a,b in zip(plan,previous_plan):
            assert all(a[k]==b[k] for k in ('paper','record','field','original','candidate_serialized','candidate_sha256'))
            assert a['messages'][1]==b['messages'][1] and a['messages'][0]!=b['messages'][0]
            counts[a['field']]+=1;estimate_total+=a['estimated_prompt_tokens'];unique.add((a['field'],a['original']))
        for r in rr:
            for k in ll:exact[k]+=r[k] in ll[k]
        row['expected_normalization_requests']=len(plan)
        immutable(Path(row['normalization_dir'])/'request_plan.json',plan)
        if plan and example is None:example=plan[0]
    save(RUN/'input_manifest.json',m)
    raw_system=prompts[NORMALIZATION_KEY];rendered=example['messages'][0]['content']
    assert rendered==raw_system.replace('{{','{').replace('}}','}')
    assert rendered.count('[Start of the Example]')==rendered.count('[End of the Example]')==1
    assert rendered.count('Item List:')==3 and example['messages'][1]['content'].count('Item list:')==1
    (RUN/'normalization_prompt_original.txt').write_text(raw_system,encoding='utf-8')
    immutable(RUN/'rendered_request_example.json',{'model':MODEL,'temperature':0,'seed':0,'stream':False,'n':1,'messages':example['messages']})
    immutable(RUN/'prompt_hash.json',{'source_file':str(REPO/'prompts.json'),'source_sha256':sha(REPO/'prompts.json'),'extraction_prompt_key':'few-shot-extraction-system-prompt','normalization_prompt_key':NORMALIZATION_KEY,'normalization_raw_sha256':hashlib.sha256(raw_system.encode()).hexdigest(),'normalization_rendered_system_sha256':hashlib.sha256(rendered.encode()).hexdigest(),'is_few_shot':True,'example_count':3,'example_inputs':['Pos tagging','PTB','F1 score '],'candidate_examples_static_unchanged':True,'braces_rendered_once':True,'extraction_prompt_verification_papers':43})
    immutable(RUN/'precheck.json',{'papers':43,'records':293,'gold':295,'candidate_counts':{k:len(v) for k,v in labels.items()},'exact_fields':dict(exact),'exact_fields_total':sum(exact.values()),'llm_fields':dict(counts),'expected_requests':sum(counts.values()),'unique_nonexact_field_values':len(unique),'cache_used':False,'estimated_prompt_tokens_total':estimate_total,'candidate_order_identical_to_B':True,'all_normalization_human_messages_identical_to_B':True,'all_system_messages_changed_to_official_fewshot':True,'extraction_requests':0})
    immutable(RUN/'config.json',{'model':MODEL,'base_url':URL,'temperature':0,'seed':0,'stream':False,'n':1,'is_few_shot':True,'model_type':'gpt4-turbo-128k','extraction_prompt_key':'few-shot-extraction-system-prompt','normalization_prompt_key':NORMALIZATION_KEY,'output_limits':'omitted from HTTP payload','sdk_retries':0,'python_hash_seed':'0','worker_count':1,'source_extraction_run':str(PREVIOUS),'zero_shot_reference':str(BASE),'git_commit':commit,'python_version':sys.version,'python_executable':sys.executable,'normalization':'Unmodified official main, full candidates, exact membership, no cache or postprocessing','timeout_seconds':{'connect':20,'read':180,'write':30,'pool':20},'reproduction_differences':['GPT-4.1 fixed snapshot replaces GPT-4 Turbo','Original default max_new_tokens=15 omitted under user-authorized configuration','Frozen local Gold and same 27 supplied leaderboard JSON; data hashes recorded'],'new_extraction_requests':0})
    print('PRECHECK',json.dumps(read(RUN/'precheck.json')),flush=True)

if __name__=='__main__':main()
