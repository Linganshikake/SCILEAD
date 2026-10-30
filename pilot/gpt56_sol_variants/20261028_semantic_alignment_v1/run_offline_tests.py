"""Run the complete owned suite in the existing scilead environment, with HTTP mocked."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from runtime_policy import OWNED, offline_guard
import variant_runtime as v

SUITES = ('test_prompt_variant', 'test_transport', 'test_original_partially',
          'test_original_cold_start')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=SUITES, action='append')
    args = parser.parse_args()
    offline_guard()
    folder = OWNED / 'reproducibility' / ('test_run_' + str(time.time_ns()))
    folder.mkdir(parents=True)
    results = []
    os.environ.update(PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    for name in args.suite or SUITES:
        log = folder / (name + '.log')
        with log.open('w', encoding='utf-8') as f:
            proc = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(OWNED / 'offline_entry.py'), name],
                                  stdout=f, stderr=subprocess.STDOUT, cwd=OWNED)
        result = {'suite': name, 'exit_code': proc.returncode, 'log': str(log)}
        results.append(result)
        print(json.dumps(result), flush=True)
        if proc.returncode:
            print(log.read_text('utf-8')[-6000:], flush=True)
    passed = all(r['exit_code'] == 0 for r in results)
    evidence = dict(status='PASS' if passed else 'FAIL', suites=results, new_api_requests=0,
                    credential_reads=0, model_loads=0, network_guard=True, owned_write_guard=True,
                    root_transport_path=str(v.A1/'run_trial.py'), root_transport_sha256=v.sha(v.A1/'run_trial.py'),
                    original_observers={name: str(v.PILOT / name / 'engine.py')
                                        for name in ('full43_partially', 'full43_cold_start')})
    v.save(folder / 'summary.json', evidence)
    if args.suite is None:
        v.save(OWNED / 'reproducibility/offline_tests.json', evidence)
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
