"""Freeze existing evidence and original scenario scopes; no remote requests."""
import inspect,subprocess,concurrent.futures
import variant_runtime as v
from variant_runtime import *

def main():
    setup();assert not (TOP/'experiment_manifest.json').exists(),'Preparation already frozen'
    source=BASE/'merged/output.json';raw=read(source);old=read(PILOT/'full43_uncapped/merged/output.json')
    assert len(raw)==43 and set(raw)==set(old)
    copied={p:raw[p] for p in old};assert all(copied[p]==raw[p] for p in copied)
    assert sum(len(json.loads(x['output'])) for x in raw.values())==335
    assert all(set(r)=={'Task','Dataset','Metric','Result'} and all(isinstance(x,str) for x in r.values()) for p in raw.values() for r in json.loads(p['output']))
    save(TOP/'inputs/output.json',copied);save(TOP/'merged/output.json',copied)
    oldcfg=read(PILOT/'full43_partially/config.json');goldpath=Path(oldcfg['gold_path']);boardpath=Path(oldcfg['leaderboards_path'])
    gold=read(goldpath);boards=read(boardpath)
    assert len(gold)==43 and sum(len(x['TDMs']) for x in gold.values())==295 and len(boards)==27
    protected={};protected_paths=[]
    for directory in (BASE,PILOT/'gpt56_sol_fully/20261024_A2_formal43',PILOT/'full43_uncapped',PILOT/'full43_cs',PILOT/'full43_partially',PILOT/'full43_cold_start'):
        protected_paths.extend(p for p in directory.rglob('*') if p.is_file())
    critical=[p for p in REPO.iterdir() if p.is_file() and p.suffix in ('.py','.json','.md','.txt')]+[goldpath,boardpath,A1/'run_trial.py',source,PILOT/'full43_partially/engine.py',PILOT/'full43_cold_start/engine.py']
    protected_paths.extend(critical)
    if (TOP/'protected_hashes.json').exists():
        protected=read(TOP/'protected_hashes.json')
        assert set(protected)==set(map(str,protected_paths)),'FROZEN_FILE_LIST_CHANGED'
        assert all(sha(p)==protected[str(p)] for p in critical),'CRITICAL_FROZEN_SOURCE_CHANGED'
        print(json.dumps({'reuse_existing_pre_call_freeze':len(protected),'critical_hashes_verified':len(critical)}),flush=True)
    else:
        print(json.dumps({'hashing_files':len(protected_paths),'workers':8}),flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for i,(p,h) in enumerate(pool.map(lambda p:(str(p),sha(p)),protected_paths),1):
                protected[p]=h
                if i%5000==0:print(json.dumps({'hashed':i,'total':len(protected_paths)}),flush=True)
    save(TOP/'protected_hashes.json',protected)
    save(TOP/'critical_paths.json',[str(p) for p in critical])
    save(TOP/'reproducibility/dependency_versions.json',{d.metadata['Name']:d.version for d in importlib.metadata.distributions()})
    import tdm_llm_masked_normalization as original
    labels=original.sample_tdms(boards,gold,0,TOP.as_posix()+'/',False,'masking/')
    save(TOP/'masking/initial_labels.json',labels_state(labels));save(TOP/'references/cold_initial_labels.json',labels_state({k:set() for k in ('Task','Dataset','Metric')}))
    assert read(TOP/'masking/initial_labels.json')==read(PILOT/'full43_partially/masking/initial_labels.json')
    assert sha(TOP/'masking/partially_masked_leaderboards.json')==sha(PILOT/'full43_partially/masking/partially_masked_leaderboards.json')
    for name,seed in [('partially',None),('cold_default',None),('cold_0','0'),('cold_42','42')]:
        cold=name.startswith('cold_');order=list(copied)
        if cold and seed is not None:random.seed(seed);order=random.sample(order,len(order))
        legacy=PILOT/'full43_cold_start'/('order_'+name[5:])/'paper_order.json' if cold else PILOT/'full43_partially/paper_order.json'
        assert order==read(legacy)['papers']
        conf={'run_id':name,'model':MODEL,'generation':{k:x for k,x in frozen.payload([]).items() if k!='messages'},'api_base':URL,'cold_start':cold,'cold_start_seed':seed,'cold_start_seed_type':type(seed).__name__,'masking_seed':0,'python_hash_seed':0,'gold_path':str(goldpath),'leaderboards_path':str(boardpath),'input_path':str(TOP/'inputs/output.json'),'input_sha256':sha(TOP/'inputs/output.json'),'paper_order':order,'original_default_output_budgets':{'stage1':15,'stage2':100},'override':'Use same verified GPT56 A2 generation settings in both stages; no legacy GPT4.1 seed/temperature','automatic_retries':0,'semantic_cache':False}
        save(TOP/name/'config.json',conf);save(TOP/name/'official_config.json',{'model_type':'gpt4-turbo-128k','actual_request_model':MODEL});save(TOP/name/'paper_order.json',{'papers':order,'legacy_order_source':str(legacy),'cold_start_seed':seed})
    input_rows=[{'paper_id':p,'records':len(json.loads(raw[p]['output'])),'gold_records':len(gold[p]['TDMs']),'source_documents':len(raw[p]['source_documents']),'per_paper_content_sha256':digest(raw[p]),'source_documents_sha256':digest(raw[p]['source_documents'])} for p in copied]
    save(TOP/'input_manifest.json',input_rows)
    with (TOP/'input_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(input_rows[0]));w.writeheader();w.writerows(input_rows)
    # Reuse complete method/replay test scenarios; adapt only test module imports and output roots.
    for kind in ('partially','cold_start'):
        text=(PILOT/('full43_'+kind)/'test_offline.py').read_text('utf-8')
        prefix="import variant_runtime as v\nfrom variant_runtime import *\nRUN=TOP=Path(__file__).resolve().parent/'reproducibility'/'"+kind+"'\n(RUN/'reproducibility').mkdir(parents=True,exist_ok=True)\nv.RUN_ID='"+('cold_test' if kind=='cold_start' else 'partially_test')+"'"
        text=text.replace('from common import *',prefix).replace('from engine import run_original,SimulatedInterruption','from variant_runtime import run_original,SimulatedInterruption')
        (TOP/('test_original_'+kind+'.py')).write_text(text,encoding='utf-8')
    manifest={'status':'PREPARED','authorized_by':'User: 先做在GPT-5.6-Sol模型下，按原有实验流程的Partially和Cold Start实验，Fully补充+CS','model':MODEL,'papers':43,'gold_records':295,'predictions':335,'source':str(source),'source_sha256':sha(source),'input_paper_reorder_only':list(raw)!=list(copied),'paper_order_reference':str(PILOT/'full43_uncapped/merged/output.json'),'per_paper_content_unchanged':True,'gold_boards':27,'masked_boards':len(read(TOP/'masking/partially_masked_leaderboards.json')),'scenarios':['fully_cs','partially','cold_default','cold_0','cold_42'],'upstream_commit':'8bf74b0a830feb7035c6166dce3394dc344ae532','archive_commit':'b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25','actual_upstream_head':subprocess.check_output(['git','-c','safe.directory='+str(REPO),'-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'generation':{k:x for k,x in frozen.payload([]).items() if k!='messages'},'new_extraction_requests':0,'estimated_normalization_calls':'Approximately 2000–3000 across Partially and 3 Cold Start runs, actual data-dependent; CS 0 model API requests','maximum_method_positions':4*335*4,'no_method_changes':True,'protected_file_count':len(protected),'created_epoch':time.time()}
    save(TOP/'experiment_manifest.json',manifest);save(TOP/'generation_config.json',manifest['generation']);save(TOP/'preparation_verification.json',verify())
    print(json.dumps({'status':'PREPARED','protected_files':len(protected),'papers':43,'records':335,'masked_boards':manifest['masked_boards'],'paper_reorder_only':manifest['input_paper_reorder_only']}),flush=True)

if __name__=='__main__':main()
