import hashlib
from pathlib import Path
GIB=2**30
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def disk_guard(free):return 'DISK_RESERVE' if free<20*GIB else None
def start_guard(available,free):return disk_guard(free) or ('START_LOW_MEMORY' if available<6*GIB else None)
def reusable(result,input_sha,config_sha):
    if result.get('input_sha256')!=input_sha or result.get('configuration_sha256')!=config_sha:return False
    artifacts=result.get('artifacts',[])
    return bool(artifacts) and all(Path(x['path']).is_file() and Path(x['path']).stat().st_size==x['bytes'] and sha(x['path'])==x['sha256'] for x in artifacts)
