set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
python3 -u "$ROOT/scripts/monitor.py" --stage conversion_validation --timeout 60 -- bash "$ROOT/scripts/run_stage.sh" conversion_validation > "$RUN/conversion_validation.log" 2>&1
cat "$RUN/conversion_environment_validation.json"
