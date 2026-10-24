set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/engrafo_pull_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
test "$(df -B1 --output=avail / | tail -n 1)" -gt 21474836480
tmux new-session -d -s axcell-single-engrafo "python3 -u $ROOT/scripts/monitor.py --stage engrafo_pull --timeout 1200 -- bash $ROOT/scripts/pull_engrafo.sh > $RUN/engrafo_pull.log 2>&1"
tmux list-sessions -F '#{session_name}'
