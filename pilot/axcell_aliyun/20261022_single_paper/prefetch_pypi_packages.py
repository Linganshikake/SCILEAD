import requests,json,hashlib,time,concurrent.futures
from pathlib import Path
OUT=Path(r'E:\SCILEAD\axcell\cache\aliyun_python_artifacts');LOCAL=Path(__file__).resolve().parent
ITEMS=[('scikit-learn','0.21.3'),('regex','2019.11.1'),('scispacy','0.2.4'),('psutil','5.6.7'),('fastai','1.0.55'),('fastprogress','0.1.21')]
def fetch(item):
 name,version=item;s=requests.Session();s.trust_env=False
 r=s.get('https://pypi.org/pypi/'+name+'/'+version+'/json',timeout=(15,45));r.raise_for_status();meta=r.json()
 accepted=['cp37-cp37m-manylinux1_x86_64.whl','cp37-cp37m-manylinux2010_x86_64.whl','py3-none-any.whl','py2.py3-none-any.whl']
 files=[x for x in meta['urls'] if any(x['filename'].endswith(tag) for tag in accepted)]
 if not files:files=[x for x in meta['urls'] if x['packagetype']=='sdist']
 assert len(files)==1,(name,len(files));data=files[0];p=OUT/data['filename'];start=time.monotonic()
 if not p.exists():
  part=p.with_suffix(p.suffix+'.part');assert not part.exists()
  assert data['url'].startswith('https://files.pythonhosted.org/')
  with s.get(data['url'],stream=True,timeout=(15,45),allow_redirects=False) as response,part.open('xb') as out:
   response.raise_for_status();assert response.status_code==200
   for block in response.iter_content(1024*1024):out.write(block)
  assert part.stat().st_size==data['size'] and hashlib.sha256(part.read_bytes()).hexdigest()==data['digests']['sha256'];part.rename(p)
 assert p.stat().st_size==data['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==data['digests']['sha256']
 row={'name':name,'version':version,'file':p.name,'local_path':str(p),'source_url':data['url'],'bytes':data['size'],'sha256':data['digests']['sha256'],'hash_origin':'official PyPI release JSON SHA256','requires_python':data.get('requires_python'),'seconds':round(time.monotonic()-start,2)}
 print(json.dumps({'package':name,'version':version,'file':p.name,'bytes':data['size'],'official_sha256_verified':True}),flush=True);return row
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(fetch,ITEMS))
 (LOCAL/'pypi_package_artifacts.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'error_type':type(e).__name__}));raise SystemExit(1)
