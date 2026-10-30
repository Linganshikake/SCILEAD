"""Run the offline suite and one baseline parity evaluation; never rerun a model."""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
from offline_support import ANALYSIS, boundary, fresh_directory, read, save, sha, verify
from evaluate_offline import evaluate
from evaluate_ready import check_environment
from evaluation_contract import (BASELINE, RAW, Evidence, verify_audit, ready_stage,
                                 load_evaluation, seal_evaluation, verified_evaluation)

PARITY_FILES = ('tdm_official/eval_results.json', 'tdm_official/eval_values.json',
                'per_paper_metrics.json', 'strict_result_metrics.json',
                'leaderboard/official/eval_results.json', 'leaderboard/official/eval_values.json',
                'leaderboard/official/generated_leaderboards.json',
                'leaderboard/official/gold_after_official_conversion.json',
                'leaderboard/paper_metrics/leaderboard_metrics_by_tdm.json',
                'leaderboard/leaderboards/gold_vs_predicted.json')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ANALYSIS/'verification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    args=p.parse_args()
    boundary()
    out=fresh_directory(args.out)
    report={'status':'FAILED','new_api_requests':0,'model_runs':0}
    try:
        report['audit']=verify_audit()
        check_environment()
        suite=unittest.defaultTestLoader.discover(str(ANALYSIS),pattern='test_*.py')
        stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        (out/'tests.log').write_text(stream.getvalue(),encoding='utf-8')
        print(stream.getvalue(),end='')
        report['tests']={'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)}
        if not result.wasSuccessful():
            raise ValueError('Offline test suite failed')
        evidence=Evidence()
        stage=ready_stage(BASELINE,'partially_stage2',evidence)
        if stage['status']!='READY': raise ValueError('Baseline parity stage not ready')
        old=BASELINE/'analysis/evaluations/partially_stage2'
        new=out/'baseline_partially_stage2_parity'
        baseline=load_evaluation(old,stage['normalized'],evidence)
        status=evaluate(RAW,stage['normalized'],new)
        if status['status']!='COMPLETE': raise ValueError(f'Parity evaluation failed: {status}')
        candidate=load_evaluation(new,stage['normalized'],evidence)
        equal=[]
        for name in PARITY_FILES:
            if evidence.read(old/name)!=evidence.read(new/name):
                raise ValueError(f'Parity mismatch: {name}')
            equal.append(name)
        for name in ('tuple','leaderboard','per_paper','coverage'):
            if baseline[name]!=candidate[name]: raise ValueError(f'Parity mismatch: {name}')
        seal_evaluation(new,stage)
        before={str(p):sha(p) for p in new.rglob('*') if p.is_file()}
        verified_evaluation(new,stage['normalized'],evidence)
        verified_evaluation(new,stage['normalized'],evidence)
        verify(before)
        report.update(status='PASSED',parity_case='baseline partially_stage2',
                      parity_json_files_equal=equal, aggregate_per_paper_scope_equal=True,
                      verified_reuse_is_read_only=True, source_integrity=verify(evidence.hashes))
        save(out/'source_hashes.json',evidence.hashes)
    except Exception as error:
        report.update(error_type=type(error).__name__,error=str(error))
    save(out/'verification.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print('Verification directory: '+str(out))
    return 0 if report['status']=='PASSED' else 1


if __name__=='__main__':
    sys.exit(main())
