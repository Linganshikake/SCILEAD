set -euo pipefail
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
export PATH="$ROOT/envs/axcell-original/bin:$PATH"
export PYTHONPATH="$ROOT/source/axcell"
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="$ROOT/cache/tmp"
export OMP_NUM_THREADS=6
export MKL_NUM_THREADS=6
cd "$ROOT/source/axcell"
case "$1" in
 conversion_validation)
  exec python "$ROOT/scripts/validate_conversion.py"
  ;;
 environment_validation)
  python -m pip check > "$RUN/pip_check.txt"
  exec python "$ROOT/scripts/validate_environment.py"
  ;;
 conversion)
  test -f "$RUN/conversion_environment_validation.json"
  exec python -u "$ROOT/scripts/run_single.py" convert
  ;;
 elasticsearch_start)
  test -f "$RUN/parsed_artifacts.json"
  test -z "$(docker ps --filter name=^/axcell-single-convert$ --format '{{.ID}}')"
  exec bash "$ROOT/scripts/start_elasticsearch.sh"
  ;;
 extraction)
  test -f "$RUN/elasticsearch_version.json"
  test -f "$RUN/parsed_artifacts.json"
  exec python -u "$ROOT/scripts/run_single.py" extract
  ;;
 extraction_console_fix)
  test -f "$RUN/elasticsearch_restart_check.json"
  exec python -u "$ROOT/scripts/run_single.py" extract --attempt console_progress_compat
  ;;
 *) exit 2 ;;
esac
