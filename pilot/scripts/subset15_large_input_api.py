"""Generalized validated adapters; independent per-paper durable request ledger.

Resume replays only the identical, already-completed request at its original
position. Repeated field values still have distinct paid requests (no name cache).
An attempted request without a completed checkpoint is never automatically retried.
"""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import pickle
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; REPO=ROOT/'emnlp2024-leaderboard-generation'; SUB=Path(os.environ.get('SCILEAD_RUN_ROOT',str(ROOT/'pilot/subset15'))).resolve()
assert SUB.is_relative_to((ROOT/'pilot').resolve()),'Run root must remain inside SCILEAD/pilot'
MODEL='gpt-4.1-2025-04-14';BASE='https://9527.codes/v1';ENV_FILE=ROOT/'SCILEAD_small_test/.env'
KEY='';NETWORK=False;STAGE=''
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def scrub(x):
    if isinstance(x,str):return x.replace(KEY,'[REDACTED]') if KEY else x
    if isinstance(x,list):return [scrub(v) for v in x]
    if isinstance(x,dict):return {k:('[REDACTED]' if k.lower() in ('authorization','api_key','x-api-key') else scrub(v)) for k,v in x.items()}
    return x
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(scrub(x),ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wire(messages):return [{'role':{'system':'system','human':'user'}[m.type],'content':m.content} for m in messages]
def setup(stage):
    global KEY,STAGE
    STAGE=stage;work=SUB/'work';work.mkdir(exist_ok=True);os.chdir(work)
    os.environ.update({'HF_HOME':str(ROOT/'assets/huggingface'),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1','ANONYMIZED_TELEMETRY':'False','LANGCHAIN_TRACING':'false','LANGCHAIN_TRACING_V2':'false','LANGSMITH_TRACING':'false','TIKTOKEN_CACHE_DIR':str(ROOT/'assets/tiktoken')})
    logging.disable(logging.CRITICAL)
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo') and not NETWORK:raise RuntimeError('Network disabled outside authorized request')
        if event=='open' and isinstance(args[0],(str,bytes)):
            p=Path(os.fsdecode(args[0]));s=str(p).replace('\\','/').lower()
            if any(v in s for v in ('/.codex/','/.claude/','/.aws/')):raise RuntimeError('Unrelated sensitive configuration forbidden')
            if p.name.startswith('.env') and p.resolve()!=ENV_FILE.resolve():raise RuntimeError('Only designated dotenv authorized')
            if stage=='extract' and p.name in ('tdm_annotations.json','leaderboards.json','data-provenance.json'):raise RuntimeError('Extraction cannot read Gold answers')
    sys.addaudithook(guard)
    from dotenv import dotenv_values
    KEY=os.environ.get('OPENAI_API_KEY') or os.environ.get('API_KEY') or ''
    if not KEY:
        values=dotenv_values(ENV_FILE,interpolate=False,encoding='utf-8-sig');KEY=values.get('OPENAI_API_KEY') or values.get('API_KEY') or ''
    assert KEY.strip(),'Missing API key'
    KEY=KEY.strip();sys.path.insert(0,str(REPO))

def model_with_ledger(out,plan,max_tokens):
    import httpx,openai
    from langchain_openai import ChatOpenAI
    from langchain_core.pydantic_v1 import PrivateAttr
    calls=out/'api_calls';calls.mkdir(exist_ok=True)
    class Ledger:
        def __init__(self):self.cursor=0;self.active=None
        def summary(self):
            states=[read(p) for p in sorted(calls.glob('*/state.json'))]
            totals={k:sum((s.get('usage') or {}).get(k,0) or 0 for s in states) for k in ('prompt_tokens','completion_tokens','total_tokens')}
            usage={'requested_model':MODEL,'expected_requests':len(plan),'actual_request_attempts':len(list(calls.glob('*/attempt.json'))),'completed_requests':sum(s['status']=='COMPLETE' for s in states),'retries':0,'calls':states,'billing_cost':None,'seed':0,'seed_parameter_accepted':all(s.get('http_status')==200 for s in states) if states else None,'seed_determinism_verified':False,'candidate_order':'str(set), PYTHONHASHSEED=0','resume_policy':'Replay completed request at identical index/message only; no duplicate-name cache; unfinished attempts never retried',**totals}
            save(out/'api_usage.json',usage)
            if STAGE=='normalize':save(out/'normalization_api_usage.json',usage)
            return usage
    ledger=Ledger()
    def request_hook(request):
        payload=json.loads(request.content);a=ledger.active
        assert request.method=='POST' and str(request.url)==BASE+'/chat/completions'
        assert payload['messages']==a['expected']['messages'] and payload['model']==MODEL and payload['max_tokens']==max_tokens and payload['temperature']==0 and payload['seed']==0
        assert payload.get('n',1)==1 and not payload.get('stream',False)
        assert len(list(calls.glob('*/attempt.json')))<len(plan)
        with (a['folder']/'attempt.json').open('x',encoding='utf-8') as f:json.dump({'time':time.time(),'attempt':1},f)
        a['state']['status']='ATTEMPTED';save(a['folder']/'request.json',payload);save(a['folder']/'state.json',a['state']);ledger.summary()
    def response_hook(response):
        a=ledger.active;response.read()
        try:body=response.json()
        except ValueError:body={'body_text':response.text}
        a['state'].update(http_status=response.status_code,request_id=response.headers.get('x-request-id') or response.headers.get('request-id'))
        if 200<=response.status_code<300:
            a['state'].update(returned_model=body.get('model'),response_id=body.get('id'),usage=body.get('usage') or {},finish_reason=(body.get('choices') or [{}])[0].get('finish_reason'),system_fingerprint=body.get('system_fingerprint'))
        save(a['folder']/'response.json',body);save(a['folder']/'state.json',a['state']);ledger.summary()
    timeout=httpx.Timeout(connect=20,read=180,write=30,pool=20)
    client=httpx.Client(timeout=timeout,follow_redirects=False,event_hooks={'request':[request_hook],'response':[response_hook]})
    sdk=openai.OpenAI(api_key=KEY,base_url=BASE,organization='',project='',max_retries=0,timeout=timeout,http_client=client)
    class LoggedChatOpenAI(ChatOpenAI):
        _ledger=PrivateAttr()
        def _generate(self,messages,stop=None,run_manager=None,**kwargs):
            global NETWORK
            index=self._ledger.cursor;assert index<len(plan)
            expected=plan[index];assert wire(messages)==expected['messages'],'Request differs from fixed preflight'
            folder=calls/f'{index+1:04d}';folder.mkdir(exist_ok=True)
            if (folder/'state.json').exists():
                state=read(folder/'state.json')
                assert state['expected']==expected,'Resume input changed'
                if state['status']=='COMPLETE':
                    result=self._create_chat_result(read(folder/'response.json'));self._ledger.cursor+=1;return result
            if (folder/'attempt.json').exists():raise RuntimeError('Unfinished or failed request: no automatic retry')
            state={'call':index+1,'status':'PREPARING','expected':expected,'max_tokens':max_tokens,'model':MODEL,'temperature':0,'seed':0,'attempts':0}
            self._ledger.active={'folder':folder,'state':state,'expected':expected};start=time.monotonic()
            try:
                NETWORK=True;result=super()._generate(messages,stop=stop,run_manager=run_manager,**kwargs);NETWORK=False
                state.update(status='COMPLETE',raw_answer=result.generations[0].message.content,attempts=1)
                self._ledger.cursor+=1;return result
            except Exception as exc:
                NETWORK=False;state.update(status='FAILED',error_type=type(exc).__name__,error=scrub(str(exc)),attempts=int((folder/'attempt.json').exists()));raise
            finally:
                NETWORK=False;state['seconds']=round(time.monotonic()-start,3);save(folder/'state.json',state);self._ledger.summary()
                print(f'{STAGE} request {index+1}/{len(plan)} {state["status"]}',flush=True)
    llm=LoggedChatOpenAI(model=MODEL,api_key=KEY,base_url=BASE,temperature=0,max_tokens=max_tokens,model_kwargs={'seed':0},max_retries=0,timeout=timeout,client=sdk.chat.completions,async_client=object(),cache=False)
    llm._ledger=ledger;return llm,ledger,client

def estimate(messages):
    import tiktoken
    e=tiktoken.encoding_for_model(MODEL)
    return 3+sum(3+len(e.encode(m['role']))+len(e.encode(m['content'])) for m in messages)
def validate(text):
    info={'json_valid':False,'is_array':False,'field_schema_valid':False,'results_are_strings':False,'records':None}
    try:rows=json.loads(text)
    except ValueError:return info
    info.update(json_valid=True,is_array=isinstance(rows,list))
    if not isinstance(rows,list):return info
    info.update(records=len(rows),field_schema_valid=all(isinstance(r,dict) and set(r)=={'Task','Dataset','Metric','Result'} and all(isinstance(v,str) for v in r.values()) for r in rows),results_are_strings=all(isinstance(r,dict) and isinstance(r.get('Result'),str) for r in rows))
    info['duplicates']=len(rows)-len({json.dumps(r,sort_keys=True) for r in rows});return info

def extraction(row):
    approval=read(SUB/'context_limit_exception.json')
    assert approval['approved'] is True and row['id']==approval['paper']=='1912.08777.pdf'
    input_limit=approval['input_limit']
    assert input_limit==60000 and approval['authorized_input_tokens']==54504
    out=Path(row['extraction_dir']);out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists():
        s=read(out/'summary.json')
        if s['status']=='COMPLETE':print('SKIP_COMPLETE extraction',row['id']);return
        if s['status'] in ('INVALID_OUTPUT','TOKEN_LIMIT'):raise RuntimeError('Recorded extraction blocker retained; no repeat generation')
    pre=Path(row['preprocess_dir']);assert read(pre/'summary.json')['status']=='COMPLETE'
    with (pre/'processed_docs.pkl').open('rb') as f:papers=pickle.load(f)
    assert list(papers)==[row['id']];docs=papers[row['id']]
    from prompting import TDMPrompt
    from pdf_loader import PreProcessedDocuments
    from langchain.chains import RetrievalQA
    prompts=read(REPO/'prompts.json');template=TDMPrompt(prompts['tdm-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    messages=wire(template.format_messages(question=prompts['query'],context='\n\n'.join(d.page_content for d in docs)))
    tokens=estimate(messages);plan=[{'call':1,'messages':messages,'estimated_prompt_tokens':tokens}]
    assert plan==read(Path(approval['blocked_extraction_dir'])/'request_plan.json'),'Approved input changed'
    assert sha(pre/'processed_docs.pkl')==approval['processed_docs_sha256']
    save(out/'request_plan.json',plan)
    config={'paper':row['id'],'model':MODEL,'model_type':'gpt4-turbo-128k','is_few_shot':False,'zero_shot':True,'base_url':BASE,'temperature':0,'seed':0,'max_tokens':1024,'max_retries':0,'chain_type':'stuff','query':prompts['query'],'processed_docs_path':str(pre/'processed_docs.pkl'),'processed_docs_sha256':sha(pre/'processed_docs.pkl'),'evidence_count':len(docs),'prompt_sha256':sha(REPO/'prompts.json'),'estimated_prompt_tokens':tokens,'provider_context_limit':'UNVERIFIED','user_input_limit':input_limit,'input_limit_exception':str(SUB/'context_limit_exception.json')}
    save(out/'config.json',config);save(out/'dry_run.json',{'tokens':tokens,'under_30000':tokens<=30000,'within_authorized_exception':tokens<=input_limit,'paper_count':1,'evidence_count':len(docs),'gold_read':False})
    if tokens>input_limit:save(out/'summary.json',{'status':'TOKEN_LIMIT','tokens':tokens});return
    llm,ledger,client=model_with_ledger(out,plan,1024);start=time.monotonic()
    try:
        chain=RetrievalQA.from_chain_type(llm=llm,chain_type='stuff',retriever=PreProcessedDocuments(docs=docs).init_retriever(),return_source_documents=True,chain_type_kwargs={'prompt':template})
        result=chain.invoke(prompts['query']);assert result['source_documents']==docs
        save(out/'output.json',{row['id']:{'output':result['result'],'source_documents':[{'content':d.page_content,'metadata':d.metadata} for d in result['source_documents']]}})
        v=validate(result['result']);last=ledger.summary()['calls'][0];v.update(finish_reason=last.get('finish_reason'),output_truncated=last.get('finish_reason')=='length');save(out/'validation.json',v)
        status='COMPLETE' if v['field_schema_valid'] and not v['output_truncated'] else 'INVALID_OUTPUT'
        save(out/'summary.json',{'status':status,'records':v['records'],'seconds':round(time.monotonic()-start,3),'evidence_count':len(docs),'tokens':tokens})
    finally:client.close()

def normalization(row):
    ex=Path(row['extraction_dir']);out=Path(row['normalization_dir']);out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists() and read(out/'summary.json')['status']=='COMPLETE':print('SKIP_COMPLETE normalization',row['id']);return
    assert read(ex/'summary.json')['status']=='COMPLETE','Extraction unavailable or invalid'
    manifest=read(SUB/'manifest.json');gold=read(Path(manifest['gold_path']));assert sha(Path(manifest['gold_path']))==manifest['gold_sha256']
    labels={k:set() for k in ('Task','Dataset','Metric')}
    for value in gold.values():
        for r in value['TDMs']:
            for k in labels:labels[k].add(r[k])
    output=read(ex/'output.json');assert list(output)==[row['id']];rows=json.loads(output[row['id']]['output'])
    from prompting import NormalizationPrompt
    template=NormalizationPrompt(read(REPO/'prompts.json')['normalization-system-prompt'],'gpt4-turbo-128k').prompt_template
    plan=[]
    for index,r in enumerate(rows):
        for k,v in r.items():
            if k!='Result' and v not in labels[k]:
                messages=wire(template.invoke({'items':str(labels[k]),'input':v}).to_messages());plan.append({'call':len(plan)+1,'record':index+1,'field':k,'original_value':v,'messages':messages,'estimated_prompt_tokens':estimate(messages)})
    assert len(plan)<=3*len(rows)
    save(out/'request_plan.json',plan);save(out/'candidate_sets.json',{k:str(v) for k,v in labels.items()});save(out/'config.json',{'model':MODEL,'max_tokens':15,'temperature':0,'seed':0,'max_retries':0,'python_hash_seed':0,'calls_expected':len(plan),'gold_sha256':manifest['gold_sha256'],'input_sha256':sha(ex/'output.json')})
    llm,ledger,client=model_with_ledger(out,plan,15)
    import tdm_llm_normalization as official
    official.utils.llm_init_langchain=lambda config,max_new_tokens,seed:llm
    args=argparse.Namespace(seed=0,max_new_tokens=15,gold_tdm_path=manifest['gold_path'],tdm_output_path=ex.as_posix()+'/',prompt_file=str(REPO/'prompts.json'))
    start=time.monotonic()
    try:
        official.main(args);assert ledger.cursor==len(plan)
        normalized=read(out/'normalized_output.json')[row['id']];assert normalized['source_documents']==output[row['id']]['source_documents'];nr=normalized['normalized_output'];assert [r['Result'] for r in nr]==[r['Result'] for r in rows]
        u=ledger.summary();accepted=0
        for c in u['calls']:
            c['exact_member_of_standard_set']=c['raw_answer'] in labels[c['expected']['field']];accepted+=int(c['exact_member_of_standard_set'])
        save(out/'normalization_api_usage.json',u)
        save(out/'summary.json',{'status':'COMPLETE','records':len(nr),'calls':len(plan),'llm_valid_mappings':accepted,'llm_invalid_mappings':len(plan)-accepted,'null_fields':sum(r[k] is None for r in nr for k in labels),'exact_fields_skipped':3*len(rows)-len(plan),'seconds':round(time.monotonic()-start,3)})
    finally:client.close()

def worker(paper,stage):
    row=next(r for r in read(SUB/'manifest.json')['papers'] if r['id']==paper);assert not row['reused'],'Prior baseline must not be rerun'
    setup(stage)
    if stage=='extract':extraction(row)
    else:normalization(row)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--paper');parser.add_argument('--stage',choices=['extract','normalize','all'],default='all');a=parser.parse_args()
    if a.paper:
        assert a.stage!='all';worker(a.paper,a.stage);return
    stages=['extract','normalize'] if a.stage=='all' else [a.stage]
    for row in read(SUB/'manifest.json')['papers']:
        if row['reused']:continue
        for stage in stages:
            prerequisite=Path(row['preprocess_dir'])/'summary.json' if stage=='extract' else Path(row['extraction_dir'])/'summary.json'
            if not prerequisite.exists() or read(prerequisite)['status']!='COMPLETE':print('SKIP_PREREQUISITE',stage,row['id'],flush=True);continue
            folder=Path(row['extraction_dir'] if stage=='extract' else row['normalization_dir']);folder.mkdir(parents=True,exist_ok=True)
            if (folder/'summary.json').exists() and read(folder/'summary.json')['status']=='COMPLETE':continue
            print('START',stage,row['id'],flush=True)
            with (folder/'run.log').open('a',encoding='utf-8') as log:
                process=subprocess.run([sys.executable,'-X','utf8',__file__,'--paper',row['id'],'--stage',stage],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONHASHSEED='0',PYTHONDONTWRITEBYTECODE='1'))
            m=read(SUB/'manifest.json');entry=next(p for p in m['papers'] if p['id']==row['id']);s=read(folder/'summary.json') if (folder/'summary.json').exists() else {'status':'FAILED'};entry['status']=stage.upper()+'_'+s['status'];save(SUB/'manifest.json',m);print('END',stage,row['id'],s['status'],'exit',process.returncode,flush=True)
            if process.returncode!=0:break
if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Model errors are already redacted in the durable call ledger.
        print('STAGE_STOP',type(exc).__name__,scrub(str(exc)),flush=True);sys.exit(2)
