set -euo pipefail
export MAMBA_ROOT_PREFIX=/root/scilead/axcell/envs/mamba-root
export CONDA_PKGS_DIRS=/root/scilead/axcell/cache/conda-pkgs
export TMPDIR=/root/scilead/axcell/cache/tmp
export MAMBA_REMOTE_MAX_RETRIES=3
ROOT=/root/scilead/axcell
test ! -x "$ROOT/envs/axcell-original/bin/python"
test "$(df -B1 --output=avail / | tail -n 1)" -gt 21474836480
"$ROOT/envs/bootstrap/micromamba" --no-rc create -y -p "$ROOT/envs/axcell-original" --file "$ROOT/runs/20261022_single_paper/conda-explicit.txt" --json
"$ROOT/envs/axcell-original/bin/python" --version
"$ROOT/envs/axcell-original/bin/python" -m pip --version
