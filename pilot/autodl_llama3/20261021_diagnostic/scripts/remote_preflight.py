"""Read-only GPU/environment/source and historical-output audit. No generation."""
from pathlib import Path
import json,hashlib,subprocess,sys,os,inspect
ROOT=Path('/root/autodl-tmp/scilead')
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'source')]
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
EXPECTED=__EXPECTED_HASHES__
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args):
    p=subprocess.run(args,text=True,capture_output=True)
    return {'code':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
def main():
    mismatches=[rel for rel,digest in EXPECTED.items() if sha(ROOT/rel)!=digest]
    assert not mismatches, 'FROZEN_SOURCE_OR_EVIDENCE_MISMATCH'
    ready=json.loads((ROOT/'setup/llama3_download_status.json').read_text())
    assert ready['status']=='READY' and ready['revision']=='50fd307e57011801c7833c87efa1984ddf2db42f'
    config=json.loads((ROOT/'models/llama3/config.json').read_text())
    assert config['max_position_embeddings']==8192
    weights=list((ROOT/'models/llama3').glob('*.safetensors'))
    assert len(weights)==30 and sum(p.stat().st_size for p in weights)==141107497872
    assert sha(ROOT/'models/llama3/config.json')=='bfd937677ee1c3d5b535ccaeec3223c06eca9452f3ac0dabe2ff87deb0f818a4'
    import torch,transformers,bitsandbytes,importlib.metadata
    from transformers import AutoTokenizer,TextGenerationPipeline
    from input_audit import render
    from prompting import TDMPrompt
    from langchain.chains import RetrievalQA
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.documents import Document
    from langchain_core.language_models.llms import LLM
    from langchain_core.pydantic_v1 import PrivateAttr
    class Capture(LLM):
        _captured=PrivateAttr(default='')
        @property
        def _llm_type(self):return 'offline-capture'
        def _call(self,prompt,**kw):self._captured=prompt;return '[]'
    class Frozen(BaseRetriever):
        external_docs:list
        def _get_relevant_documents(self,query,*,run_manager):return self.external_docs
    tok=AutoTokenizer.from_pretrained(str(ROOT/'models/llama3'),use_fast=False,legacy=False,padding_side='left',local_files_only=True)
    prompts=json.loads((ROOT/'source/prompts.json').read_text());audit=[]
    for item in json.loads((ROOT/'data/paper_index.json').read_text()):
        docs=json.loads((ROOT/item['evidence_file']).read_text())[item['paper_id']]
        text=render('llama-3-instruct-70b',docs)
        llm=Capture();chain=RetrievalQA.from_chain_type(llm=llm,chain_type='stuff',retriever=Frozen(external_docs=[Document(page_content=d['content'],metadata=d['metadata']) for d in docs]),return_source_documents=True,chain_type_kwargs={'prompt':TDMPrompt(prompts['tdm-extraction-system-prompt'],'llama-3-instruct-70b').prompt_template})
        result=chain.invoke(prompts['query']);assert llm._captured==text
        ids=tok(text,add_special_tokens=False,truncation=False)['input_ids']
        assert text.count('<|begin_of_text|>')==1 and text.count('<|start_header_id|>')==3
        audit.append({'paper_id':item['paper_id'],'input_tokens':len(ids),'prompt_sha256':hashlib.sha256(text.encode()).hexdigest(),'evidence_count':len(docs),'first_token':ids[0],'begin_of_text_count':ids.count(tok.convert_tokens_to_ids('<|begin_of_text|>')),'eligible':len(ids)+1024<=8192})
    smoke=ROOT/'runs/smoke/llama3-20261021/extraction/calls/000000'
    request=json.loads((smoke/'request.json').read_text());raw=json.loads((smoke/'pipeline_raw_response.json').read_text());answer=(smoke/'response.txt').read_text()
    assert len(raw)==1 and len(raw[0])==1
    assert raw[0][0]['generated_text']==request['prompt']+answer
    assert answer.startswith('\n\nHere are the extracted tuples in JSON format:')
    runtime=json.loads((smoke.parent/'model_runtime.json').read_text())
    assert runtime['pipeline_forward_params']=={'max_new_tokens':1024,'do_sample':False}
    pipcheck=cmd([sys.executable,'-m','pip','check']);assert pipcheck['code']==0
    procs=cmd(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader'])
    assert procs['code']==0 and procs['stdout']=='','GPU_NOT_IDLE'
    result={'status':'PASS','source_hash_files':len(EXPECTED),'model_revision':ready['revision'],'weights_status':'30 files/sizes checked; previous full official LFS SHA256 verification reused','weights_bytes':sum(p.stat().st_size for p in weights),'gpu':cmd(['nvidia-smi','--query-gpu=name,memory.total,memory.used,memory.free,driver_version','--format=csv,noheader'])['stdout'],'gpu_processes':procs,'memory_limit':Path('/sys/fs/cgroup/memory/memory.limit_in_bytes').read_text().strip() if Path('/sys/fs/cgroup/memory/memory.limit_in_bytes').exists() else Path('/sys/fs/cgroup/memory.max').read_text().strip(),'pip_check':pipcheck,'versions':{k:importlib.metadata.version(k) for k in ['torch','transformers','bitsandbytes','langchain','langchain-community','tokenizers','accelerate']},'cuda_runtime':torch.version.cuda,'pipeline_add_special_tokens_default':inspect.signature(TextGenerationPipeline.preprocess).parameters['add_special_tokens'].default,'tokenizer':{'class':type(tok).__name__,'bos':tok.bos_token_id,'eos':tok.eos_token_id,'padding_side':tok.padding_side},'historical_prefix_is_generated_content':True,'historical_raw_pipeline_equals_exact_prompt_plus_author_output':True,'retrievalqa_prompt_equivalences':len(audit),'audit':audit,'paid_api_calls':0,'new_model_generations':0}
    print(json.dumps(result))
if __name__=='__main__':main()
