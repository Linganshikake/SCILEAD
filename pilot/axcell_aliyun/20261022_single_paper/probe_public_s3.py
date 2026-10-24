import requests,concurrent.futures,json
urls=[
'https://s3.us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz',
'https://ai2-s2-scispacy.s3.us-west-2.amazonaws.com/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz',
'https://ai2-s2-scispacy.s3-us-west-2.amazonaws.com/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz']
def probe(url):
 try:
  s=requests.Session();s.trust_env=False;r=s.head(url,timeout=(10,20),allow_redirects=False)
  return {'url':url,'status':r.status_code,'content_length':r.headers.get('Content-Length'),'etag':r.headers.get('ETag')}
 except Exception as e:return {'url':url,'error_type':type(e).__name__}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for result in pool.map(probe,urls):print(json.dumps(result),flush=True)
