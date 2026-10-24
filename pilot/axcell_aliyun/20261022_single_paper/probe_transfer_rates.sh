set -eu
python3 - <<'PY'
import subprocess,json,concurrent.futures
urls=[
('scispacy_regional','https://s3.us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz'),
('scispacy_bucket','https://ai2-s2-scispacy.s3.us-west-2.amazonaws.com/releases/v0.2.4/en_core_sci_sm-0.2.4.tar.gz'),
('torch_official','https://download.pytorch.org/whl/cpu/torch-1.3.1%2Bcpu-cp37-cp37m-linux_x86_64.whl')]
def probe(item):
 name,url=item
 p=subprocess.run(['curl','--silent','--show-error','--range','0-262143','--max-time','20','--connect-timeout','10','--output','/dev/null','--write-out','%{http_code} %{size_download} %{speed_download} %{time_total}',url],capture_output=True,text=True)
 return {'source':name,'exit_code':p.returncode,'http_bytes_bytesPerSec_seconds':p.stdout}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for row in pool.map(probe,urls):print(json.dumps(row))
PY
