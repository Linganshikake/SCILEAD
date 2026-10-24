import hashlib,json,urllib.parse
from html.parser import HTMLParser
from pathlib import Path
BASE=Path(__file__).resolve().parent;CACHE=Path(r'E:\SCILEAD\axcell\cache\aliyun_pypi_transport')
records=[json.loads(x) for x in (BASE/'pypi_transport_downloads.jsonl').read_text(encoding='utf-8').splitlines()]
links={}
class Parser(HTMLParser):
 def handle_starttag(self,tag,attrs):
  if tag!='a':return
  href=dict(attrs).get('href','');url,fragment=urllib.parse.urldefrag(href)
  sha=urllib.parse.parse_qs(fragment).get('sha256')
  if sha:links[url]=sha[0]
for row in records:
 if row.get('kind')=='index':
  data=(CACHE/row['cache_file']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];Parser().feed(data.decode('utf-8'))
checks=[]
for row in records:
 if row.get('kind')!='artifact':continue
 p=CACHE/row['cache_file'];h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 expected=links.get(row['official_url'])
 ok=h.hexdigest()==row['sha256']==expected and p.stat().st_size==row['bytes']
 checks.append({'official_url':row['official_url'],'bytes':row['bytes'],'sha256':h.hexdigest(),'official_index_sha256':expected,'match':ok})
d={'all_public_artifacts_match_official_pypi_index':all(x['match'] for x in checks),'artifact_count':len(checks),'includes_resolver_candidates_not_necessarily_installed':True,'download_errors_logged':sum('error_type' in x for x in records),'checks':checks}
(BASE/'pypi_transport_integrity.json').write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in d.items() if k!='checks'}));assert d['all_public_artifacts_match_official_pypi_index']
