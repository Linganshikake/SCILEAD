"""Offline behavior suite and all-eight Sol baseline exact-parity verification."""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from offline_support import ANALYSIS, boundary, fresh_directory, save, sha, verify
from evaluate_ready import run_cases, check_environment
from evaluation_contract import (BASELINE, CASES, Evidence, verify_audit, stage_paths,
                                 verified_evaluation, verify_baseline_parity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ANALYSIS/'verification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    args = parser.parse_args()
    boundary()
    out = fresh_directory(args.out)
    report = {'status':'FAILED', 'created_utc':datetime.now(timezone.utc).isoformat(),
              'new_api_requests':0, 'model_runs':0}
    try:
        report['audit'] = verify_audit()
        check_environment()
        suite = unittest.defaultTestLoader.discover(str(ANALYSIS), pattern='test_*.py')
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        (out/'tests.log').write_text(stream.getvalue(), encoding='utf-8')
        print(stream.getvalue(), end='')
        report['tests'] = {'run':result.testsRun, 'failures':len(result.failures), 'errors':len(result.errors)}
        if not result.wasSuccessful():
            raise ValueError('Offline behavior tests failed')
        baseline = run_cases(source='baseline')
        if baseline['status'] != 'COMPLETE':
            raise ValueError('Baseline re-evaluation/parity failed; see baseline_readiness.json')
        report['baseline_actions'] = {j['case']:j['action'] for j in baseline['jobs']}
        evidence, parity = Evidence(), []
        for case in CASES:
            folder = ANALYSIS/'baseline_evaluations'/case
            frozen = {str(p):sha(p) for p in folder.rglob('*') if p.is_file()}
            norm = stage_paths(BASELINE, case)[0]
            verified_evaluation(folder, norm, evidence)
            verified_evaluation(folder, norm, evidence)
            verify(frozen)
            parity.append(verify_baseline_parity(folder, case, evidence))
        report.update(status='PASSED', baseline_cases=8, exact_parity=parity,
                      verified_reuse_is_read_only=True, source_integrity=verify(evidence.hashes),
                      write_boundary=str(ANALYSIS),
                      safety='Python audit guard active; synthetic blocked events tested without making network/model/process calls')
        save(out/'source_hashes.json', evidence.hashes)
    except Exception as error:
        report.update(error_type=type(error).__name__, error=str(error))
    save(out/'verification.json', report)
    print(json.dumps({k:v for k,v in report.items() if k != 'exact_parity'}, ensure_ascii=False, indent=2))
    print('Verification directory: '+str(out))
    return 0 if report['status'] == 'PASSED' else 1


if __name__ == '__main__':
    sys.exit(main())
