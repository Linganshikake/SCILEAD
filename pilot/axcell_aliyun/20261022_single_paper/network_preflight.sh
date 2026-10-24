set -eu
python3 - <<'PY'
import urllib.request,urllib.error,json,time
urls=['https://conda.anaconda.org/conda-forge/linux-64/repodata.json.zst','https://repo.anaconda.com/pkgs/main/linux-64/repodata.json.zst','https://registry-1.docker.io/v2/','https://auth.docker.io/token?service=registry.docker.io&scope=repository:arxivvanity/engrafo:pull','https://docker.elastic.co/v2/','https://pypi.org/simple/sentencepiece/']
for u in urls:
 t=time.monotonic()
 try:
  with urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=12) as r:d={'url':u.split('?')[0],'status':r.status}
 except urllib.error.HTTPError as e:d={'url':u.split('?')[0],'status':e.code}
 except Exception as e:d={'url':u.split('?')[0],'error_type':type(e).__name__}
 d['seconds']=round(time.monotonic()-t,2);print(json.dumps(d),flush=True)
PY
