"""Fetch only explicitly named public source pages/attachments; never model APIs."""
import urllib.request,urllib.error,hashlib,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
SOURCES={
 'acl_article.html':'https://aclanthology.org/2024.emnlp-main.453/',
 'acl_data.zip':'https://aclanthology.org/2024.emnlp-main.453.data.zip',
 'acl_software.zip':'https://aclanthology.org/2024.emnlp-main.453.software.zip',
 'tudatalib_handle.html':'https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/4345',
 'github_readme.md':'https://raw.githubusercontent.com/UKPLab/emnlp2024-leaderboard-generation/8bf74b0a830feb7035c6166dce3394dc344ae532/README.md',
}
def fetch(item):
    name,url=item;entry={'url':url,'retrieved_epoch':time.time(),'maximum_bytes':2*1024*1024,'kind':'public source GET; not LLM inference'}
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'SCILEAD-Reproduction-Audit/1.0'})
        with urllib.request.urlopen(request,timeout=25) as response:
            entry.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'),declared_size=response.headers.get('Content-Length'))
            content=response.read(entry['maximum_bytes']+1)
            if len(content)>entry['maximum_bytes']:raise ValueError('Source exceeds bounded download size')
            target=ROOT/'downloads'/name;target.write_bytes(content)
            entry.update(path=str(target),bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),status='FETCHED')
    except urllib.error.HTTPError as error:
        entry.update(status='HTTP_ERROR',http_status=error.code,reason=error.reason,final_url=error.url)
    except Exception as error:entry.update(status='FAILED',error_type=type(error).__name__,reason=str(error))
    print(json.dumps(entry,ensure_ascii=False),flush=True);return entry
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,SOURCES.items()))
    (ROOT/'official_fetch_log.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
