"""Public metadata GET only. No credentials, no inference endpoints."""
import urllib.request, json, hashlib, zipfile, io, concurrent.futures
from pathlib import Path
from datetime import datetime, timezone
OUT=Path(__file__).resolve().parent/'public_sources'; OUT.mkdir(exist_ok=True)
SOURCES={
 'software.zip':'https://aclanthology.org/2024.emnlp-main.453.software.zip',
 'data.zip':'https://aclanthology.org/2024.emnlp-main.453.data.zip',
 'fixed_tree.json':'https://api.github.com/repos/UKPLab/emnlp2024-leaderboard-generation/git/trees/8bf74b0a830feb7035c6166dce3394dc344ae532?recursive=1',
 'releases.json':'https://api.github.com/repos/UKPLab/emnlp2024-leaderboard-generation/releases',
}
def fetch(pair):
    name,url=pair; result={'name':name,'url':url,'time_utc':datetime.now(timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'SCILEAD-scope-audit','Accept':'application/json' if name.endswith('.json') else '*/*'})
        with urllib.request.urlopen(req,timeout=20) as r:
            result.update(http_status=r.status,final_url=r.geturl())
            limit=20*1024*1024
            if int(r.headers.get('Content-Length','0'))>limit: raise ValueError('Read-only metadata download exceeds 20MiB limit')
            data=r.read(limit+1)
            if len(data)>limit: raise ValueError('Read-only metadata download exceeds 20MiB limit')
        (OUT/name).write_bytes(data);result.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        if name.endswith('.zip'):
            z=zipfile.ZipFile(io.BytesIO(data)); result['members']=[{'name':v.filename,'bytes':v.file_size} for v in z.infolist()]
            result['scope_mentions']=[]
            for item in z.infolist():
                if item.file_size>4*1024*1024 or item.is_dir():continue
                if Path(item.filename).suffix.lower() not in ('.md','.txt','.json','.csv','.tsv','.py','.yaml','.yml'):continue
                txt=z.read(item).decode('utf-8',errors='replace')
                hits=[{'line':i+1,'text':line[:500]} for i,line in enumerate(txt.splitlines()) if any(k in line.lower() for k in ('axcell','36 tex','36 papers'))]
                if hits:result['scope_mentions'].append({'file':item.filename,'hits':hits[:30]})
        result['status']='FETCHED'
    except Exception as e: result.update(status='UNAVAILABLE',error_type=type(e).__name__,error=str(e))
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(fetch,SOURCES.items()))
(OUT/'fetch_status.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k not in ('members','scope_mentions')} for r in results],ensure_ascii=True))
