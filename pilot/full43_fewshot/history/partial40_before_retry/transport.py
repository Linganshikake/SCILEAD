"""Durable transport copied from validated Cold Start engine, without its normalization observer."""
import logging, types
import common as c
from common import *

class Transport:
    def __init__(self,out,observer,mock=None,interrupt_after=None):
        self.out=Path(out);self.observer=observer;self.cursor=0;self.mock=mock;self.interrupt_after=interrupt_after;self.mock_new=0;self.client=None;self.llm=None
        (self.out/'api_calls').mkdir(parents=True,exist_ok=True)
    def summary(self):
        states=[read(p) for p in sorted((self.out/'api_calls').glob('*/state.json'))];attempts=len(list((self.out/'api_calls').glob('*/attempt.json')))
        usage={'attempts':attempts,'successful_responses':sum(x.get('status')=='COMPLETE' for x in states),'failed_or_uncertain':sum(x.get('status')!='COMPLETE' and (self.out/'api_calls'/f'{x["call"]:04d}'/'attempt.json').exists() for x in states),'unknown_usage_attempts':sum(not x.get('usage') for x in states if (self.out/'api_calls'/f'{x["call"]:04d}'/'attempt.json').exists()),'prompt_tokens':sum((x.get('usage') or {}).get('prompt_tokens',0) or 0 for x in states),'completion_tokens':sum((x.get('usage') or {}).get('completion_tokens',0) or 0 for x in states),'total_tokens':sum((x.get('usage') or {}).get('total_tokens',0) or 0 for x in states),'request_seconds':sum(x.get('seconds',0) for x in states),'mock':self.mock is not None,'calls':states,'billing_cost':None,'seed':0,'seed_parameter_acceptance_observable':True,'determinism_not_guaranteed':True}
        save(self.out/'api_usage.json',usage);return usage
    def create_live(self):
        import httpx,openai
        from dotenv import dotenv_values
        from langchain_openai import ChatOpenAI
        from langchain_core.pydantic_v1 import PrivateAttr
        logging.disable(logging.CRITICAL)
        c.KEY=(os.environ.get('OPENAI_API_KEY') or os.environ.get('API_KEY') or '').strip()
        if not c.KEY:
            values=dotenv_values(ROOT/'SCILEAD_small_test/.env',interpolate=False,encoding='utf-8-sig');c.KEY=(values.get('OPENAI_API_KEY') or values.get('API_KEY') or '').strip()
        assert c.KEY,'Missing designated API credential'
        transport=self
        def request_hook(request):
            payload=json.loads(request.content);a=transport.active
            assert request.method=='POST' and str(request.url)==URL+'/chat/completions'
            assert payload['messages']==a['expected']['messages'] and payload['model']==MODEL and payload['temperature']==0 and payload['seed']==0
            assert payload.get('stream') is False and payload.get('n',1)==1
            assert not set(payload)&{'max_tokens','max_completion_tokens','max_output_tokens','response_format','tools','functions','stop'}
            a['state']['status']='ATTEMPTED'
            with (a['folder']/'attempt.json').open('x',encoding='utf-8') as f:json.dump({'time':time.time(),'attempt':1},f)
            save(a['folder']/'request.json',payload);save(a['folder']/'state.json',a['state'])
        def response_hook(response):
            a=transport.active;response.read()
            try:body=response.json()
            except ValueError:body={'body_text':response.text}
            a['state'].update(http_status=response.status_code,request_id=response.headers.get('x-request-id') or response.headers.get('request-id'))
            if isinstance(body,dict):a['state'].update(returned_model=body.get('model'),response_id=body.get('id'),usage=body.get('usage'),finish_reason=(body.get('choices') or [{}])[0].get('finish_reason'),system_fingerprint=body.get('system_fingerprint'))
            save(a['folder']/'response.json',body);save(a['folder']/'state.json',a['state'])
        timeout=httpx.Timeout(connect=20,read=180,write=30,pool=20)
        self.client=httpx.Client(timeout=timeout,follow_redirects=False,event_hooks={'request':[request_hook],'response':[response_hook]})
        sdk=openai.OpenAI(api_key=c.KEY,base_url=URL,organization='',project='',max_retries=0,timeout=timeout,http_client=self.client)
        class Logged(ChatOpenAI):
            def _generate(self,messages,stop=None,run_manager=None,**kwargs):return transport.generate(wire(messages),lambda:super(Logged,self)._generate(messages,stop=stop,run_manager=run_manager,**kwargs),self._create_chat_result)
        self.llm=Logged(model=MODEL,api_key=c.KEY,base_url=URL,temperature=0,max_tokens=None,model_kwargs={'seed':0},streaming=False,max_retries=0,timeout=timeout,client=sdk.chat.completions,async_client=object(),cache=False)
        return self.llm
    def generate(self,messages,send,convert):
        expected=self.observer.expected(messages);index=self.cursor+1;folder=self.out/'api_calls'/f'{index:04d}';folder.mkdir(exist_ok=True)
        immutable(folder/'expected.json',expected)
        if (folder/'state.json').exists():
            previous=read(folder/'state.json')
            if previous['status']=='COMPLETE':
                body=read(folder/'response.json');assert digest(body)==previous['response_sha256'];answer=body['choices'][0]['message']['content'];self.cursor=index;self.observer.answer(answer,index);return convert(body)
        if (folder/'attempt.json').exists():raise RuntimeError(f'Unresolved attempt {index}; automatic retry prohibited')
        state={'run_id':RUN_ID,'call':index,'status':'PREPARING','position':{k:expected[k] for k in ('paper','record','field')},'prompt_sha256':expected['prompt_sha256'],'candidate_sha256':expected['candidate_sha256'],'requested_model':MODEL}
        self.active={'folder':folder,'state':state,'expected':expected};save(folder/'state.json',state);start=time.monotonic()
        try:
            result=send();body=read(folder/'response.json')
            assert state.get('http_status')==200,'HTTP response not successful'
            assert state.get('returned_model')==MODEL,'Unexpected response model; dependent processing paused'
            assert state.get('finish_reason')=='stop','Response not complete stop; dependent processing paused'
            answer=body['choices'][0]['message']['content'];assert isinstance(answer,str)
            state.update(status='COMPLETE',raw_answer=answer,response_sha256=digest(body));save(folder/'state.json',state)
            if self.interrupt_after==index:raise SimulatedInterruption('After response saved, before original field update')
            self.cursor=index;self.observer.answer(answer,index);return result
        except SimulatedInterruption:raise
        except Exception as e:
            state.update(status='FAILED_OR_UNCERTAIN',error_type=type(e).__name__,error=c.scrub(str(e)));raise
        finally:
            state['seconds']=time.monotonic()-start;save(folder/'state.json',state);self.summary();print(self.observer.stage,index,state['status'],expected['paper'],expected['field'],flush=True)
    def create_mock(self):
        transport=self
        class Mock:
            def invoke(self,prompt):
                def convert(body):return types.SimpleNamespace(content=body['choices'][0]['message']['content'])
                def send():
                    a=transport.active;answer=transport.mock(a['expected']);transport.mock_new+=1
                    with (a['folder']/'attempt.json').open('x') as f:f.write('{}')
                    body={'model':MODEL,'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':answer}}],'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}}
                    a['state'].update(http_status=200,returned_model=MODEL,finish_reason='stop',usage=body['usage']);save(a['folder']/'response.json',body);return convert(body)
                return transport.generate(wire(prompt.to_messages()),send,convert)
        return Mock()
class SimulatedInterruption(Exception):pass

