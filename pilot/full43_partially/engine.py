"""Original-main observer and same-position durable API response replay.

No normalization decisions replace official code: post-field assertions check
its actual locals. Trace hooks only persist state and compare replay events.
Transport is adapted from the previously validated scilead_api.py.
"""
import copy,inspect,logging,types
import common as c
from common import *

class Observer:
    def __init__(self,module,stage,out):
        self.module=module;self.stage=stage;self.out=Path(out);self.pending=None;self.event_index=0;self.call_index=0;self.events=[];self.initial=None
        source,start=inspect.getsourcelines(module.main)
        self.lines={s.strip():i+start for i,s in enumerate(source)}
        self.code=module.main.__code__
    def trace(self,frame,event,arg):
        if frame.f_code is not self.code:return None
        if event=='line':
            loc=frame.f_locals;line=frame.f_lineno
            if self.stage=='stage1':
                if line==self.lines['for key in tdm:'] and self.pending is not None:self.finish(loc)
                if line==self.lines["if key != 'Result' and tdm[key] not in labels_dict[key]:"]:
                    state=labels_state(loc['labels_dict'])
                    if self.initial is None:self.initial=state;immutable(self.out/'initial_labels.json',state)
                    self.pending={'paper':loc['paper'],'record':len(loc['normalized_tdms'])+1,'field':loc['key'],'original':loc['tdm'][loc['key']],'labels_before':state}
            else:
                if line==self.lines['normalized_tdm = tdm']:
                    self.pending={'paper':loc['paper'],'record':len(loc['normalized_tdms'])+1,'original':copy.deepcopy(loc['tdm']),'candidate_order':list(loc['leaderboard_tdm_set']),'candidate_serialized':'{'+', '.join(loc['leaderboard_tdm_set'])+'}'}
                    immutable(self.out/'candidates.json',{'ordered_values':list(loc['leaderboard_tdm_set']),'serialized':self.pending['candidate_serialized']})
                if line==self.lines['normalized_tdms.append(normalized_tdm)']:self.finish(loc)
        return self.trace
    def expected(self,messages):
        p=self.pending;assert p is not None
        if self.stage=='stage1':
            field=p['field'];serial=p['labels_before'][field]['serialized'];original=p['original']
        else:field='TDM';serial=p['candidate_serialized'];original='('+', '.join(p['original'][k] for k in ('Task','Dataset','Metric'))+')'
        assert messages[1]['content']=='\n\nItem list: '+serial+'\n\nInput: '+original+'\n\nAnswer: '
        return {'paper':p['paper'],'record':p['record'],'field':field,'original':original,'candidate_serialized':serial,'candidate_sha256':digest(serial),'messages':messages,'prompt_sha256':digest(messages)}
    def answer(self,answer,index):self.pending['raw_answer']=answer;self.pending['call']=index;self.call_index=index
    def finish(self,loc):
        p=self.pending;assert p is not None;event=copy.deepcopy(p)
        if self.stage=='stage1':
            k=p['field'];old=p['original'];before=p['labels_before'];after=labels_state(loc['labels_dict']);actual=loc['normalized_tdm'][k];added=None
            if k=='Result' or old in before[k]['ordered_values']:expected=str(old);branch='exact_or_result';assert 'call' not in p
            else:
                a=p['raw_answer']
                if a in before[k]['ordered_values']:expected=a;branch='existing_candidate'
                elif k in ('Task','Dataset') and a==old:expected=a;added=a;branch='original_name_added'
                else:expected=None;branch='null'
            assert actual==expected
            for key in before:assert set(after[key]['ordered_values'])==set(before[key]['ordered_values'])|({added} if added is not None and key==k else set())
            event.update(normalized=actual,branch=branch,added_name=added,labels_after=after)
        else:
            old=p['original'];expected=copy.deepcopy(old);branch='null_skipped' if any(old[k] is None for k in ('Task','Dataset','Metric')) else 'exact_tuple'
            if 'call' in p:
                if p['raw_answer'] in p['candidate_order']:
                    parts=p['raw_answer'][1:-1].split(', ')
                    for k,v in zip(('Task','Dataset','Metric'),parts[:3]):expected[k]=v
                    branch='tuple_mapped'
                else:branch='unmatched_preserved'
            assert loc['normalized_tdm']==expected;event.update(normalized=copy.deepcopy(loc['normalized_tdm']),branch=branch,changed=old!=expected)
        self.event_index+=1;event['event']=self.event_index
        immutable(self.out/'events'/f'{self.event_index:04d}.json',event)
        self.events.append(event)
        save(self.out/'checkpoint.json',{'status':'RUNNING','event':self.event_index,'paper':p['paper'],'record':p['record'],'field':p.get('field','TDM'),'last_call':self.call_index,'raw_answer':p.get('raw_answer'),'normalized':event['normalized'],'state_after':event.get('labels_after',{'candidate_order':p.get('candidate_order')}),'resume':'Replay saved responses from start, verify each prompt/state/event; no cross-position semantic cache'})
        self.pending=None

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
        state={'call':index,'status':'PREPARING','position':{k:expected[k] for k in ('paper','record','field')},'prompt_sha256':expected['prompt_sha256'],'candidate_sha256':expected['candidate_sha256'],'requested_model':MODEL}
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

def run_original(module,stage,args,out,mock=None,interrupt_after=None):
    observer=Observer(module,stage,out);transport=Transport(out,observer,mock,interrupt_after);llm=transport.create_mock() if mock is not None else transport.create_live()
    previous=module.utils.llm_init_langchain
    module.utils.llm_init_langchain=lambda config,max_new_tokens,seed:llm
    try:
        sys.settrace(observer.trace);module.main(args)
    finally:
        sys.settrace(None);module.utils.llm_init_langchain=previous
        if transport.client is not None:transport.client.close()
        transport.summary()
    save(Path(out)/'observer_summary.json',{'events':observer.event_index,'requests':transport.cursor,'mock_new_requests':transport.mock_new})
    return observer,transport
