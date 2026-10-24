"""Invoke unchanged author main(), adding checkpoint and per-field observations only."""
from pathlib import Path
import sys,json,inspect,time,hashlib
R=Path(__file__).resolve().parents[1];ROOT=Path('/root/autodl-tmp/scilead')
sys.path.insert(0,str(ROOT/'adapters'))
import run_llama as adapter
original_factory=adapter.factory
def audit_factory(config,budget,logdir):
    from langchain_core.language_models.llms import LLM
    from langchain_core.pydantic_v1 import PrivateAttr
    inner=original_factory(config,budget,logdir)
    class AuditLLM(LLM):
        _index=PrivateAttr(default=0)
        @property
        def _llm_type(self):return 'observer-of-unchanged-author-stage'
        def _call(self,prompt,stop=None,run_manager=None,**kwargs):
            i=self._index;self._index+=1;context={}
            frame=inspect.currentframe()
            while frame:
                if Path(frame.f_code.co_filename).name in ['tdm_llm_normalization.py','tdm_llm_masked_normalization.py','leaderboard_llm_normalization.py'] and frame.f_code.co_name=='main':
                    loc=frame.f_locals;key=loc.get('key');context={'paper_id':loc.get('paper'),'original_tdm':dict(loc.get('tdm',{})),'field':key,'original_value':loc.get('tdm',{}).get(key),'author_module':Path(frame.f_code.co_filename).name}
                    if 'labels_dict' in loc:context['candidate_order']=list(loc['labels_dict'][key])
                    else:context['candidate_order']=list(loc.get('leaderboard_tdm_set',set()));context['original_value']=loc.get('model_tuple')
                    break
                frame=frame.f_back
            del frame
            context['call_index']=i;context['prompt_sha256']=hashlib.sha256(prompt.encode()).hexdigest()
            path=logdir/f'{i:06d}'/'field_context.json'
            adapter.save(path,context)
            answer=inner.invoke(prompt,stop=stop,**kwargs);processed=answer[2:]
            context.update(raw_answer=answer,official_answer_after_slice=processed,in_candidates=processed in context['candidate_order'])
            adapter.save(path,context);return answer
    return AuditLLM()
def main():
    stage=sys.argv[1];assert stage in ['fully','partial','leaderboard']
    adapter.factory=audit_factory;config=adapter.read(R/'extraction/config.json');start=time.monotonic()
    if stage=='fully':out=R/'normalization/fully_llm';inp=R/'extraction/prepared_output.json'
    elif stage=='partial':out=R/'normalization/partially/stage1';inp=R/'extraction/prepared_output.json'
    else:out=R/'normalization/partially/stage2';inp=R/'normalization/partially/stage1/partially_masked_normalization/partially_masked_normalized_output.json'
    adapter.official_stage(stage,config,R/'extraction/config.json',inp,out)
    adapter.save(out/'timing.json',{'seconds':time.monotonic()-start,'paid_api_calls':0})
if __name__=='__main__':main()
