set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/conda_install_linux_owner.json"
test "$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)" -gt 6291456
tmux new-session -d -s axcell-single-conda-install "python3 -u $ROOT/scripts/monitor.py --stage conda_install --timeout 1800 -- bash $ROOT/scripts/install_conda.sh > $RUN/conda_install.log 2>&1"
tmux list-sessions -F '#{session_name}'
