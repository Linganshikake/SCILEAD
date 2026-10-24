set -eu
RUN=/root/scilead/axcell/runs/20261022_single_paper
test ! -e "$RUN/pip_install_tunnel_linux_status.json"
test "$(grep -c 'Installing collected packages:' "$RUN/pip_install_tunnel.log" || true)" -eq 0
touch "$RUN/pip_install_tunnel.stop"
