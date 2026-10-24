set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/conda_dry_run_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-solve "python3 -u $ROOT/scripts/monitor.py --stage conda_dry_run --timeout 900 -- bash $ROOT/scripts/solve_environment.sh > $RUN/conda_dry_run.log 2>&1"
tmux list-sessions -F '#{session_name}'
