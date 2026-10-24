set -eu
python3 - <<'PY'
import urllib.request,urllib.error,json
urls=['https://download.pytorch.org/whl/cpu/torch-1.3.1%2Bcpu-cp37-cp37m-linux_x86_64.whl','https://download.pytorch.org/whl/cpu/torchvision-0.4.2%2Bcpu-cp37-cp37m-linux_x86_64.whl','https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz','https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz']
for u in urls:
 try:
  with urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=15) as r:print(json.dumps({'url':u,'status':r.status,'content_length':r.headers.get('Content-Length')}),flush=True)
 except urllib.error.HTTPError as e:print(json.dumps({'url':u,'http_status':e.code}),flush=True)
 except Exception as e:print(json.dumps({'url':u,'error_type':type(e).__name__}),flush=True)
PY
