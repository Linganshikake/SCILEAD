"""Small strict adaptation of the verified scilead_api durable ledger.
No normalization decisions here; official tdm_llm_normalization remains responsible.
"""
import json,time,hashlib
from pathlib import Path
import httpx,openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
MODEL='gpt-4.1-2025-04-14';BASE='https://9527.codes/v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class FrozenLedger:
    def __init__(self,root,plan,key,transport=None,network_switch=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.plan=plan;self.key=key;self.cursor=0;self.active=None;self.network_switch=network_switch or (lambda active:None)
        self.timeout=httpx.Timeout(connect=20,read=180,write=30,pool=20)
        self.http=httpx.Client(timeout=self.timeout,follow_redirects=False,transport=transport,event_hooks={'request':[self.request_hook],'response':[self.response_hook]})
        sdk=openai.OpenAI(api_key=key,base_url=BASE,organization='',project='',max_retries=0,timeout=self.timeout,http_client=self.http)
        self.llm=ChatOpenAI(model=MODEL,api_key=key,base_url=BASE,temperature=0,max_tokens=None,model_kwargs={'seed':0},max_retries=0,timeout=self.timeout,client=sdk.chat.completions,async_client=object(),cache=False)
    def scrub(self,x):
        if isinstance(x,str):return x.replace(self.key,'[REDACTED]') if self.key else x
        if isinstance(x,list):return [self.scrub(v) for v in x]
        if isinstance(x,dict):return {k:('[REDACTED]' if k.lower() in ('authorization','api_key','x-api-key') else self.scrub(v)) for k,v in x.items()}
        return x
    def save(self,path,x):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(self.scrub(x),ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)
    def request_hook(self,request):
        a=self.active;payload=json.loads(request.content)
        assert request.method=='POST' and str(request.url)==BASE+'/chat/completions'
        assert payload==a['item']['payload'],'Actual SDK wire payload differs from approved P4'
        assert payload['model']==MODEL and not any(k in payload for k in ('max_tokens','max_output_tokens','max_completion_tokens','response_format','tools'))
        with (a['folder']/'attempt.json').open('x',encoding='utf-8') as f:json.dump({'time_epoch':time.time(),'attempt':1,'request_id':a['item']['request_id'],'billing_unknown_until_response':True},f)
        a['state'].update(status='ATTEMPTED',attempts=1)
        self.save(a['folder']/'request.json',payload);self.save(a['folder']/'state.json',a['state'])
    def response_hook(self,response):
        a=self.active;response.read()
        try:body=response.json()
        except ValueError:body={'body_text':response.text}
        self.save(a['folder']/'response.json',body)
        a['state'].update(http_status=response.status_code,server_request_id=response.headers.get('x-request-id') or response.headers.get('request-id'),response_sha256=sha(a['folder']/'response.json'))
        if 200<=response.status_code<300:
            choice=(body.get('choices') or [{}])[0]
            a['state'].update(returned_model=body.get('model'),response_id=body.get('id'),usage=body.get('usage') or {},finish_reason=choice.get('finish_reason'),system_fingerprint=body.get('system_fingerprint'))
            assert body.get('model')==MODEL,'Unexpected response model; do not switch or accept substitute'
            assert len(body.get('choices',[]))==1 and choice.get('finish_reason')=='stop','Non-stop or incomplete response'
            assert isinstance(choice.get('message',{}).get('content'),str),'Missing text response'
        self.save(a['folder']/'state.json',a['state'])
    def invoke(self,prompt):
        assert self.cursor<len(self.plan),'More invocations than authorized'
        messages=prompt.to_messages() if hasattr(prompt,'to_messages') else prompt
        wire=[{'role':{'system':'system','human':'user','ai':'assistant'}[m.type],'content':m.content} if not isinstance(m,dict) else m for m in messages]
        item=self.plan[self.cursor];assert wire==item['payload']['messages'],'Messages differ from P4'
        folder=self.root/item['request_id'];folder.mkdir(exist_ok=True);statepath=folder/'state.json'
        if statepath.exists():
            old=json.loads(statepath.read_text(encoding='utf-8'));assert old['checkpoint_cache_key']==item['checkpoint_cache_key']
            if old['status']=='COMPLETE':
                assert json.loads((folder/'request.json').read_text(encoding='utf-8'))==item['payload']
                assert sha(folder/'response.json')==old['response_sha256'] and old['finish_reason']=='stop' and old['returned_model']==MODEL
                body=json.loads((folder/'response.json').read_text(encoding='utf-8'));assert body['choices'][0]['message']['content']==old['raw_answer']
                self.cursor+=1;return AIMessage(content=old['raw_answer'])
        if (folder/'attempt.json').exists():raise RuntimeError('Attempt exists without validated completion; automatic retry forbidden')
        state={'request_id':item['request_id'],'checkpoint_cache_key':item['checkpoint_cache_key'],'status':'PREPARING','model':MODEL,'attempts':0,'started_epoch':time.time()}
        self.active={'item':item,'folder':folder,'state':state};start=time.monotonic()
        try:
            self.network_switch(True)
            answer=self.llm.invoke(messages)
            self.network_switch(False)
            assert state.get('http_status')==200 and state.get('finish_reason')=='stop'
            state.update(status='COMPLETE',raw_answer=answer.content,billing_unknown=not bool(state.get('usage')))
            self.cursor+=1
            return answer
        except Exception as exc:
            state.update(status='FAILED',error_type=type(exc).__name__,error=self.scrub(str(exc)),billing_unknown=not bool(state.get('usage')))
            raise
        finally:
            self.network_switch(False);state['seconds']=round(time.monotonic()-start,3);self.save(statepath,state)
            print(f"{item['request_id']} {state['status']} {state.get('http_status','NO_HTTP')} {state['seconds']}s",flush=True)
    def close(self):self.http.close()
