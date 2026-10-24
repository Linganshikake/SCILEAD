import requests,json,time,hashlib,zipfile,email
from pathlib import Path
OUT=Path(r'E:\SCILEAD\axcell\cache\aliyun_python_artifacts')
REPORT=Path(__file__).resolve().parent/'cpu_wheel_artifacts.json'
items=[('torch','1.3.1+cpu','torch-1.3.1+cpu-cp37-cp37m-linux_x86_64.whl',111810291),('torchvision','0.4.2+cpu','torchvision-0.4.2+cpu-cp37-cp37m-linux_x86_64.whl',13547528)]
def main():
 OUT.mkdir(parents=True,exist_ok=True);rows=[]
 s=requests.Session();s.trust_env=False
 for name,version,filename,size in items:
  p=OUT/filename;url='https://download.pytorch.org/whl/cpu/'+filename.replace('+','%2B');start=time.monotonic()
  if not p.exists():
   part=p.with_suffix(p.suffix+'.part');assert not part.exists(),'Preserve incomplete attempt for inspection'
   with s.get(url,stream=True,timeout=(15,45),allow_redirects=False) as r:
    r.raise_for_status();assert r.status_code==200 and int(r.headers['Content-Length'])==size
    with part.open('xb') as f:
     tick=time.monotonic()
     for block in r.iter_content(1024*1024):
      if time.monotonic()-start>1200:raise TimeoutError('Bounded official CPU wheel transfer timeout')
      f.write(block)
      if time.monotonic()-tick>30:print(json.dumps({'file':filename,'bytes':f.tell(),'total':size}),flush=True);tick=time.monotonic()
   assert part.stat().st_size==size;part.rename(p)
  assert p.stat().st_size==size
  with zipfile.ZipFile(p) as z:
   names=[x for x in z.namelist() if x.endswith('.dist-info/METADATA')];assert len(names)==1
   meta=email.message_from_bytes(z.read(names[0]));assert meta['Name'].lower()==name and meta['Version']==version
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
  row={'name':name,'version':version,'file':filename,'local_path':str(p),'source_url':url,'bytes':size,'sha256':h.hexdigest(),'hash_origin':'computed from official HTTPS file; not an upstream published checksum','seconds':round(time.monotonic()-start,2)}
  rows.append(row);REPORT.write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(row),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'error_type':type(e).__name__,'stage':'official_cpu_wheel_prefetch'}));raise SystemExit(1)
