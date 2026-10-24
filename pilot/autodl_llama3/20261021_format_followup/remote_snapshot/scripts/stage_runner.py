"""Unmodified author main with exact per-position reuse and observable dynamic state."""
from pathlib import Path
import sys,os,json,inspect,hashlib,time,copy
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead');OLD=ROOT/'runs/llama3/20261021_formal42'
sys.path.insert(0,str(ROOT/'adapters'));import run_llama as a
from reuse_contract import reusable
read=a.read;save=a.save
PATHS={'fully':'normalization/fully_llm','partial':'normalization/partially/stage1','leaderboard':'normalization/partially/stage2'}
RELS={'fully':'normalization/normalized_output.json','partial':'partially_masked_normalization/partially_masked_normalized_output.json','leaderboard':'leaderboard_normalized_output.json'}
NEW={'fully':'fully_llm','partial':'partially_stage1','leaderboard':'partially_stage2'}
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False).encode()).hexdigest()
def context():
    f=inspect.currentframe()
    while f:
        if Path(f.f_code.co_filename).name in ['tdm_llm_normalization.py','tdm_llm_masked_normalization.py','leaderboard_llm_normalization.py'] and f.f_code.co_name=='main':
            l=f.f_locals;stage2='leaderboard_tdm_set' in l
            state={k:{'order':list(v),'serialized':str(v)} for k,v in l['labels_dict'].items()} if not stage2 else {'leaderboards':{'order':list(l['leaderboard_tdm_set']),'serialized':str(l['leaderboard_tdm_set'])}}
            v={'paper_id':l['paper'],'record_index':len(l['normalized_tdms']),'field':'TDM' if stage2 else l['key'],'source_row':dict(l['tdm']),'partial_row':{} if stage2 else dict(l['normalized_tdm']),'candidate_state':state,'author_module':Path(f.f_code.co_filename).name}
            return copy.deepcopy(v)
        f=f.f_back
    raise RuntimeError('AUTHOR_CONTEXT_NOT_FOUND')
def key(c):return json.dumps([c['paper_id'],c['record_index'],c['field']])
def expected(prompt,config,budget):
    return {'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'max_new_tokens':budget,'seed':0,'model_type':config['model_type'],'model_path':config['model_path'],'model_revision':config['model_revision'],'do_sample':False,'output_wrapper_sha256':hashlib.sha256((ROOT/'adapters/author_hf_pipeline.py').read_bytes()).hexdigest()}
def main():
    mode,stage=sys.argv[1:3];assert mode in ['index','v2','diagnostic'];assert stage in PATHS;assert os.environ['PYTHONHASHSEED']=='0'
    import utils
    author_init=utils.llm_init_langchain
    t=time.monotonic();config=read(OLD/'extraction/config.json');budget=100 if stage=='leaderboard' else 15;original=a.factory
    oldroot=OLD/PATHS[stage]
    if mode=='index':out=R/'audit/official_replay'/stage;inp=OLD/'extraction/prepared_output.json' if stage!='leaderboard' else OLD/PATHS['partial']/RELS['partial']
    else:
        base=R/('format_v2' if mode=='v2' else 'token2048_diagnostic');out=base/'normalization'/NEW[stage]
        inp=base/'extraction/prepared_output.json' if stage!='leaderboard' else base/'normalization/partially_stage1'/RELS['partial']
    if (out/'done.json').exists():print('SKIP_DONE',mode,stage);return
    index_path=R/'audit/reuse_index'/f'{stage}.json';prior=read(index_path) if mode!='index' else {};oldcalls=sorted((oldroot/'calls').glob('*/request.json'));events=[];index={}
    from langchain_core.language_models.llms import LLM
    from langchain_core.pydantic_v1 import PrivateAttr
    class ReplayOrGenerate(LLM):
        _inner=PrivateAttr(default=None)
        @property
        def _llm_type(self):return 'exact-position-state-author-replay'
        def _call(self,prompt,stop=None,run_manager=None,**kw):
            c=context();request=expected(prompt,config,budget);current={'context':c,'request':request};j=len(events);ref=None;reason=[]
            if mode=='index':
                p=oldcalls[j];assert read(p)==request,'OLD_REQUEST_REPLAY_MISMATCH';ref=p.parent
            elif key(c) in prior:
                previous=prior[key(c)]
                if reusable(previous,current):ref=Path(previous['call_directory'])
                else:reason=[k for k in current if current[k]!=previous[k]]
            else:reason=['NEW_POSITION']
            if ref:
                answer=(ref/'response.txt').read_text();assert hashlib.sha256(answer.encode()).hexdigest()==read(ref/'complete.json')['response_sha256'];origin='OFFLINE_REPLAY' if mode=='index' else 'REUSED_EXACT'
            else:
                if self._inner is None:
                    patched=utils.llm_init_langchain
                    try:
                        utils.llm_init_langchain=author_init;self._inner=original(config,budget,out/'new_calls')
                    finally:utils.llm_init_langchain=patched
                answer=self._inner.invoke(prompt,stop=stop,**kw);origin='NEW_GENERATION'
            e={**current,'origin':origin,'old_call_directory':str(ref) if ref else None,'mismatch':reason,'raw_answer':answer,'official_answer_after_slice':answer[2:],'event_index':j}
            save(out/'events'/f'{j:06d}.json',e);events.append(e)
            if mode=='index':
                assert key(c) not in index;index[key(c)]={**current,'call_directory':str(ref)}
            if j%25==0:print('EVENT',mode,stage,j,origin,c['paper_id'],flush=True)
            return answer
    llm=ReplayOrGenerate();a.factory=lambda *args,**kwargs:llm
    # Resume replays official state from the beginning; only persisted exact new-call checkpoints are read.
    if (out/'stage_complete.json').exists():raise RuntimeError('STAGE_FINISHED_WITHOUT_SUMMARY_INSPECT_FIRST')
    a.official_stage(stage,config,OLD/'extraction/config.json',inp,out)
    result=read(out/RELS[stage])
    if mode=='index':assert len(events)==len(oldcalls) and result==read(oldroot/RELS[stage]);save(index_path,index)
    if mode=='v2' and stage=='fully':
        before=read(oldroot/RELS[stage]);assert all(result[p]==v for p,v in before.items())
    save(out/'normalized_output.json',result)
    save(out/'done.json',{'status':'COMPLETE','mode':mode,'stage':stage,'events':len(events),'new_generations':sum(e['origin']=='NEW_GENERATION' for e in events),'reused_requests':sum(e['origin']=='REUSED_EXACT' for e in events),'offline_replay_requests':sum(e['origin']=='OFFLINE_REPLAY' for e in events),'papers':len(result),'records':sum(len(x['normalized_output']) for x in result.values()),'seconds':time.monotonic()-t})
    print(json.dumps(read(out/'done.json')),flush=True)
if __name__=='__main__':main()
