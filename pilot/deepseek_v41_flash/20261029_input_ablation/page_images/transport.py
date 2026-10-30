"""DeepSeek official transport. Durable attempts, no automatic retry or fallback."""
import hashlib,json,os,re,time,sys
from pathlib import Path
from datetime import datetime,timezone
import httpx
ROOT=Path(__file__).resolve().parent
ENV=Path(r'D:\C++\SCILEAD\deepseek.env')
MODEL='deepseek-flash'
BASE='https://api.deepseek.com'
DOCUMENTED_VERSION='DeepSeek-V4.1-Flash-1017'
ACCEPTED_MODELS={MODEL,DOCUMENTED_VERSION,DOCUMENTED_VERSION.lower()}

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def save(p,value):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 temp=p.with_name(p.name+'.tmp');text=json.dumps(value,ensure_ascii=False,indent=2)
 for i in range(20):
  try:temp.write_text(text,encoding='utf8');os.replace(temp,p);return
  except PermissionError:
   if i==19:raise
   time.sleep(min(.05*(i+1),.25))

def load_credentials():
 text=ENV.read_text(encoding='utf-8-sig')
 keys=re.findall(r'(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]+',text)
 urls=re.findall(r'https://[^\s\"\'<>]+',text)
 if len(set(keys))!=1 or len(set(urls))!=1 or urls[0].rstrip('/')!=BASE:raise ValueError('UNEXPECTED_CREDENTIAL_STRUCTURE')
 return keys[0],BASE

def payload(messages):
 return {'model':MODEL,'messages':messages,'thinking':{'type':'enabled'},'reasoning_effort':'high','stream':False}

def validate(response,extraction):
 if response.get('model') not in ACCEPTED_MODELS:raise ValueError('RESPONSE_MODEL_MISMATCH')
 choices=response.get('choices',[])
 if len(choices)!=1:raise ValueError('INVALID_CHOICES')
 c=choices[0];m=c.get('message',{})
 if c.get('finish_reason')!='stop':raise ValueError('NON_STOP_FINISH')
 if m.get('tool_calls') or m.get('function_call') or m.get('refusal'):raise ValueError('TOOL_OR_REFUSAL')
 text=m.get('content')
 if not isinstance(text,str) or not text.strip():raise ValueError('EMPTY_CONTENT')
 if not extraction:return text
 from result_compat import convert
 rows,_=convert(text)
 return rows

def one_request(client,folder,payload,key,url):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 if url!=BASE+'/chat/completions' or payload.get('model')!=MODEL:raise ValueError('UNEXPECTED_TARGET')
 if set(payload)!={'model','messages','thinking','reasoning_effort','stream'}:raise ValueError('UNEXPECTED_REQUEST_FIELDS')
 if payload!=globals()['payload'](payload['messages']):raise ValueError('PARAMETER_DRIFT')
 with (folder/'attempt.lock').open('x',encoding='utf8') as f:f.write(now())
 save(folder/'request.json',payload)
 state={'status':'SENDING','started_utc':now(),'post_calls':1,'automatic_retries':0,'endpoint':url,'request_model':MODEL}
 save(folder/'state.json',state);start=time.monotonic()
 try:r=client.post(url,json=payload,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 except httpx.HTTPError as e:
  state.update(status='UNKNOWN_TRANSPORT_ERROR',error_type=type(e).__name__,elapsed_seconds=time.monotonic()-start)
  save(folder/'state.json',state);raise RuntimeError(type(e).__name__) from None
 raw=r.text;redacted=key in raw
 if redacted:raw=raw.replace(key,'[REDACTED_CREDENTIAL]')
 (folder/'response_raw.txt').write_text(raw,encoding='utf8')
 state.update(http_status=r.status_code,elapsed_seconds=time.monotonic()-start,credential_redaction_applied=redacted,
  headers={k:v for k,v in r.headers.items() if k.lower() in {'x-request-id','request-id','retry-after','content-type','date'}})
 try:body=json.loads(raw);save(folder/'response.json',body)
 except ValueError:body={}
 choices=body.get('choices') or []
 state.update(response_model=body.get('model'),usage=body.get('usage'),response_id=body.get('id'),system_fingerprint=body.get('system_fingerprint'),finish_reason=choices[0].get('finish_reason') if choices else None)
 state['status']='RECEIVED' if r.status_code==200 else 'HTTP_ERROR';save(folder/'state.json',state)
 if r.status_code!=200:raise RuntimeError('HTTP_'+str(r.status_code))
 if redacted:raise RuntimeError('CREDENTIAL_ECHO_REDACTED')
 return body
