set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/docker_transport_fix_linux_owner.json"
tmux new-session -d -s axcell-single-http-fix "python3 -u $ROOT/scripts/monitor.py --stage docker_transport_fix --timeout 300 -- bash $ROOT/scripts/fix_docker_transport.sh > $RUN/docker_transport_fix.log 2>&1"
