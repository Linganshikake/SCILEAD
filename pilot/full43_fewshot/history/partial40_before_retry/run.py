import argparse, subprocess, shutil, contextlib
from common import *
from transport import Transport
class PlanObserver:
    def __init__(self,plan,stage):self.plan=plan;self.stage=stage;self.index=0
    def expected(self,messages):
        p=self.plan[self.index];assert messages==p['messages'],'Request differs from frozen plan';return p
    def answer(self,answer,index):assert index==self.index+1;self.index=index
def normalization_plan(paper,rows):
    manifest=read(RUN/'manifest.json');gold=read(manifest['gold_path']);assert sha(manifest['gold_path'])==manifest['gold_sha256']
    labels={k:set() for k in ('Task','Dataset','Metric')}
    for v in gold.values():
        for r in v['TDMs']:
            for k in labels:labels[k].add(r[k])
    assert {k:str(v) for k,v in labels.items()}==read(RUN/'candidate_sets.json')
    from prompting import NormalizationPrompt
    template=NormalizationPrompt(read(REPO/'prompts.json')['normalization-system-prompt'],'gpt4-turbo-128k').prompt_template
    plan=[]
    for i,r in enumerate(rows,1):
        for k,v in r.items():
            if k!='Result' and v not in labels[k]:
                messages=wire(template.invoke({'items':str(labels[k]),'input':v}).to_messages())
                plan.append({'paper':paper,'record':i,'field':k,'original':v,'candidate_serialized':str(labels[k]),'candidate_sha256':digest(str(labels[k])),'messages':messages,'prompt_sha256':digest(messages),'estimated_prompt_tokens':estimate(messages)})
    return plan,labels
def extraction(row):
    out=Path(row['extraction_dir']);plan=read(out/'request_plan.json');evidence=read(row['evidence_path']);docs=evidence['source_documents'];assert digest(docs)==row['source_documents_sha256']
    if (out/'summary.json').exists():
        assert read(out/'summary.json')['status']=='COMPLETE','Previous failed extraction is not retried';return
    from langchain_core.documents import Document
    from prompting import TDMPrompt
    from pdf_loader import PreProcessedDocuments
    from langchain.chains import RetrievalQA
    documents=[Document(page_content=d['content'],metadata=d['metadata']) for d in docs]
    prompts=read(REPO/'prompts.json');template=TDMPrompt(prompts['few-shot-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    observer=PlanObserver(plan,'extract');t=Transport(out,observer);start=time.time()
    immutable(out/'config.json',{'model':MODEL,'model_type':'gpt4-turbo-128k','is_few_shot':True,'temperature':0,'seed':0,'stream':False,'max_tokens_policy':'omitted','chain_type':'stuff','source_documents_sha256':digest(docs),'query':prompts['query'],'system_prompt_key':'few-shot-extraction-system-prompt'})
    try:
        llm=t.create_live();chain=RetrievalQA.from_chain_type(llm=llm,chain_type='stuff',retriever=PreProcessedDocuments(documents).init_retriever(),return_source_documents=True,chain_type_kwargs={'prompt':template})
        result=chain.invoke(prompts['query']);assert result['source_documents']==documents
        immutable(out/'output.json',{row['id']:{'output':result['result'],'source_documents':docs}})
        v=validate(result['result']);save(out/'validation.json',v)
        assert v['schema_valid'],'Invalid raw JSON/schema; no repair or normalization'
        save(out/'summary.json',{'status':'COMPLETE','records':v['records'],'seconds':time.time()-start,'evidence_count':len(docs)})
    except Exception as e:
        save(out/'summary.json',{'status':'FAILED','error_type':type(e).__name__,'error':scrub(str(e)),'seconds':time.time()-start});raise
    finally:
        if t.client:t.client.close()
        t.summary()
def normalization(row,mock=None,output_override=None):
    ex=Path(row['extraction_dir']);out=Path(output_override or row['normalization_dir']);out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists():
        assert read(out/'summary.json')['status']=='COMPLETE','Failed normalization requires explicit review';return
    assert read(ex/'summary.json')['status']=='COMPLETE'
    raw=read(ex/'output.json');rows=json.loads(raw[row['id']]['output']);plan,labels=normalization_plan(row['id'],rows)
    immutable(out/'request_plan.json',plan);immutable(out/'candidate_sets.json',{k:str(v) for k,v in labels.items()})
    # Original normalization main reads config from its input directory. A separate
    # directory selects the unchanged fully-predefined prompt, without falsifying
    # the extraction configuration or modifying official source.
    immutable(out.parent/'output.json',raw)
    immutable(out.parent/'config.json',{'model_type':'gpt4-turbo-128k','is_few_shot':False,'model':MODEL,'normalization_only':True,'extraction_was_few_shot':True,'output_limit_policy':'omitted'})
    observer=PlanObserver(plan,'normalize');t=Transport(out,observer,mock=mock);start=time.time()
    import tdm_llm_normalization as official
    try:
        llm=t.create_mock() if mock is not None else t.create_live()
        official.utils.llm_init_langchain=lambda config,max_new_tokens,seed:llm
        official.main(argparse.Namespace(seed=0,max_new_tokens=None,gold_tdm_path=read(RUN/'manifest.json')['gold_path'],tdm_output_path=out.parent.as_posix()+'/',prompt_file=str(REPO/'prompts.json')))
        assert t.cursor==len(plan)
        nr=read(out/'normalized_output.json')[row['id']];assert nr['source_documents']==raw[row['id']]['source_documents']
        assert [r['Result'] for r in nr['normalized_output']]==[r['Result'] for r in rows]
        calls=t.summary()['calls'];save(out/'summary.json',{'status':'COMPLETE','records':len(rows),'requests':len(plan),'exact_fields_skipped':len(rows)*3-len(plan),'null_fields':sum(r[k] is None for r in nr['normalized_output'] for k in labels),'returned_candidate':sum(c['raw_answer'] in labels[c['position']['field']] for c in calls),'seconds':time.time()-start,'official_main_used':True,'normalization_prompt':'normalization-system-prompt'})
    except Exception as e:
        save(out/'summary.json',{'status':'FAILED','error_type':type(e).__name__,'error':scrub(str(e)),'seconds':time.time()-start});raise
    finally:
        if t.client:t.client.close()
        t.summary()
def orchestrate(stage):
    m=read(RUN/'manifest.json');immutable(RUN/'execution_started.json',read(RUN/'execution_started.json') if (RUN/'execution_started.json').exists() else {'epoch':time.time()})
    for r in m['papers']:
        folder=Path(r['extraction_dir'] if stage=='extract' else r['normalization_dir']);folder.mkdir(parents=True,exist_ok=True)
        if (folder/'summary.json').exists():print('SKIP_RECORDED',r['id'],stage,flush=True);continue
        if stage=='normalize' and (not (Path(r['extraction_dir'])/'summary.json').exists() or read(Path(r['extraction_dir'])/'summary.json')['status']!='COMPLETE'):continue
        print('START',stage,r['id'],flush=True)
        with (folder/'run.log').open('a',encoding='utf-8') as log:
            if stage=='normalize':
                # Reuse imported libraries only. Each paper still gets a fresh
                # client, observer, fixed candidate plan and independent ledger.
                # No model response or name-mapping cache crosses paper boundaries.
                with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
                    try:normalization(r);code=0
                    except Exception as e:print('STOP',type(e).__name__,scrub(str(e)),flush=True);code=2
            else:
                p=subprocess.run([sys.executable,'-B','-X','utf8',__file__,'--stage',stage,'--paper',r['id']],env=dict(os.environ,PYTHONHASHSEED='0'),stdout=log,stderr=subprocess.STDOUT);code=p.returncode
        s=read(folder/'summary.json') if (folder/'summary.json').exists() else {'status':'WORKER_FAILED'};r[stage+'_status']=s['status'];save(RUN/'manifest.json',m);print('END',stage,r['id'],s['status'],code,flush=True)
    save(RUN/(stage+'_finished.json'),{'epoch':time.time()})
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['extract','normalize'],required=True);p.add_argument('--paper');a=p.parse_args()
    setup(a.stage);assert os.environ.get('PYTHONHASHSEED')=='0'
    if a.paper:
        row=next(r for r in read(RUN/'manifest.json')['papers'] if r['id']==a.paper)
        (extraction if a.stage=='extract' else normalization)(row)
    else:orchestrate(a.stage)
if __name__=='__main__':
    try:main()
    except Exception as e:print('STOP',type(e).__name__,scrub(str(e)),flush=True);sys.exit(2)
