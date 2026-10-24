"""Bounded range transfer of one public, fixed-version 17 MB dependency archive."""
import concurrent.futures,email,gzip,hashlib,json,tarfile,time,urllib.request,re
from pathlib import Path
ROOT=Path('/root/scilead/axcell');RUN=ROOT/'runs/20261022_single_paper'
P=ROOT/'cache/public_python_artifacts/en_core_sci_sm-0.2.4.tar.gz'
URL='https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz'
TOTAL=17042664
def main():
 start=time.monotonic();partial=P.with_name(P.name+'.part');offset=partial.stat().st_size
 assert not P.exists() and 0<offset<TOTAL
 with urllib.request.urlopen(urllib.request.Request(URL,method='HEAD'),timeout=45) as r:
  assert int(r.headers['Content-Length'])==TOTAL;etag=r.headers['ETag']
 def request_range(a,b):
  r=urllib.request.urlopen(urllib.request.Request(URL,headers={'Range':'bytes={}-{}'.format(a,b),'If-Match':etag}),timeout=45)
  assert r.status==206 and r.headers['Content-Range']=='bytes {}-{}/{}'.format(a,b,TOTAL)
  assert r.headers['ETag']==etag
  return r
 with request_range(0,65535) as r,partial.open('rb') as f:assert r.read()==f.read(65536),'Preserved partial prefix does not match the official object'
 width=(TOTAL-offset+2)//3
 ranges=[(a,min(a+width-1,TOTAL-1)) for a in range(offset,TOTAL,width)]
 (RUN/'scispacy_range_plan.json').write_text(json.dumps({'url':URL,'expected_bytes':TOTAL,'etag_as_http_validator_only':etag,'prefix_bytes':offset,'ranges':ranges,'max_connections':3,'buffer_bytes':65536,'max_attempts_per_range':3},indent=2))
 def fetch(bounds):
  a,b=bounds;dest=P.with_name(P.name+'.range-{}-{}'.format(a,b));done=0
  assert not dest.exists()
  for attempt in range(1,4):
   try:
    with request_range(a+done,b) as response,dest.open('ab') as f:
     while True:
      if time.monotonic()-start>1800:raise TimeoutError('Bounded range transfer deadline')
      block=response.read(min(65536,b-a+1-done))
      if not block:break
      f.write(block);done+=len(block)
      if done==b-a+1:break
    assert done==b-a+1
    print(json.dumps({'range':bounds,'bytes':done,'attempt':attempt,'status':'COMPLETE'}),flush=True)
    return dest
   except (OSError,EOFError) as e:
    print(json.dumps({'range':bounds,'bytes':done,'attempt':attempt,'error_type':type(e).__name__}),flush=True)
    if attempt==3:raise
    time.sleep(3*attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:pieces=list(pool.map(fetch,ranges))
 combined=P.with_name(P.name+'.verified-temp');assert not combined.exists()
 with combined.open('xb') as out:
  for src in [partial]+pieces:
   with src.open('rb') as f:
    for block in iter(lambda:f.read(1024*1024),b''):out.write(block)
 assert combined.stat().st_size==TOTAL
 with gzip.open(combined,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):pass
 with tarfile.open(combined,'r:gz') as tf:
  member=next(x for x in tf.getmembers() if x.name.count('/')==1 and x.name.endswith('/PKG-INFO'))
  meta=email.message_from_bytes(tf.extractfile(member).read());assert re.sub(r'[-_.]+','-',meta['Name'].lower())=='en-core-sci-sm' and meta['Version']=='0.2.4'
 digest=hashlib.sha256(combined.read_bytes()).hexdigest();combined.rename(P)
 result={'file':P.name,'source_url':URL,'expected_bytes':TOTAL,'actual_bytes':P.stat().st_size,'sha256':digest,'hash_origin':'computed from official HTTPS object; not upstream published SHA256','etag_as_http_validator_only':etag,'preserved_prefix_bytes':offset,'range_download_bytes':TOTAL-offset,'seconds':round(time.monotonic()-start,2),'gzip_crc_and_package_metadata_verified':True}
 (RUN/'scispacy_artifact_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
