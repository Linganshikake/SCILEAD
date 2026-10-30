"""Evaluate only completed variant stages, offline. Exit: 0 complete, 2 pending, 1 error."""
import argparse
import importlib.metadata
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode = True
from offline_support import ANALYSIS, boundary, save, verify, require_output
from evaluate_offline import evaluate
from evaluation_contract import (CASES, EXPERIMENT, RAW, Evidence, ready_stage, stage_paths,
                                 BASELINE, verify_audit, load_evaluation, seal_evaluation, verified_evaluation)


def check_environment():
    from offline_support import read, sha
    audit=read(BASELINE/'analysis/evaluations/partially_stage2/leaderboard/adapter_audit.json')
    spec=importlib.util.find_spec('rbo')
    if spec is None or not spec.origin:
        raise ValueError(r'Use existing D:\miniconda3\envs\scilead\python.exe (rbo already installed); no dependencies are installed by this tool.')
    if importlib.metadata.version('rbo') != audit['rbo_version'] or sha(spec.origin) != audit['rbo_source_sha256']:
        raise ValueError('rbo installation differs from audited baseline environment')


def run_cases(cases=CASES, inspect_only=False):
    boundary()
    verify_audit()
    jobs = []
    for case in cases:
        job = {'case':case}
        try:
            evidence = Evidence()
            stage = ready_stage(EXPERIMENT, case, evidence)
            if stage['status'] != 'READY':
                job.update(stage)
            else:
                output = require_output(ANALYSIS/'evaluations'/case)
                job['evaluation'] = str(output)
                if output.exists() and any(output.iterdir()):
                    verified_evaluation(output, stage['normalized'], evidence)
                    job.update(status='COMPLETE', action='SKIP_VERIFIED')
                elif inspect_only:
                    job.update(status='READY', action='INSPECT_ONLY')
                else:
                    check_environment()
                    verify(stage['input_hashes'])
                    result = evaluate(RAW, stage['normalized'], output)
                    if result['status'] != 'COMPLETE':
                        raise ValueError(f'Evaluator {result["status"]}: {result.get("error", result.get("reason"))}')
                    load_evaluation(output, stage['normalized'], evidence)
                    verify(stage['input_hashes'])
                    verify_audit()
                    seal_evaluation(output, stage)
                    verified_evaluation(output, stage['normalized'], evidence)
                    job.update(status='COMPLETE', action='EVALUATED')
        except Exception as error:
            job.update(status='ERROR', error_type=type(error).__name__, reason=str(error))
        jobs.append(job)
        print(json.dumps(job, ensure_ascii=False), flush=True)
    status = 'ERROR' if any(j['status']=='ERROR' for j in jobs) else 'COMPLETE' if all(j['status']=='COMPLETE' for j in jobs) else 'INCOMPLETE'
    report = {'status':status, 'jobs':jobs, 'selected_cases':list(cases), 'expected_cases':list(CASES),
              'all_eight_complete':len(set(cases))==8 and status=='COMPLETE', 'new_api_requests':0,
              'scope':'Offline stage evaluation only; no claim about global runtime/Prompt/usage integrity.'}
    save(ANALYSIS/'readiness.json', report)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', action='append', choices=CASES, help='Repeat to select stages; default all eight')
    p.add_argument('--inspect', action='store_true', help='Check readiness/reuse without running the evaluators')
    p.add_argument('--wait-seconds', type=float, default=0, help='Bounded polling for unfinished stages; default one pass')
    p.add_argument('--poll-seconds', type=float, default=10, help='1 to 60 seconds between passes')
    args = p.parse_args()
    if not 1 <= args.poll_seconds <= 60 or not 0 <= args.wait_seconds < float('inf'):
        p.error('Require 1 <= poll-seconds <= 60 and finite wait-seconds >= 0')
    deadline = time.monotonic()+args.wait_seconds
    cases = tuple(dict.fromkeys(args.case or CASES))
    try:
        while True:
            report = run_cases(cases, args.inspect)
            if report['status'] in ('COMPLETE', 'ERROR') or args.inspect or time.monotonic() >= deadline:
                return {'COMPLETE':0, 'INCOMPLETE':2, 'ERROR':1}[report['status']]
            time.sleep(min(args.poll_seconds, max(0, deadline-time.monotonic())))
    except Exception as error:
        print(json.dumps({'status':'ERROR','error':str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
