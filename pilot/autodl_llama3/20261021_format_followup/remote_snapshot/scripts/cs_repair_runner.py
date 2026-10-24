"""Engineering repair: expose the same pinned custom-code cache to Transformers."""
from pathlib import Path
import sys,os,json,hashlib,runpy
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];OLD=Path('/root/autodl-tmp/scilead/runs/llama3/20261021_formal42');rev='8079a782f9671d3696b5ab189781480fcca58d25'
hub=R/'cache/hub';src=OLD/'cache/hub/models--dangvantuan--bilingual_impl/snapshots'/rev;dest=hub/'models--dangvantuan--bilingual_impl/snapshots'/rev
proof=[]
for name in ['config.py','modeling.py']:
    data=(src/name).read_bytes();p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    proof.append({'file':name,'sha256':hashlib.sha256(data).hexdigest(),'byte_identical':True})
os.environ.update(TRANSFORMERS_CACHE=str(hub),HF_HUB_CACHE=str(hub),HUGGINGFACE_HUB_CACHE=str(hub),HF_MODULES_CACHE=str(R/'cache/modules'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
from transformers.utils.hub import cached_file
for x in proof:
    p=Path(cached_file('dangvantuan/bilingual_impl',x['file'],revision=rev,local_files_only=True));assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
(R/'audit/cs_cache_repair.json').write_text(json.dumps({'status':'PASS','cause':'Transformers custom-code cache path did not resolve in isolated HF_HOME','no_weight_download_or_version_change':True,'code_files':proof,'revision':rev},indent=2))
if sys.argv[1]=='probe':print('PINNED_OFFLINE_CODE_CACHE_PASS')
else:runpy.run_path(str(R/'scripts/cs_runner.py'),run_name='__main__')
