set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/elasticsearch_pull_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
test "$(df -B1 --output=avail / | tail -n 1)" -gt 21474836480
tmux new-session -d -s axcell-single-es-image "python3 -u $ROOT/scripts/monitor.py --stage elasticsearch_pull --timeout 1800 -- bash $ROOT/scripts/pull_elasticsearch.sh > $RUN/elasticsearch_pull.log 2>&1"
tmux list-sessions -F '#{session_name}'
