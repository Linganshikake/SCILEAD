import collections,inspect,random,shutil,subprocess
from common import *
def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0';assert not (RUN/'freeze_before.json').exists()
    previous=read(CS/'freeze_before.json')
    goldpath=Path(read(CS/'config.json')['gold_path']);lbpath=Path(read(CS/'config.json')['gold_leaderboards_path']);gold=read(goldpath);boards=read(lbpath);raw=read(BASE/'merged/output.json')
    assert len(raw)==len(gold)==43 and sum(len(x['TDMs']) for x in gold.values())==295 and sum(len(json.loads(x['output'])) for x in raw.values())==284 and len(boards)==27
    full={k:{r[k] for x in gold.values() for r in x['TDMs']} for k in ('Task','Dataset','Metric')};assert [len(v) for v in full.values()]==[23,71,26]
    sources={str(p):sha(p) for p in REPO.iterdir() if p.is_file() and p.suffix in ('.py','.json','.md','.txt')};sources.update({str(p):sha(p) for p in (goldpath,lbpath)})
    for p,h in previous['sources_gold'].items():assert sha(p)==h
    for d in (BASE,CS,LB):assert d.is_dir()
    frozen={'directories':{str(d):{str(p):sha(p) for p in d.rglob('*') if p.is_file()} for d in (BASE,CS,LB)},'sources_gold':sources,'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()}}
    save(RUN/'freeze_before.json',frozen)
    (RUN/'work').mkdir(exist_ok=True);shutil.copyfile(BASE/'merged/output.json',RUN/'work/output.json');assert sha(RUN/'work/output.json')==sha(BASE/'merged/output.json')
    commit=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'rev-parse','HEAD'],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip();assert commit=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    import tdm_llm_masked_normalization as original
    captured={}
    def trace(frame,event,arg):
        if frame.f_code is original.sample_tdms.__code__ and event=='return':
            captured.update({k:frame.f_locals[k] for k in ('leaderboard_tasks','task_sampling_pool','masked_tasks','masked_datasets')})
        return trace
    sys.settrace(trace)
    try:labels=original.sample_tdms(boards,gold,0,RUN.as_posix()+'/',False,'masking/')
    finally:sys.settrace(None)
    save(RUN/'masking/task_leaderboard_counts.json',captured['leaderboard_tasks']);save(RUN/'masking/masked_tasks.json',captured['masked_tasks']);save(RUN/'masking/masked_datasets.json',list(captured['masked_datasets']));save(RUN/'masking/initial_labels.json',labels_state(labels))
    save(RUN/'masking/masking_manifest.json',{'seed':0,'seed_type':'int','cold_start':False,'python_hash_seed':0,'sampling_pool':captured['task_sampling_pool'],'sample_size':round(len(captured['leaderboard_tasks'])/3),'masked_leaderboards':len(read(RUN/'masking/partially_masked_leaderboards.json')),'initial_counts':{k:len(v) for k,v in labels.items()},'full_counts':{k:len(v) for k,v in full.items()},'official_sample_tdms_sha256':digest(inspect.getsource(original.sample_tdms))})
    save(RUN/'paper_order.json',{'policy':'frozen_output_key_order','papers':list(raw),'gold_json_key_order':list(gold),'equals_gold_key_order':list(raw)==list(gold),'provenance':'Frozen full43_uncapped merged output: subset5 then subset15 extension then full43 extension. Author historical run order not recoverable from supplied data/README; current Gold JSON key order is recorded but does not prove historical execution order.','record_and_field_orders':{p:[list(r) for r in json.loads(x['output'])] for p,x in raw.items()}})
    conf={'model':MODEL,'base_url':URL,'model_type':'gpt4-turbo-128k','model_type_purpose':'Select original GPT prompt and comparison branches; actual API snapshot is gpt-4.1-2025-04-14','temperature':0,'seed':0,'masking_seed':0,'python_hash_seed':0,'stream':False,'output_limit_parameters':'OMITTED','original_script_default_output_limits':{'stage1':15,'stage2':100},'max_retries':0,'gold_path':str(goldpath),'leaderboards_path':str(lbpath),'input_path':str(RUN/'work/output.json'),'input_sha256':sha(BASE/'merged/output.json'),'commit':commit,'cold_start':False,'paper_order':'frozen_output_key_order','started_epoch':time.time(),'original_api_adapter_source':str(ROOT/'pilot/scripts/scilead_api.py')}
    save(RUN/'config.json',conf);save(RUN/'work/official_config.json',{'model_type':'gpt4-turbo-128k'})
    save(RUN/'reproducibility/dependency_versions.json',frozen['dependencies']);verify();print(json.dumps(read(RUN/'masking/masking_manifest.json'),ensure_ascii=False));print(json.dumps({'masked_tasks':captured['masked_tasks'],'masked_datasets':list(captured['masked_datasets'])},ensure_ascii=False))
if __name__=='__main__':main()
