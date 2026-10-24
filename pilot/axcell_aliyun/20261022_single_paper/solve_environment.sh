set -euo pipefail
export MAMBA_ROOT_PREFIX=/root/scilead/axcell/envs/mamba-root
export CONDA_PKGS_DIRS=/root/scilead/axcell/cache/conda-pkgs
export TMPDIR=/root/scilead/axcell/cache/tmp
export PIP_CACHE_DIR=/root/scilead/axcell/cache/pip
cd /root/scilead/axcell/source/axcell
/root/scilead/axcell/envs/bootstrap/micromamba --no-rc create --dry-run -y -p /root/scilead/axcell/envs/axcell-original -f environment.yml --json
