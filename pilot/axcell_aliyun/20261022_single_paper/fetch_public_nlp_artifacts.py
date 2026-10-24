"""Official pinned dependency artifacts; transport fallback without environment changes."""
from pathlib import Path
from urllib.parse import urlparse,urljoin
import requests,json,hashlib,time,tarfile,email

OUT=Path(__file__).resolve().parent
CACHE=Path(r'E:\SCILEAD\axcell\cache\aliyun_python_artifacts')
ARTIFACTS=[('https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz',12013172,'en-core-web-sm','2.2.5'),('https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz',17042664,'en-core-sci-sm','0.2.4')]
ALLOWED={'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com','s3-us-west-2.amazonaws.com'}
s=requests.Session();s.trust_env=False
def get(url):
 for _ in range(6):
  assert urlparse(url).scheme=='https' and urlparse(url).hostname in ALLOWED
  r=s.get(url,stream=True,allow_redirects=False,timeout=(15,45))
  if r.is_redirect:url=urljoin(url,r.headers['Location']);r.close();continue
  r.raise_for_status();return r
 raise RuntimeError('Redirect limit')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 CACHE.mkdir(parents=True,exist_ok=True);rows=[]
 for url,size,name,version in ARTIFACTS:
  p=CACHE/Path(urlparse(url).path).name;start=time.monotonic()
  if not p.exists():
   for attempt in range(4):
    try:
     with get(url) as response,p.with_suffix(p.suffix+'.part').open('wb') as f:
      for chunk in response.iter_content(1024*1024):f.write(chunk)
     part=p.with_suffix(p.suffix+'.part');assert part.stat().st_size==size;part.replace(p);break
    except Exception as e:
     print(json.dumps({'artifact':p.name,'attempt':attempt+1,'error_type':type(e).__name__}),flush=True)
     if attempt==3:raise
     time.sleep([3,8,15][attempt])
  assert p.stat().st_size==size
  with tarfile.open(p,'r:gz') as tf:
   info=next(m for m in tf.getmembers() if m.isfile() and m.name.endswith('/PKG-INFO'))
   metadata=email.message_from_bytes(tf.extractfile(info).read())
   assert metadata['Name'].replace('_','-')==name and metadata['Version']==version
  row={'source_url':url,'local_path':str(p),'name':name,'version':version,'bytes':size,'sha256':digest(p),'checksum_origin':'locally computed from official HTTPS download; remote transfer must match','seconds':round(time.monotonic()-start,2)}
  rows.append(row);print(json.dumps({k:v for k,v in row.items() if k not in ('source_url','local_path')}),flush=True)
  (OUT/'public_nlp_artifacts.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'sensitive_exception_details_suppressed':True}));raise SystemExit(1)
