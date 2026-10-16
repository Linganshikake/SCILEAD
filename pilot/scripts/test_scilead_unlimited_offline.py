"""Verify wire parameters for both stages without network or credentials."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'pilot/subset15_uncapped_retry/offline_settings_test'
OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('scilead_unlimited',Path(__file__).with_name('scilead_api.py'))
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
import httpx
from langchain_core.messages import SystemMessage,HumanMessage
def guard(event,args):
    if event in ('socket.connect','socket.getaddrinfo'):raise AssertionError('Real network forbidden in test')
sys.addaudithook(guard)
seen=[]
def transport(request):
    payload=json.loads(request.content)
    assert 'max_tokens' not in payload and 'max_completion_tokens' not in payload
    assert payload['temperature']==0 and payload['seed']==0
    seen.append(payload)
    return httpx.Response(200,json={'id':'offline-'+api.STAGE,'object':'chat.completion','created':0,'model':api.MODEL,'choices':[{'index':0,'message':{'role':'assistant','content':'[]'},'finish_reason':'stop'}],'usage':{'prompt_tokens':10,'completion_tokens':1,'total_tokens':11}})
original=httpx.Client
class MockClient(original):
    def __init__(self,*args,**kwargs):
        kwargs['transport']=httpx.MockTransport(transport);super().__init__(*args,**kwargs)
httpx.Client=MockClient
api.KEY='offline-placeholder-not-a-real-key'
for stage in ('extract','normalize'):
    api.STAGE=stage
    (OUT/stage).mkdir(exist_ok=True)
    messages=[SystemMessage(content='Offline parameter test'),HumanMessage(content='No model request')]
    plan=[{'call':1,'messages':api.wire(messages)}]
    llm,ledger,client=api.model_with_ledger(OUT/stage,plan,None)
    llm.invoke(messages)
    before=len(seen);ledger.cursor=0;llm.invoke(messages);assert len(seen)==before
    client.close()
assert len(seen)==2
result={'status':'PASS','mock_requests':2,'real_network_requests':0,'both_stages_omit_output_token_parameters':True,'completed_checkpoint_replay_additional_requests':0}
(OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
