set -eu
ROOT=/root/scilead/axcell
RUN=$ROOT/runs/20261022_single_paper
test ! -e "$RUN/scispacy_resume_linux_owner.json"
tmux new-session -d -s axcell-single-scispacy "python3 -u $ROOT/scripts/monitor.py --stage scispacy_resume --timeout 1860 -- python3 -u $ROOT/scripts/resume_public_scispacy.py > $RUN/scispacy_resume.log 2>&1"
