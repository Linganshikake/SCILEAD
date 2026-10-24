set -eu
cd /root/scilead/axcell
python3 - <<'PY'
from pathlib import Path
import tarfile,json,hashlib
root=Path('/root/scilead/axcell')
archive=root/'cache/source_bootstrap_one_paper.tar.gz'
with tarfile.open(archive) as tf:
 for m in tf.getmembers():
  p=(root/m.name).resolve()
  if not p.is_relative_to(root) or not m.isfile():raise RuntimeError('Unsafe archive entry')
  if p.exists():raise RuntimeError('Will not overwrite existing transferred source')
 tf.extractall(root)
manifest=json.loads((root/'manifests/transfer_manifest.json').read_text())
for f in manifest['files']:
 p=root/f['relative']
 assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],f['relative']
for d in ['cache/tmp','cache/conda-pkgs','cache/pip','envs/mamba-root','runs/20261022_single_paper','parsed','scripts']:(root/d).mkdir(parents=True,exist_ok=True)
(root/'envs/bootstrap/micromamba').chmod(0o755)
print(json.dumps({'verified_source_and_bootstrap_files':len(manifest['files']),'revision':manifest['axcell_revision']}))
PY
/root/scilead/axcell/envs/bootstrap/micromamba --version
