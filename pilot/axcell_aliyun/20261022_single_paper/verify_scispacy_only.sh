set -eu
python3 - <<'PY'
import email,gzip,hashlib,json,re,tarfile
from pathlib import Path
r=Path('/root/scilead/axcell');run=r/'runs/20261022_single_paper'
p=r/'cache/public_python_artifacts/en_core_sci_sm-0.2.4.tar.gz.verified-temp'
dest=p.with_name('en_core_sci_sm-0.2.4.tar.gz')
assert not dest.exists() and p.stat().st_size==17042664
with gzip.open(p,'rb') as f:
 for block in iter(lambda:f.read(1024*1024),b''):pass
metadata=[]
with tarfile.open(p,'r:gz') as tf:
 for member in tf.getmembers():
  if member.name.endswith('/PKG-INFO'):
   m=email.message_from_bytes(tf.extractfile(member).read())
   assert re.sub(r'[-_.]+','-',m['Name'].lower())=='en-core-sci-sm' and m['Version']=='0.2.4'
   metadata.append({'name':m['Name'],'version':m['Version']})
assert len(metadata)==2
h=hashlib.sha256(p.read_bytes()).hexdigest();p.rename(dest)
plan=json.loads((run/'scispacy_range_plan.json').read_text())
d={'file':dest.name,'source_url':plan['url'],'actual_bytes':dest.stat().st_size,'sha256':h,'hash_origin':'computed from official HTTPS content, not an upstream checksum','gzip_crc_and_package_metadata_verified':True,'metadata':metadata,'name_comparison':'Python distribution normalized name per PEP 503; underscore and hyphen are equivalent','verification_fix_only_no_redownload':True,'preserved_prefix_bytes':plan['prefix_bytes'],'range_download_bytes':dest.stat().st_size-plan['prefix_bytes']}
(run/'scispacy_artifact_verification.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
PY
