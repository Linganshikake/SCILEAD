set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/elasticsearch_restart_console_fix_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-es-restart "python3 -u $ROOT/scripts/monitor.py --stage elasticsearch_restart_console_fix --timeout 180 -- bash $ROOT/scripts/restart_es_for_console_fix.sh > $RUN/elasticsearch_restart_console_fix.log 2>&1"
