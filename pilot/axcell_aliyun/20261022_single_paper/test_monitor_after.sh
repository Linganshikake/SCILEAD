set -eu
python3 /root/scilead/axcell/scripts/monitor_orphan_test.py monitor_orphan_after
python3 /root/scilead/axcell/scripts/test_adapter_guards.py
bash -n /root/scilead/axcell/scripts/run_stage.sh
bash -n /root/scilead/axcell/scripts/start_elasticsearch.sh
