import requests,json,concurrent.futures
digest='sha256:a0115e92049eae8a83d89f119c23b69720f2e94af7bf97d170b7316eb0a6ff5b'
def probe(repo):
 s=requests.Session();s.trust_env=False
 try:
  a=s.get('https://auth.docker.io/token',params={'service':'registry.docker.io','scope':'repository:'+repo+':pull'},timeout=(10,20));a.raise_for_status();token=a.json()['token']
  r=s.get('https://registry-1.docker.io/v2/'+repo+'/manifests/'+digest,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.docker.distribution.manifest.v2+json'},timeout=(10,20))
  return {'repository':repo,'status':r.status_code,'docker_content_digest':r.headers.get('Docker-Content-Digest'),'same_fixed_digest':r.status_code==200 and r.headers.get('Docker-Content-Digest')==digest}
 except Exception as e:return {'repository':repo,'error_type':type(e).__name__}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 rows=list(pool.map(probe,['elastic/elasticsearch-oss','elastic/elasticsearch','library/elasticsearch']))
 print(json.dumps(rows))
