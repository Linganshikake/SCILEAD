"""Temporary loopback-only SSH transport for public official PyPI; no package installation."""
import hashlib,http.server,json,re,select,socket,threading,time,urllib.parse,sys
from pathlib import Path
LOCAL=Path(__file__).resolve().parent
CACHE=Path(r'E:\SCILEAD\axcell\cache\aliyun_pypi_transport')
sys.path.append(r'D:\miniconda3\envs\scilead\Lib\site-packages')
import remote,requests
STOP=LOCAL/'pypi_transport.stop';assert not STOP.exists()
CACHE.mkdir(parents=True,exist_ok=True)
locks={};guard=threading.Lock();started=time.monotonic();remote_port=0
def log(row):
 with guard:
  with (LOCAL/'pypi_transport_downloads.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
def fetch(url,index=False):
 key=hashlib.sha256(url.encode()).hexdigest();p=CACHE/key
 with guard:lock=locks.setdefault(key,threading.Lock())
 with lock:
  if p.exists():return p
  s=requests.Session();s.trust_env=False
  headers={'Accept':'text/html' if index else 'application/octet-stream','Accept-Encoding':'identity'}
  with s.get(url,headers=headers,timeout=(15,45),stream=True,allow_redirects=False) as r:
   r.raise_for_status();assert r.status_code==200
   part=p.with_suffix('.part');count=0;h=hashlib.sha256();begin=time.monotonic()
   with part.open('wb') as f:
    for block in r.iter_content(1024*1024):
     count+=len(block);assert count<500*1024*1024 and time.monotonic()-begin<300
     f.write(block);h.update(block)
   part.replace(p)
  log({'official_url':url,'bytes':count,'sha256':h.hexdigest(),'cache_file':key,'kind':'index' if index else 'artifact'})
  return p
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  try:
   path=urllib.parse.urlsplit(self.path).path
   if re.fullmatch(r'/simple/[A-Za-z0-9._-]+/',path):
    p=fetch('https://pypi.org'+path,True)
    body=p.read_bytes().replace(b'https://files.pythonhosted.org/',('http://127.0.0.1:'+str(remote_port)+'/files/').encode())
    self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
   elif path.startswith('/files/packages/') and '..' not in path:
    p=fetch('https://files.pythonhosted.org/'+path[len('/files/'):])
    self.send_response(200);self.send_header('Content-Length',str(p.stat().st_size));self.send_header('Content-Type','application/octet-stream');self.end_headers()
    with p.open('rb') as f:
     for block in iter(lambda:f.read(1024*1024),b''):self.wfile.write(block)
   else:self.send_error(404)
  except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
  except Exception as e:
   log({'error_type':type(e).__name__,'route':self.path[:200]});self.send_error(502,'Public package transport failed')
def pipe(channel,local_port):
 s=socket.create_connection(('127.0.0.1',local_port),timeout=20)
 try:
  while not STOP.exists():
   ready,_,_=select.select([s,channel],[],[],5)
   for src in ready:
    data=src.recv(65536)
    if not data:return
    (channel if src is s else s).sendall(data)
 finally:s.close();channel.close()
def main():
 global remote_port
 t=remote.connect();http_server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
 threading.Thread(target=http_server.serve_forever,daemon=True).start()
 remote_port=t.request_port_forward('127.0.0.1',0)
 config={'remote_bind':'127.0.0.1','remote_port':remote_port,'index_url':'http://127.0.0.1:'+str(remote_port)+'/simple','upstream':'https://pypi.org/simple','artifact_upstream':'https://files.pythonhosted.org','ssh_host_key_pinned':True,'public_listening':False,'max_lifetime_seconds':1800}
 (LOCAL/'pypi_transport_config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
 print(json.dumps(config),flush=True)
 try:
  while t.is_active() and not STOP.exists() and time.monotonic()-started<1800:
   channel=t.accept(2)
   if channel is not None:threading.Thread(target=pipe,args=(channel,http_server.server_port),daemon=True).start()
 finally:
  t.cancel_port_forward('127.0.0.1',remote_port);http_server.shutdown();http_server.server_close();t.close();print('Temporary PyPI SSH transport closed.',flush=True)
if __name__=='__main__':main()
