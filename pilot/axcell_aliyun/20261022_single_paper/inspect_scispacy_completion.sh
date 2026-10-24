set -eu
tail -n 14 /root/scilead/axcell/runs/20261022_single_paper/scispacy_resume.log
python3 - <<'PY'
from pathlib import Path
import tarfile,email,json,gzip
p=Path('/root/scilead/axcell/cache/public_python_artifacts/en_core_sci_sm-0.2.4.tar.gz.verified-temp')
with gzip.open(p,'rb') as f:
 for chunk in iter(lambda:f.read(1024*1024),b''):pass
print('GZIP_CRC_PASS')
with tarfile.open(p,'r:gz') as tf:
 for member in tf.getmembers():
  if member.name.endswith('/PKG-INFO'):
   m=email.message_from_bytes(tf.extractfile(member).read());print(json.dumps({'path':member.name,'Name':m['Name'],'Version':m['Version']}))
PY
