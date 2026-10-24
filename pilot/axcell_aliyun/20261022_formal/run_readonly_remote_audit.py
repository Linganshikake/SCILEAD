"""Reuse pinned authentication while saving only a public/resource audit response."""
from pathlib import Path
import json,sys,time
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parent/'20261022_single_paper'))
import remote
def main():
 t=remote.connect()
 try:
  c=t.open_session(timeout=20);c.exec_command('python3 -')
  c.sendall((OUT/'remote_stage0_probe.py').read_bytes());c.shutdown_write()
  data=bytearray();err=bytearray();start=time.monotonic()
  while True:
   if c.recv_ready():data.extend(c.recv(65536))
   if c.recv_stderr_ready():err.extend(c.recv_stderr(65536))
   if c.exit_status_ready() and not c.recv_ready() and not c.recv_stderr_ready():break
   if time.monotonic()-start>180:raise RuntimeError('Readonly audit timeout; no stage launched')
   time.sleep(.05)
  code=c.recv_exit_status()
  if code:
   (OUT/'remote_audit_error.txt').write_bytes(err)
   raise RuntimeError('Readonly audit failed; see local error evidence')
  d=json.loads(data);(OUT/'remote_preflight.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
  summary={'read_only':True,'min_available_gib':round(min(x['memory']['MemAvailable'] for x in d['memory_samples'])/2**30,3),'disk_free_gib':round(d['disk_free_bytes']/2**30,3),'original_assets_match':d['original_assets_match'],'single_paper_unchanged':d['single_paper_run_unchanged'],'package_diff':d['package_diff_from_single_paper'],'pip_check':d['pip_check'],'running_containers':d['running_containers']['stdout'],'elasticsearch':d['elasticsearch_readiness']}
  print(json.dumps(summary))
 finally:t.close()
if __name__=='__main__':main()
