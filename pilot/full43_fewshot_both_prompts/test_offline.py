from common import *
from normalize import labels_and_plan,normalize_paper,PlanObserver
from transport import Transport

def main():
    setup();assert os.environ.get('PYTHONHASHSEED')=='0'
    row=read(RUN/'input_manifest.json')['papers'][0];folder=RUN/'offline_tests'/str(time.time_ns())
    labels,_=labels_and_plan(row['id'],[]);valid={k:sorted(v)[0] for k,v in labels.items()}
    records=[{**{k:'__offline_unknown__' for k in labels},'Result':'0.40 +/- 0.02'} for _ in range(3)]+[{**valid,'Result':'95.00%'}]
    docs=[{'content':'offline evidence retained verbatim','metadata':{'page_number':7}}]
    raw={row['id']:{'output':json.dumps(records),'source_documents':docs}}
    fake=dict(row,normalization_dir=str(folder/'input/normalization'),calls_dir=str(folder/'calls'))
    calls=[]
    def mock(e):
        calls.append(e);assert e['messages'][0]['content'].count('[Start of the Example]')==1
        assert e['messages'][1]['content']=='\n\nItem list: '+str(labels[e['field']])+'\n\nInput: __offline_unknown__\n\nAnswer: '
        return valid[e['field']] if e['record']==1 else 'None' if e['record']==2 else ' '+valid[e['field']]
    normalize_paper(fake,mock=mock,raw_override=raw)
    actual=read(Path(fake['normalization_dir'])/'normalized_output.json')[row['id']]
    assert len(calls)==9 and [x['record'] for x in calls]==[1,1,1,2,2,2,3,3,3]
    assert all(actual['normalized_output'][0][k]==valid[k] for k in labels)
    assert all(actual['normalized_output'][i][k] is None for i in (1,2) for k in labels)
    assert actual['normalized_output'][3]==records[3]
    assert actual['source_documents']==docs and [x['Result'] for x in actual['normalized_output']]==[x['Result'] for x in records]
    plan=read(Path(fake['normalization_dir'])/'request_plan.json')
    replay=Transport(Path(fake['normalization_dir']),PlanObserver(plan),mock=lambda e:(_ for _ in ()).throw(AssertionError('Must replay completed position')),calls_dir=fake['calls_dir'])
    from langchain_core.messages import SystemMessage,HumanMessage
    class Prompt:
        def to_messages(self):return [SystemMessage(content=plan[0]['messages'][0]['content']),HumanMessage(content=plan[0]['messages'][1]['content'])]
    assert replay.create_mock().invoke(Prompt()).content==valid['Task'] and replay.mock_new==0
    ambiguous=Transport(folder/'ambiguous',PlanObserver(plan));count=[0]
    def fail():
        count[0]+=1;(ambiguous.active['folder']/'attempt.json').write_text('{}');raise TimeoutError('mock uncertain request')
    try:ambiguous.generate(plan[0]['messages'],fail,lambda b:b)
    except TimeoutError:pass
    else:raise AssertionError('Expected transport failure')
    assert read(ambiguous.calls_dir/'0001/state.json')['status']=='FAILED_OR_UNCERTAIN'
    try:ambiguous.generate(plan[0]['messages'],fail,lambda b:b)
    except RuntimeError:pass
    else:raise AssertionError('Ambiguous request must not be repeated')
    assert count==[1]
    check=read(RUN/'precheck.json');assert check['exact_fields_total']+check['expected_requests']==293*3
    assert check['expected_requests']==453 and check['exact_fields_total']==426
    save(RUN/'offline_validation.json',{'passed':True,'new_api_requests':0,'original_main_executed':True,'is_few_shot':True,'prompt_key':NORMALIZATION_KEY,'checks':['original dispatch uses exact Few-shot system and Human template','static three examples once; dynamic candidates separate','all three fields in-set and out-of-set handling','whitespace response not cleaned','exact original names skip LLM','repeated unknown fields invoke independently','Result strings/evidence/order unchanged','completed request position replays locally','uncertain transport errors retained and retry blocked'],'test_dir':str(folder)})
    print('OFFLINE_VALIDATION_PASS',flush=True)

if __name__=='__main__':main()
