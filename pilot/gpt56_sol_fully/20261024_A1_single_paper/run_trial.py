"""One approved paper only. No automatic retry, fallback, retrieval or evaluation."""
import argparse
import ast
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx

ROOT=Path(__file__).resolve().parent
A0=ROOT.parent/'20261024_A0_preparation'
ENV=Path(r'D:\C++\SCILEAD\SCILEAD_small_test\.env')
MODEL='gpt-5.6-sol'
PAPER='2020.emnlp-main.152.pdf'

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_name(p.name+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temp,p)
def now():return datetime.now(timezone.utc).isoformat()

def validate(response,extraction):
    if response.get('model')!=MODEL:raise ValueError('RESPONSE_MODEL_MISMATCH')
    choices=response.get('choices',[])
    if len(choices)!=1:raise ValueError('INVALID_CHOICES')
    choice=choices[0];msg=choice.get('message',{})
    if choice.get('finish_reason')!='stop':raise ValueError('NON_STOP_FINISH')
    if msg.get('tool_calls') or msg.get('function_call') or msg.get('refusal'):raise ValueError('TOOL_OR_REFUSAL')
    text=msg.get('content')
    if not isinstance(text,str) or not text.strip():raise ValueError('EMPTY_CONTENT')
    if not extraction:return text
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('DUPLICATE_JSON_KEY')
            d[k]=v
        return d
    rows=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('NONFINITE')))
    if not isinstance(rows,list):raise ValueError('NOT_ARRAY')
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'Task','Dataset','Metric','Result'}:raise ValueError('INVALID_FIELDS')
        if not all(isinstance(v,str) for v in row.values()):raise ValueError('INVALID_FIELD_TYPES')
    return rows

def one_request(client,folder,payload,key,url):
    folder.mkdir(parents=True,exist_ok=True)
    # Durable exclusive marker blocks every attempted resend, including UNKNOWN.
    with (folder/'attempt.lock').open('x',encoding='utf-8') as f:f.write(now())
    save(folder/'request.json',payload)
    state={'status':'SENDING','started_utc':now(),'post_calls':1,'automatic_retries':0,'endpoint':url}
    save(folder/'state.json',state)
    start=time.monotonic()
    try:
        response=client.post(url,json=payload,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    except httpx.HTTPError as e:
        state.update(status='UNKNOWN_TRANSPORT_ERROR',error_type=type(e).__name__,elapsed_seconds=time.monotonic()-start)
        save(folder/'state.json',state)
        raise RuntimeError(type(e).__name__) from None
    raw=response.text
    redacted=key in raw
    if redacted:raw=raw.replace(key,'[REDACTED_CREDENTIAL]')
    (folder/'response_raw.txt').write_text(raw,encoding='utf-8')
    state.update(http_status=response.status_code,elapsed_seconds=time.monotonic()-start,credential_redaction_applied=redacted,
                 headers={k:v for k,v in response.headers.items() if k.lower() in {'x-request-id','request-id','retry-after','content-type','date'}})
    try:
        body=json.loads(raw);save(folder/'response.json',body)
    except ValueError:body={}
    state.update(response_model=body.get('model'),usage=body.get('usage'),response_id=body.get('id'))
    state['status']='RECEIVED' if response.status_code==200 else 'HTTP_ERROR'
    save(folder/'state.json',state)
    if response.status_code!=200:raise RuntimeError('HTTP_'+str(response.status_code))
    if redacted:raise RuntimeError('CREDENTIAL_ECHO_REDACTED')
    return body

def payload(messages):
    return {'model':MODEL,'messages':messages,'reasoning_effort':'medium','max_completion_tokens':32768,'stream':False}

def main(execute):
    protected=load(A0/'delivery_manifest.json')
    assert all(digest(A0/p)==h for p,h in protected.items()),'A0_HASH_MISMATCH'
    source=A0/'inputs'/PAPER
    docs=load(source/'source_documents.json');messages=load(source/'extraction_messages.json')
    prompts=load(A0/'frozen_prompts.json');candidate_strings=load(A0/'candidate_sets.json')
    candidates={k:ast.literal_eval(v) for k,v in candidate_strings.items()}
    assert [len(candidates[k]) for k in ['Task','Dataset','Metric']]==[23,71,26]
    assert messages==[{'role':'system','content':prompts['tdm-extraction-system-prompt'].format()},
                     {'role':'user','content':prompts['query']+'\n\nRetrieved document contents:\n\n'+'\n\n'.join(d['content'] for d in docs)+'.\n\n Output json:\n\n'}]
    row=next(r for r in load(A0/'input_manifest.json') if r['paper_id']==PAPER)
    preflight={'paper_id':PAPER,'evidence_count':len(docs),'text_blocks':row['text_blocks'],'table_documents':row['table_documents'],
               'proxy_input_tokens':row['proxy_input_tokens'],'a0_hashes_checked':len(protected),'input_unchanged':True,
               'scope':'One extraction, then this paper only official Fully normalization; stop on any request/structure error',
               'authorization':'User: 可以进行单篇试跑','model':MODEL,'no_retrieval':True,'no_gold_in_extraction':True,
               'network':'Direct TLS verified connection, trust_env=False; historical proxy TLS failures avoided',
               'provider_mapping':'UNVERIFIED until observed; returned ID alone is not independent upstream attestation',
               'generation_parameters':{k:v for k,v in payload(messages).items() if k!='messages'},
               'timeout_seconds':{'connect':20,'read':600,'write':30,'pool':20},'automatic_retries':0}
    save(ROOT/'preflight.json',preflight)
    if not execute:
        print(json.dumps(preflight,ensure_ascii=False));return
    from dotenv import dotenv_values
    env=dotenv_values(ENV,interpolate=False,encoding='utf-8-sig')
    key=next((env[k] for k in ['OPENAI_API_KEY','API_KEY','SK'] if env.get(k)),None)
    base=next((env[k] for k in ['BASE_URL','OPENAI_BASE_URL','API_BASE','OPENAI_API_BASE','API_BASE_URL'] if env.get(k)),None)
    assert key and base and base.rstrip('/') in ['https://9527.codes','https://9527.codes/v1'],'CONFIG_NOT_EXPECTED'
    url=base.rstrip('/')
    if not url.endswith('/v1'):url+='/v1'
    url+='/chat/completions'
    with (ROOT/'execution.lock').open('x',encoding='utf-8') as f:f.write(now())
    save(ROOT/'config.json',preflight)
    save(ROOT/'source_documents.json',docs)
    status='STARTED';error=None;rows=[];normalized=[];start=time.monotonic()
    try:
        with httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,
                          timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20)) as client:
            response=one_request(client,ROOT/'extraction',payload(messages),key,url)
            rows=validate(response,True)
            save(ROOT/'output.json',{PAPER:{'output':response['choices'][0]['message']['content'],'source_documents':docs}})
            save(ROOT/'extraction_validation.json',{'valid':True,'records':len(rows),'finish_reason':'stop'})
            planned=[{'record':i,'field':k,'input':v} for i,r in enumerate(rows) for k,v in r.items() if k!='Result' and v not in candidates[k]]
            save(ROOT/'normalization_request_manifest.json',{'requests':planned,'count':len(planned),'candidates':candidate_strings,'no_duplicate_cache':True})
            print(json.dumps({'extraction':'VALID','records':len(rows),'normalization_requests':len(planned)}),flush=True)
            count=0
            for i,r in enumerate(rows):
                nr={}
                for k,v in r.items():
                    if k=='Result' or v in candidates[k]:nr[k]=str(v);continue
                    count+=1
                    nm=[{'role':'system','content':prompts['normalization-system-prompt']},
                        {'role':'user','content':'\n\nItem list: '+candidate_strings[k]+'\n\nInput: '+v+'\n\nAnswer: '}]
                    folder=ROOT/'normalization'/'requests'/f'{count:03d}_record{i}_{k}'
                    res=one_request(client,folder,payload(nm),key,url)
                    answer=validate(res,False)
                    nr[k]=answer if answer in candidates[k] else None
                    save(folder/'mapping.json',{'record':i,'field':k,'input':v,'raw_answer':answer,'accepted':nr[k],
                                               'reason':'EXACT_CANDIDATE' if nr[k] is not None else 'OUTSIDE_CANDIDATES'})
                    print(json.dumps({'normalization_completed':count,'total':len(planned),'accepted':nr[k] is not None}),flush=True)
                normalized.append(nr);save(ROOT/'normalization'/'partial_output.json',normalized)
            save(ROOT/'normalization'/'normalized_output.json',{PAPER:{'normalized_output':normalized,'source_documents':docs}})
            status='SINGLE_PAPER_COMPLETE'
    except Exception as e:
        # Avoid exception repr: transport/server objects may carry request headers.
        status='STOPPED';error={'type':type(e).__name__,'code':str(e).replace(key,'[REDACTED]')[:300]}
        save(ROOT/'failure.json',error)
    finally:
        states=[load(p) for p in sorted(ROOT.rglob('state.json'))]
        usage={k:sum((s.get('usage') or {}).get(k,0) or 0 for s in states) for k in ['prompt_tokens','completion_tokens','total_tokens']}
        usage.update(request_attempts=len(states),http_200=sum(s.get('http_status')==200 for s in states),unknown_usage_requests=sum(s.get('usage') is None for s in states),elapsed_seconds=time.monotonic()-start)
        save(ROOT/'api_usage.json',usage)
        unchanged=all(digest(A0/p)==h for p,h in protected.items())
        secret_free=all(key.encode() not in p.read_bytes() for p in ROOT.rglob('*') if p.is_file())
        verification={'status':status,'paper_id':PAPER,'records':len(rows),'normalized_records':len(normalized),'a0_hashes_unchanged':unchanged,
                      'secret_scan_passed':secret_free,'no_automatic_retries':True,'no_other_papers':True,'error':error,'api_usage':usage}
        save(ROOT/'verification.json',verification)
        (ROOT/'report.md').write_text('# GPT-5.6 Sol 单篇试跑\n\n'+
            f'论文：{PAPER}。状态：{status}。\n\n'+
            f'实际请求 {len(states)} 次，HTTP 200 {usage["http_200"]} 次；抽取 {len(rows)} 条，完成标准化 {len(normalized)} 条。\n\n'+
            f'已报告 Tokens：{usage["total_tokens"]}；未返回用量的请求 {usage["unknown_usage_requests"]} 次，不能推断未计费。\n\n'+
            f'错误：{json.dumps(error,ensure_ascii=False)}。A0文件完整性：{unchanged}。\n\n'+
            '仅使用单篇冻结证据；未重做检索、未调用其他模型、未修改Prompt、未修复预测；未开始全量实验。\n\n'+
            '请求参数与响应均保存在各请求目录。reasoning_effort实际服务端执行情况、底层模型身份无法仅由HTTP成功独立证明。\n',encoding='utf-8')
        print(json.dumps(verification,ensure_ascii=False),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true')
    main(parser.parse_args().execute)
