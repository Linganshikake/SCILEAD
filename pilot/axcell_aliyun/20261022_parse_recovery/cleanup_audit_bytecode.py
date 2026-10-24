"""Remove only bytecode created by this read-only audit, restoring source layout."""
import datetime,hashlib,json,shutil
from pathlib import Path
R=Path('/root/scilead/axcell/runs/20261022_parse_recovery')
p=Path('/root/scilead/axcell/source/axcell/axcell/scripts/__pycache__/guess_main.cpython-310.pyc')
assert p.resolve()==p and p.is_file()
st=p.stat();stamp=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat()
assert stamp=='2026-10-22T09:27:49.108213+00:00' and st.st_size==2267
out=R/'audit_housekeeping';out.mkdir(exist_ok=True)
shutil.copy2(p,out/p.name)
h=hashlib.sha256(p.read_bytes()).hexdigest();p.unlink()
removed_empty_dir=False
if not any(p.parent.iterdir()):p.parent.rmdir();removed_empty_dir=True
d={'path':str(p),'bytes':st.st_size,'sha256':h,'created_by':'input_audit_remote.py import of original main-file selector','removed_only_task_created_bytecode':not p.exists(),'removed_empty_pycache_directory':removed_empty_dir,'source_text_modified':False,'future_dont_write_bytecode':True}
(R/'audit_housekeeping.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
