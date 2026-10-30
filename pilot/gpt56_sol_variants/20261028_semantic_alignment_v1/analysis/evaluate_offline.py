"""Completed-stage facade over the byte-identical audited scorer.

CLI is the same as evaluate_ready.py. Never score arbitrary/partial input files.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from offline_support import GOLD, BOARDS, boundary
from audited_helpers.evaluate_offline import (METRICS, FIELDS, metric, strict_metric,
    validate_inputs, aggregate_results, per_paper_results, evaluate as _score)


def evaluate(raw_path, normalized_path, out_path, gold_path=GOLD, board_path=BOARDS):
    boundary()
    from evaluation_contract import (BASELINE, EXPERIMENT, RAW, CASES, ready_stage,
                                      stage_paths, verify_audit)
    from evaluate_ready import check_environment
    verify_audit()
    if Path(raw_path).resolve() != RAW.resolve():
        raise ValueError('Use the frozen Sol baseline extraction')
    if Path(gold_path).resolve() != GOLD.resolve() or Path(board_path).resolve() != BOARDS.resolve():
        raise ValueError('Only the unchanged 43/295 Gold and all27 board scope is supported')
    matches = [(root, case) for root in (BASELINE, EXPERIMENT) for case in CASES
               if stage_paths(root, case)[0].resolve() == Path(normalized_path).resolve()]
    if len(matches) != 1:
        raise ValueError('Normalized input must be a known flat Sol experiment stage')
    stage = ready_stage(*matches[0])
    if stage['status'] != 'READY':
        raise ValueError('Only COMPLETE, validated stages may be evaluated')
    check_environment()
    return _score(raw_path, normalized_path, out_path, gold_path, board_path)


if __name__ == '__main__':
    from evaluate_ready import main
    sys.exit(main())
