"""Download allowlisted public documentation only; no keys, API endpoints or POST."""
from pathlib import Path
import httpx,json,hashlib,datetime
O=Path(__file__).resolve().parent;D=O/'official_docs';D.mkdir(exist_ok=True)
paths={'model':'/api/docs/models/gpt-5.6-sol','pricing':'/api/docs/pricing','responses':'/api/reference/resources/responses/methods/create','reasoning':'/api/docs/guides/reasoning','chat_completions':'/api/reference/resources/chat/subresources/completions/methods/create'}
records=[]
with httpx.Client(trust_env=False,follow_redirects=False,timeout=httpx.Timeout(30,connect=15)) as c:
    for name,path in paths.items():
        url='https://developers.openai.com'+path+'.md';row={'title':name,'requested_url':url,'documentation_url':'https://developers.openai.com'+path,'queried_date':'2026-10-24','method':'GET','authentication':False}
        try:
            with c.stream('GET',url,headers={'Accept':'text/markdown,text/plain,text/html'}) as response:
                row['http_status']=response.status_code;row['content_type']=response.headers.get('content-type');body=bytearray()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body)>12_000_000:raise ValueError('DOCUMENT_TOO_LARGE')
                if response.status_code==200:
                    target=D/(name+'.md');target.write_bytes(body);row.update(file=str(target),bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
                else:row['saved']=False
        except Exception as e:row['error_type']=type(e).__name__
        records.append(row);print(json.dumps(row),flush=True)
        (D/'retrieval_manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
