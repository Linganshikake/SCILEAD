"""Run reporting tests under the offline/write-boundary guard; no evaluation."""
import io
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from offline_guard import activate
from audit_and_report import HERE, save, sha, timestamps


def main():
    guard = activate()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_audit_and_report.py')
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    source_files = ['audit_and_report.py', 'report_render.py', 'offline_guard.py', 'test_audit_and_report.py', 'verify_offline.py']
    proof = {'status': 'PASS' if result.wasSuccessful() and not guard.blocked else 'FAILED', **timestamps(),
             'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
             'blocked_events_during_suite': guard.blocked, 'observed_write_paths': sorted(guard.write_paths),
             'write_boundary': str(HERE), 'network_model_evaluation_calls': 0,
             'source_hashes': {name: sha(HERE / name) for name in source_files},
             'note': 'Synthetic fixtures are created and removed only below reporting. Guard denial unit tests invoke the policy directly without network/process/credential operations.'}
    save(HERE / 'test_results.json', proof)
    save(HERE / 'test_results.txt', stream.getvalue())
    print(stream.getvalue(), end='')
    print('Reporting test proof: ' + str(HERE / 'test_results.json'))
    return 0 if proof['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
