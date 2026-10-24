"""Retrieve only small public official metadata; no authentication, datasets or weights."""
from pathlib import Path
import concurrent.futures,hashlib,json,re
import requests
P=Path(__file__).resolve().parent;DEST=P/'references';DEST.mkdir(exist_ok=True)
URLS={
 'scilead_fixed_tree.json':'https://api.github.com/repos/UKPLab/emnlp2024-leaderboard-generation/git/trees/8bf74b0a830feb7035c6166dce3394dc344ae532?recursive=1',
 'scilead_releases.json':'https://api.github.com/repos/UKPLab/emnlp2024-leaderboard-generation/releases',
 'acl_publication.html':'https://aclanthology.org/2024.emnlp-main.453/',
 'dataset_landing.html':'https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/4345',
}
def fetch(pair):
 name,url=pair
 result={'name':name,'url':url,'authenticated':False,'automatic_retries':0}
 try:
  with requests.Session() as s:
   s.trust_env=False
   with s.get(url,headers={'User-Agent':'SCILEAD-reproduction-scope-audit'},timeout=(5,20),stream=True) as r:
    result.update(http_status=r.status_code,final_url=r.url);r.raise_for_status();data=bytearray()
    for block in r.iter_content(65536):
     data.extend(block)
     if len(data)>2*1024*1024:raise RuntimeError('Metadata size limit')
  (DEST/name).write_bytes(data);result.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
  if name.endswith('.html'):
   links=re.findall(r'href=["\']([^"\']+)',data.decode('utf-8',errors='replace'))
   result['relevant_links']=[x for x in links if any(w in x.lower() for w in ['453','software','supp','zip','github','4345','download'])]
  if name.endswith('.json'):
   obj=json.loads(data)
   if isinstance(obj,dict):result['tree_paths']=[x['path'] for x in obj.get('tree',[])]
   else:result['release_assets']=[{'tag':x.get('tag_name'),'assets':[a['name'] for a in x.get('assets',[])]} for x in obj]
 except Exception as e:result['error_type']=type(e).__name__
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,URLS.items()))
(P/'official_scope_fetch_status.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=True))
