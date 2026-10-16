from common import *
import types
from run import PlanObserver, normalization
from transport import Transport
def main():
    setup();m=read(RUN/'manifest.json');test=RUN/'offline_tests'/str(time.time_ns());test.mkdir(parents=True)
    from prompting import TDMPrompt
    from langchain.chains import RetrievalQA
    from langchain_core.documents import Document
    from langchain_community.chat_models.fake import FakeListChatModel
    from langchain_core.callbacks import BaseCallbackHandler
    from pdf_loader import PreProcessedDocuments
    prompts=read(REPO/'prompts.json');template=TDMPrompt(prompts['few-shot-extraction-system-prompt'],'gpt4-turbo-128k').prompt_template
    class Capture(BaseCallbackHandler):
        def on_chat_model_start(self,serialized,messages,**kwargs):self.messages=wire(messages[0])
    row=m['papers'][0];ds=read(row['evidence_path'])['source_documents'];docs=[Document(page_content=x['content'],metadata=x['metadata']) for x in ds];cap=Capture()
    chain=RetrievalQA.from_chain_type(llm=FakeListChatModel(responses=['[]'],callbacks=[cap]),chain_type='stuff',retriever=PreProcessedDocuments(docs).init_retriever(),return_source_documents=True,chain_type_kwargs={'prompt':template})
    result=chain.invoke(prompts['query']);assert result['source_documents']==docs and cap.messages==read(Path(row['extraction_dir'])/'request_plan.json')[0]['messages'];assert cap.messages[0]['content'].count('[Start of the Example]')==1
    # Original main must preserve repeated paid-call positions, exact matches,
    # out-of-set outputs, whitespace, and untouched Result strings.
    rr=[{'Task':'offline-unknown','Dataset':'CNN/DailyMail','Metric':'ROGUE-1','Result':'0.4 +/- 0.02'} for _ in range(3)]
    ex=test/'extraction';save(ex/'output.json',{row['id']:{'output':json.dumps(rr),'source_documents':[]}});save(ex/'summary.json',{'status':'COMPLETE'})
    calls=[]
    def mock(e):
        calls.append(e);return ['Summarization','None',' Summarization'][len(calls)-1]
    fake=dict(row,extraction_dir=str(ex),normalization_dir=str(test/'norm_input/normalization'))
    normalization(fake,mock=mock);nr=read(Path(fake['normalization_dir'])/'normalized_output.json')[row['id']]['normalized_output'];assert len(calls)==3 and [r['Task'] for r in nr]==['Summarization',None,None];assert [r['Result'] for r in nr]==[r['Result'] for r in rr]
    second_calls=[]
    def second_mock(e):second_calls.append(e);return 'Summarization'
    second=dict(fake,normalization_dir=str(test/'second_input/normalization'));normalization(second,mock=second_mock);assert len(second_calls)==3
    assert all(x['Task']=='Summarization' for x in read(Path(second['normalization_dir'])/'normalized_output.json')[row['id']]['normalized_output'])
    # Replay a completed identical position without any new network or mock call.
    plan=read(Path(fake['normalization_dir'])/'request_plan.json');ob=PlanObserver(plan,'test');t=Transport(Path(fake['normalization_dir']),ob,mock=lambda e:(_ for _ in ()).throw(AssertionError('Replay must not send')));llm=t.create_mock()
    from langchain_core.messages import SystemMessage,HumanMessage
    class Prompt:
        def to_messages(self):return [SystemMessage(content=plan[0]['messages'][0]['content']),HumanMessage(content=plan[0]['messages'][1]['content'])]
    assert llm.invoke(Prompt()).content=='Summarization'
    failure=test/'failure';t=Transport(failure,PlanObserver(plan,'test'));count=[0]
    def fail():
        count[0]+=1;(t.active['folder']/'attempt.json').write_text('{}');raise TimeoutError('mock ambiguous failure')
    try:t.generate(plan[0]['messages'],fail,lambda b:b)
    except TimeoutError:pass
    else:raise AssertionError('Expected timeout')
    try:t.generate(plan[0]['messages'],fail,lambda b:b)
    except RuntimeError:pass
    else:raise AssertionError('Retry should be blocked')
    assert count==[1]
    truncated=test/'truncated';t=Transport(truncated,PlanObserver(plan,'test'))
    def non_stop():
        a=t.active;(a['folder']/'attempt.json').write_text('{}');body={'model':MODEL,'choices':[{'finish_reason':'length','message':{'content':'partial'}}]};save(a['folder']/'response.json',body);a['state'].update(http_status=200,returned_model=MODEL,finish_reason='length');return body
    try:t.generate(plan[0]['messages'],non_stop,lambda b:b)
    except AssertionError:pass
    else:raise AssertionError('Non-stop output should halt')
    assert read(truncated/'api_calls/0001/state.json')['status']=='FAILED_OR_UNCERTAIN'
    assert not validate('[{"Task":"x"}]')['schema_valid'] and not validate('```json\n[]\n```')['json_valid'] and validate('[]')['schema_valid']
    save(RUN/'offline_validation.json',{'passed':True,'network_requests':0,'checks':['actual RetrievalQA stuff message/evidence equality','one official example in System','original Fully normalization prompt/logic','repeated value separate positions','out-of-set and whitespace map null','Result unmodified','completed response replay no request','ambiguous attempt blocks retry','non-stop response blocked','invalid JSON/schema refused'],'test_artifacts':str(test)})
    print('OFFLINE_VALIDATION_PASS')
if __name__=='__main__':main()
