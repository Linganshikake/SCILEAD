set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/pip_consistency_fix_linux_owner.json"
test -f "$RUN/pip_install_compatible_linux_status.json"
tmux new-session -d -s axcell-single-consistency "python3 -u $ROOT/scripts/monitor.py --stage pip_consistency_fix --timeout 300 -- bash $ROOT/scripts/fix_declared_constraints.sh > $RUN/pip_consistency_fix.log 2>&1"
