"""Frozen-evidence Llama adapter. No paid API, PDF, re-retrieval or prediction repair."""
import argparse,hashlib,json,os,random,sys,time,types
from pathlib import Path
ROOT=Path('/root/autodl-tmp/scilead');sys.path.insert(0,str(ROOT/'source'))
os.environ.setdefault('HF_HOME',str(ROOT/'cache/huggingface'))
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2));tmp.replace(p)
def validate(text):
    try:
        rows=json.loads(text)
        valid=isinstance(rows,list) and all(isinstance(x,dict) and set(x)=={'Task','Dataset','Metric','Result'} and all(isinstance(v,str) for v in x.values()) for x in rows)
        return {'valid':valid,'records':len(rows) if isinstance(rows,list) else None}
    except ValueError:return {'valid':False,'records':None,'reason':'JSON_PARSE_FAILED'}
def factory(config,budget,logdir):
    import torch,utils
    from transformers import AutoTokenizer,AutoConfig
    from langchain_core.language_models.llms import LLM
    from langchain_core.pydantic_v1 import PrivateAttr
    tokenizer=AutoTokenizer.from_pretrained(config['model_path'],use_fast=False,legacy=False,padding_side='left',local_files_only=True)
    context_limit=AutoConfig.from_pretrained(config['model_path'],local_files_only=True).max_position_embeddings
    original_init=utils.llm_init_langchain
    class CheckpointLLM(LLM):
        _inner=PrivateAttr(default=None)
        _index=PrivateAttr(default=0)
        @property
        def _llm_type(self):return 'checkpointed-official-huggingface-pipeline'
        def _call(self,prompt,stop=None,run_manager=None,**kwargs):
            idx=self._index;self._index+=1;path=logdir/f'{idx:06d}';path.mkdir(parents=True,exist_ok=True)
            request={'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'max_new_tokens':budget,'seed':0,'model_type':config['model_type'],'model_path':config['model_path'],'model_revision':config.get('model_revision'),'do_sample':False,'output_wrapper_sha256':hashlib.sha256((ROOT/'adapters/author_hf_pipeline.py').read_bytes()).hexdigest()}
            request_path=path/'request.json';complete=path/'complete.json'
            if complete.exists():
                assert read(request_path)==request,'CHECKPOINT_INPUT_MISMATCH'
                response=(path/'response.txt').read_text();assert hashlib.sha256(response.encode()).hexdigest()==read(complete)['response_sha256']
                return response
            if request_path.exists():raise RuntimeError('UNFINISHED_CALL_CHECKPOINT: inspect before any replay')
            n=len(tokenizer(prompt,add_special_tokens=False,truncation=False)['input_ids'])
            if n+budget>context_limit:
                save(path/'blocked_length.json',{'input_tokens':n,'reserved_new_tokens':budget,'context_limit':context_limit});raise RuntimeError('INPUT_LENGTH_BLOCKED')
            save(request_path,request);started=time.monotonic()
            try:
                if self._inner is None:
                    from author_hf_pipeline import HuggingFacePipeline as AuthorHFPipeline
                    wrapper=utils.HuggingFacePipeline
                    load_started=time.monotonic()
                    if torch.cuda.is_available():torch.cuda.reset_peak_memory_stats()
                    try:
                        utils.HuggingFacePipeline=AuthorHFPipeline
                        self._inner=original_init(config,budget,0)
                    finally:utils.HuggingFacePipeline=wrapper
                    load_stats={'seconds':time.monotonic()-load_started}
                    if torch.cuda.is_available():
                        torch.cuda.synchronize()
                        load_stats.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved())
                    model=self._inner.pipeline.model
                    device_map={k:str(v) for k,v in getattr(model,'hf_device_map',{}).items()}
                    if any(v in ('cpu','disk') for v in device_map.values()):raise RuntimeError('UNAPPROVED_OFFLOAD')
                    quant=getattr(model.config,'quantization_config',None)
                    save(logdir/'model_runtime.json',{'device_map':device_map,'dtype':str(model.dtype),'quantization':quant.to_dict() if hasattr(quant,'to_dict') else quant,'generation_config':model.generation_config.to_dict(),'pipeline_forward_params':getattr(self._inner.pipeline,'_forward_params',{}),'attention_implementation':getattr(model.config,'_attn_implementation',None),'pad_token_id':self._inner.pipeline.tokenizer.pad_token_id,'eos_token_id':self._inner.pipeline.tokenizer.eos_token_id,'output_wrapper':'exact author-pinned langchain-community 0.0.20','output_wrapper_sha256':hashlib.sha256((ROOT/'adapters/author_hf_pipeline.py').read_bytes()).hexdigest()})
                    save(logdir/'model_load_usage.json',load_stats)
                pipe=self._inner.pipeline;original_generate=pipe.model.generate;observed={}
                def observed_generate(*a,**kw):
                    ids=kw.get('input_ids',a[0] if a else None);length=ids.shape[-1]
                    if length+budget>context_limit:raise RuntimeError('ACTUAL_PIPELINE_INPUT_LENGTH_BLOCKED')
                    torch.cuda.reset_peak_memory_stats();t=time.monotonic();result=original_generate(*a,**kw);torch.cuda.synchronize()
                    seq=result.sequences if hasattr(result,'sequences') else result
                    save(path/'token_ids.json',{'input_ids':ids[0].tolist(),'generated_ids':seq[0,length:].tolist()})
                    eos=kw.get('eos_token_id',pipe.model.generation_config.eos_token_id);eos=eos if isinstance(eos,list) else [eos]
                    observed.update(input_tokens=length,output_tokens=int(seq.shape[-1]-length),generation_seconds=time.monotonic()-t,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),finish_reason='eos' if int(seq[0,-1]) in eos else 'length_or_other',last_token_id=int(seq[0,-1]))
                    return result
                pipe.model.generate=observed_generate
                class RecordingPipeline:
                    def __getattr__(self,name):return getattr(pipe,name)
                    def __call__(self,*a,**kw):
                        raw=pipe(*a,**kw);save(path/'pipeline_raw_response.json',raw);return raw
                try:
                    self._inner.pipeline=RecordingPipeline()
                    answer=self._inner.invoke(prompt,stop=stop,**kwargs)
                finally:
                    self._inner.pipeline=pipe;pipe.model.generate=original_generate
                (path/'response.txt').write_text(answer)
                peak_rss=None
                if sys.platform=='linux':
                    import resource
                    peak_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
                save(complete,{'response_sha256':hashlib.sha256(answer.encode()).hexdigest(),'seconds':time.monotonic()-started,'actual_generation':observed,'input_tokens_tokenizer_precheck':n,'process_peak_rss_bytes':peak_rss})
                return answer
            except Exception as e:
                save(path/'error.json',{'error_type':type(e).__name__,'seconds':time.monotonic()-started});raise
    return CheckpointLLM()
def extract(config,pid,out):
    import torch
    torch.manual_seed(config['seed']);random.seed(config['seed'])
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.documents import Document
    from langchain.chains import RetrievalQA
    from typing import List
    from prompting import TDMPrompt
    class FrozenRetriever(BaseRetriever):
        external_docs:List
        def _get_relevant_documents(self,query,*,run_manager):return self.external_docs
    source=read(ROOT/'data/evidence'/(pid+'.json'))[pid]
    llm=factory(config,1024,out/'calls')
    prompt=TDMPrompt(config['system_prompt'],config['model_type'])
    chain=RetrievalQA.from_chain_type(llm=llm,chain_type='stuff',retriever=FrozenRetriever(external_docs=[Document(page_content=d['content'],metadata=d['metadata']) for d in source]),return_source_documents=True,chain_type_kwargs={'prompt':prompt.prompt_template})
    result=chain.invoke(config['query_prompt'])
    docs=[{'content':d.page_content,'metadata':d.metadata} for d in result['source_documents']];assert docs==source
    save(out/'output.json',{pid:{'output':result['result'],'source_documents':docs}});validation=validate(result['result']);save(out/'validation.json',validation)
    save(out/'config.json',config)
    return validation
def official_stage(stage,config,config_path,output_path,out,cold_seed=None):
    import utils
    budgets={'fully':15,'partial':15,'cold':15,'leaderboard':100}
    if (out/'stage_complete.json').exists():print('SKIP complete stage');return
    out.mkdir(parents=True,exist_ok=True)
    original=utils.llm_init_langchain
    if stage in budgets:
        llm=factory(config,budgets[stage],out/'calls');utils.llm_init_langchain=lambda *a,**k:llm
    gold=ROOT/'data/gold';prompt=ROOT/'source/prompts.json'
    try:
        if stage in ('fully','cs'):
            save(out/'config.json',config);save(out/'output.json',read(output_path))
            import tdm_llm_normalization,tdm_embedding_normalization
            fn=tdm_llm_normalization.main if stage=='fully' else tdm_embedding_normalization.main
            fn(types.SimpleNamespace(gold_tdm_path=str(gold/'tdm_annotations.json'),tdm_output_path=str(out)+'/',prompt_file=str(prompt),max_new_tokens=15,seed=0))
        elif stage in ('partial','cold'):
            import tdm_llm_masked_normalization as m
            m.main(types.SimpleNamespace(gold_tdm_file=str(gold/'tdm_annotations.json'),gold_leaderboard_file=str(gold/'leaderboards.json'),tdm_config_file=str(config_path),tdm_output_file=str(output_path),normalization_output_path=str(out)+'/',prompt_file=str(prompt),cold_start=stage=='cold',cold_start_seed=cold_seed,max_new_tokens=15,seed=0))
        elif stage=='leaderboard':
            import leaderboard_llm_normalization as m
            m.main(types.SimpleNamespace(gold_leaderboard_file=str(gold/'leaderboards.json'),tdm_config_file=str(config_path),masked_normalized_file=str(output_path),leaderboard_normalization_path=str(out)+'/',prompt_file=str(prompt),max_new_tokens=100,seed=0))
        save(out/'stage_complete.json',{'stage':stage,'status':'COMPLETE'})
    finally:utils.llm_init_langchain=original
def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['smoke','extract','fully','cs','partial','cold','leaderboard']);p.add_argument('--model',choices=['llama2','llama3'],default='llama3');p.add_argument('--paper-id');p.add_argument('--out',required=True,type=Path);p.add_argument('--config',type=Path);p.add_argument('--input',type=Path);p.add_argument('--cold-start-seed');p.add_argument('--formal-authorized',action='store_true');a=p.parse_args()
    if 'runs/formal' in a.out.as_posix() and not a.formal_authorized:raise SystemExit('Formal execution requires explicit --formal-authorized')
    import fcntl
    a.out.mkdir(parents=True,exist_ok=True);execution_lock=(a.out/'.execution.lock').open('a')
    try:fcntl.flock(execution_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise SystemExit('This output directory already has an active task')
    import torch
    random.seed(0);torch.manual_seed(0)
    info=read(ROOT/'setup/model_manifest.json')[a.model]
    state=ROOT/'setup'/(a.model+'_download_status.json')
    if not state.exists() or read(state).get('status')!='READY':raise SystemExit('Official model weights not verified READY')
    prompts=read(ROOT/'source/prompts.json');config={'model_type':info['model_type'],'model_path':str(ROOT/'models'/a.model),'is_few_shot':False,'system_prompt':prompts['tdm-extraction-system-prompt'],'query_prompt':prompts['query'],'max_new_tokens':1024,'seed':0,'model_revision':info['revision'],'is_preprocessed_doc':True}
    if a.config:config=read(a.config)
    if config['model_type'] not in ('llama-2-chat-70b','llama-3-instruct-70b'):raise SystemExit('Only local Llama is allowed')
    if config['model_type']!=info['model_type'] or Path(config['model_path']).resolve()!=(ROOT/'models'/a.model).resolve() or config.get('model_revision')!=info['revision']:raise SystemExit('Model/config/revision mismatch')
    if a.stage in ('extract','smoke'):
        from input_audit import audit
        rows=audit(Path(config['model_path']),config['model_type'],a.out/'input_length_audit.csv')
        eligible=[x['paper_id'] for x in rows if not x['overlength']]
        pid=a.paper_id or (eligible[0] if eligible else None)
        if pid not in eligible:raise SystemExit('Full evidence plus generation budget exceeds model context')
        if a.stage=='smoke':
            short=factory(config,16,a.out/'short_generation/calls')
            short.invoke('Write the word ready.');del short
            import gc;gc.collect()
            torch.cuda.empty_cache()
        ext=a.out/'extraction';v=extract(config,pid,ext)
        if not v['valid']:raise SystemExit('Raw output not valid TDMR JSON. Preserved without repair.')
        if a.stage=='smoke':
            import gc;gc.collect();torch.cuda.empty_cache()
            data=read(ext/'output.json');data[pid]['output']=json.dumps(json.loads(data[pid]['output'])[:3])
            limited=a.out/'normalization_input.json';save(limited,data)
            official_stage('fully',config,ext/'config.json',limited,a.out/'fully_smoke')
    else:
        if not a.config or not a.input:raise SystemExit('--config and --input required')
        official_stage(a.stage,config,a.config,a.input,a.out,a.cold_start_seed)
if __name__=='__main__':main()
