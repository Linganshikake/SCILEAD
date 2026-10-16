import argparse, contextlib, collections
from common import *
from transport import Transport

def labels_and_plan(paper,rows):
    manifest=read(RUN/'input_manifest.json');gold=read(manifest['gold_path'])
    assert sha(manifest['gold_path'])==manifest['gold_sha256']
    labels={k:set() for k in ('Task','Dataset','Metric')}
    for value in gold.values():
        for record in value['TDMs']:
            for key in labels:labels[key].add(record[key])
    assert [len(v) for v in labels.values()]==[23,71,26]
    assert {k:str(v) for k,v in labels.items()}==read(RUN/'candidate_sets.json')
    from prompting import NormalizationPrompt
    template=NormalizationPrompt(read(REPO/'prompts.json')[NORMALIZATION_KEY],'gpt4-turbo-128k').prompt_template
    plan=[]
    for index,record in enumerate(rows,1):
        for key,value in record.items():
            if key!='Result' and value not in labels[key]:
                messages=wire(template.invoke({'items':str(labels[key]),'input':value}).to_messages())
                plan.append({'paper':paper,'record':index,'field':key,'original':value,'candidate_serialized':str(labels[key]),'candidate_sha256':digest(str(labels[key])),'messages':messages,'prompt_sha256':digest(messages),'estimated_prompt_tokens':estimate(messages)})
    return labels,plan

class PlanObserver:
    def __init__(self,plan):self.plan=plan;self.index=0;self.stage='fewshot-normalize'
    def expected(self,messages):
        expected=self.plan[self.index];assert messages==expected['messages'],'Actual message differs from official Few-shot template';return expected
    def answer(self,answer,index):assert index==self.index+1;self.index=index

def normalize_paper(row,mock=None,raw_override=None):
    out=Path(row['normalization_dir']);out.mkdir(parents=True,exist_ok=True)
    if (out/'summary.json').exists():
        assert read(out/'summary.json')['status']=='COMPLETE','Failed stage cannot automatically retry';return
    raw=raw_override if raw_override is not None else {row['id']:read(RUN/'input/output.json')[row['id']]}
    rows=json.loads(raw[row['id']]['output']);labels,plan=labels_and_plan(row['id'],rows)
    immutable(out/'request_plan.json',plan)
    immutable(out.parent/'output.json',raw)
    immutable(out.parent/'config.json',{'is_few_shot':True,'model_type':'gpt4-turbo-128k','actual_model':MODEL,'normalization_prompt':NORMALIZATION_KEY,'max_tokens_policy':'omitted','normalization_only':True})
    observer=PlanObserver(plan);t=Transport(out,observer,mock=mock,calls_dir=row.get('calls_dir'));start=time.time()
    import tdm_llm_normalization as official
    try:
        llm=t.create_mock() if mock is not None else t.create_live()
        official.utils.llm_init_langchain=lambda config,max_new_tokens,seed:llm
        official.main(argparse.Namespace(seed=0,max_new_tokens=None,gold_tdm_path=read(RUN/'input_manifest.json')['gold_path'],tdm_output_path=out.parent.as_posix()+'/',prompt_file=str(REPO/'prompts.json')))
        assert t.cursor==len(plan)
        nr=read(out/'normalized_output.json')[row['id']]
        assert nr['source_documents']==raw[row['id']]['source_documents']
        assert len(nr['normalized_output'])==len(rows)
        assert [x['Result'] for x in nr['normalized_output']]==[x['Result'] for x in rows]
        calls=t.summary()['calls']
        save(out/'summary.json',{'status':'COMPLETE','records':len(rows),'requests':len(plan),'exact_fields_skipped':len(rows)*3-len(plan),'null_fields':sum(x[k] is None for x in nr['normalized_output'] for k in labels),'returned_candidate':sum(x['raw_answer'] in labels[x['position']['field']] for x in calls),'seconds':time.time()-start,'official_main_used':True,'is_few_shot':True,'prompt_key':NORMALIZATION_KEY})
    except Exception as e:
        save(out/'summary.json',{'status':'FAILED','error_type':type(e).__name__,'error':scrub(str(e)),'seconds':time.time()-start});raise
    finally:
        if t.client:t.client.close()
        t.summary()

def main():
    setup('normalize');assert os.environ.get('PYTHONHASHSEED')=='0'
    verify();assert read(RUN/'offline_validation.json')['passed']
    m=read(RUN/'input_manifest.json');immutable(RUN/'execution_started.json',read(RUN/'execution_started.json') if (RUN/'execution_started.json').exists() else {'epoch':time.time()})
    for row in m['papers']:
        out=Path(row['normalization_dir']);out.mkdir(parents=True,exist_ok=True)
        if (out/'summary.json').exists():print('SKIP_RECORDED',row['id'],read(out/'summary.json')['status'],flush=True);continue
        print('START',row['id'],row['expected_normalization_requests'],flush=True)
        with (out/'run.log').open('a',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            try:normalize_paper(row)
            except Exception as e:print('STOP',type(e).__name__,scrub(str(e)),flush=True)
        state=read(out/'summary.json');row['status']=state['status'];save(RUN/'input_manifest.json',m)
        print('END',row['id'],state['status'],flush=True)
    save(RUN/'execution_finished.json',{'epoch':time.time()})

if __name__=='__main__':main()
