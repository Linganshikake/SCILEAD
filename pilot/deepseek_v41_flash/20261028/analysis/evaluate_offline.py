"""Standalone unchanged-official evaluation. Exit 0 complete, 2 incomplete, 1 failed.

Example: python -B -X utf8 evaluate_offline.py --raw output.json
         --normalized normalized_output.json --out analysis/evaluations/fully
"""
import argparse
import contextlib
import csv
import importlib.metadata
import importlib.util
import json
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path
import runpy
import shutil
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
from offline_support import (ANALYSIS, PILOT, REPO, GOLD, BOARDS, HELPERS, boundary,
                             bind_official, fresh_directory, read, save, sha, verify,
                             unique_object)

METRICS = ('Task IIM', 'Dataset IIM', 'Metric IIM', 'Result IIM', 'TDM Exact Match', 'TDMR Exact Match')
FIELDS = ('Task', 'Dataset', 'Metric', 'Result')


def metric(p, r):
    return {'Precision': p, 'Recall': r, 'F1': 2*p*r/(p+r) if p+r else 0.0}


def number(value):
    try:
        n = Decimal(str(value))
        return n if n.is_finite() else None
    except InvalidOperation:
        return None


def strict_metric(rows, gold):
    # Audited evaluate_variants.py auxiliary definition; no cleaning or scaling.
    pn, gn = {number(x['Result']) for x in rows}, {number(x['Result']) for x in gold}
    common = (pn & gn) - {None}
    pd = len(pn - {None}) + len({str(x['Result']) for x in rows if number(x['Result']) is None})
    gd = len(gn - {None}) + len({str(x['Result']) for x in gold if number(x['Result']) is None})
    return metric(len(common)/pd if pd else 0, len(common)/gd if gd else 0)


def validate_inputs(raw, normalized, gold):
    if not all(isinstance(x, dict) for x in (raw, normalized, gold)):
        raise ValueError('Raw, normalized and Gold must be paper-ID objects')
    if (set(raw) | set(normalized)) - set(gold):
        raise ValueError('Unknown paper IDs outside Gold')
    if set(normalized) - set(raw):
        raise ValueError('Normalized paper has no raw extraction')
    conversions, predictions = 0, 0
    for paper, item in normalized.items():
        rows = item.get('normalized_output')
        if not isinstance(rows, list):
            raise ValueError(f'{paper}: normalized_output must be a list')
        if 'source_documents' not in item or item['source_documents'] != raw[paper].get('source_documents'):
            raise ValueError(f'{paper}: source_documents changed or missing')
        source = json.loads(raw[paper]['output'], parse_float=Decimal, object_pairs_hook=unique_object)
        if not isinstance(source, list) or len(source) != len(rows):
            raise ValueError(f'{paper}: raw/normalized row count mismatch')
        for index, (a, b) in enumerate(zip(source, rows)):
            if not isinstance(a, dict) or not isinstance(b, dict) or not all(k in a and k in b for k in FIELDS):
                raise ValueError(f'{paper}/{index}: missing TDMR fields')
            if any(b[k] is not None and not isinstance(b[k], str) for k in FIELDS[:3]):
                raise ValueError(f'{paper}/{index}: labels must be strings or null')
            if not isinstance(b['Result'], str):
                raise ValueError(f'{paper}/{index}: Result must already be a string; no implicit repair')
            if isinstance(a['Result'], str):
                if a['Result'] != b['Result']:
                    raise ValueError(f'{paper}/{index}: Result string changed')
            elif isinstance(a['Result'], (int, Decimal)) and not isinstance(a['Result'], bool):
                if number(a['Result']) is None or number(a['Result']) != number(b['Result']):
                    raise ValueError(f'{paper}/{index}: numeric Result conversion is not lossless')
                conversions += 1
            else:
                raise ValueError(f'{paper}/{index}: unsupported raw Result type')
        predictions += len(rows)
    complete = set(normalized) == set(gold)
    return {'status': 'COMPLETE' if complete else 'INCOMPLETE',
            'official_papers': len(gold), 'official_gold_tdmrs': sum(len(v['TDMs']) for v in gold.values()),
            'raw_papers': len(raw), 'evaluated_papers': len(normalized), 'tuple_macro_denominator': len(normalized),
            'evaluated_gold_tdmrs': sum(len(gold[p]['TDMs']) for p in normalized),
            'predictions': predictions, 'evaluated_ids': list(normalized),
            'missing_raw_ids': sorted(set(gold)-set(raw)), 'missing_normalized_ids': sorted(set(gold)-set(normalized)),
            'raw_without_normalization_ids': sorted(set(raw)-set(normalized)),
            'numeric_result_to_string_rows': conversions,
            'tuple_scope': 'Observed normalized papers only; missing papers are NOT zero-filled in tuple macro scores.',
            'leaderboard_scope': 'Full supplied Gold boards and Gold memberships; absent predictions contribute no entries.'}


def aggregate_results(result):
    a = {k+' IIM': metric(v['Precision'], v['Recall']) for k, v in result['Individual'].items()}
    a['TDM Exact Match'] = metric(result['Exact Match Precision wo Results'], result['Exact Match Recall wo Results'])
    a['TDMR Exact Match'] = metric(result['Exact Match Precision'], result['Exact Match Recall'])
    return a


def per_paper_results(values, paper_ids):
    per = {}
    for p in paper_ids:
        m = {k+' IIM': metric(v['Precision'][p], v['Recall'][p]) for k, v in values['Individual'].items()}
        m['TDM Exact Match'] = metric(values['Exact Match Recall wo Precision'][p], values['Exact Match Recall wo Results'][p])
        m['TDMR Exact Match'] = metric(values['Exact Match Precision'][p], values['Exact Match Recall'][p])
        per[p] = m
    return per


def evaluate_tuples(out, gold_path, normalized_path, normalized, gold, coverage):
    import tdm_eval
    dest = out/'tdm_official'
    dest.mkdir()
    args = SimpleNamespace(gold_data_path=str(gold_path), normalized_tdm_output_path=str(normalized_path),
                           eval_results_path=str(dest/'eval_results.json'), eval_values_path=str(dest/'eval_values.json'))
    save(dest/'invocation.json', vars(args))
    with (dest/'run.log').open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
        tdm_eval.main(args)
    result, values = read(dest/'eval_results.json'), read(dest/'eval_values.json')
    per, strict = per_paper_results(values, normalized), {}
    for p in normalized:
        strict[p] = strict_metric(normalized[p]['normalized_output'], gold[p]['TDMs'])
    n = len(normalized)
    strict_aggregate = metric(sum(x['Precision'] for x in strict.values())/n, sum(x['Recall'] for x in strict.values())/n)
    save(out/'metrics_with_f1.json', {'status': coverage['status'], 'coverage': coverage, 'aggregate': aggregate_results(result),
         'aggregation': 'Unchanged official macro per-paper P/R; F1=2PR/(P+R), not mean paper F1.',
         'mean_per_paper_f1_SEPARATE': {k: sum(x[k]['F1'] for x in per.values())/n for k in METRICS},
         'input_path': str(normalized_path), 'input_sha256': sha(normalized_path)})
    save(out/'per_paper_metrics.json', per)
    with (out/'per_paper_metrics.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['paper_id', 'metric', 'Precision', 'Recall', 'F1', 'gold_tdmrs', 'predictions'])
        writer.writeheader()
        for p, metrics in per.items():
            for name, scores in {**metrics, 'Strict Result numeric equality': strict[p]}.items():
                writer.writerow({'paper_id': p, 'metric': name, **scores, 'gold_tdmrs': len(gold[p]['TDMs']), 'predictions': len(normalized[p]['normalized_output'])})
    save(out/'strict_result_metrics.json', {'status': coverage['status'], 'coverage': coverage,
         'aggregate': strict_aggregate, 'per_paper': strict,
         'definition': 'Auxiliary Result-only finite Decimal equality; unique numerics collapse; distinct invalid strings remain denominator entries but never match. No percent stripping, tolerance, scaling, or tuple conditioning.'})


def evaluate_boards(out, raw, normalized, gold, board_path, coverage, hashes):
    dest = out/'leaderboard'
    for name in ('official', 'paper_metrics', 'leaderboards', 'reference', 'helper_view/merged'):
        (dest/name).mkdir(parents=True, exist_ok=True)
    # The unchanged diagnostic helper indexes every Gold paper. Empty *helper-only*
    # placeholders make absent papers inspectable; no predicted rows are added.
    view_norm = dict(normalized)
    view_raw = {p: raw[p] for p in normalized}
    for p in gold:
        if p not in normalized:
            view_norm[p] = {'normalized_output': [], 'source_documents': []}
            view_raw[p] = {'output': '[]', 'source_documents': []}
    save(dest/'helper_view/normalized_output.json', view_norm)
    save(dest/'helper_view/merged/output.json', view_raw)
    import leaderboard_eval
    original_boards = leaderboard_eval.construct_output_leaderboards(read(board_path), normalized)
    if any(not math.isfinite(v) for board in original_boards.values() for v in board.values()):
        raise ValueError('Nonfinite result under official leaderboard conversion; supplementary ranking refused')
    if original_boards != leaderboard_eval.construct_output_leaderboards(read(board_path), view_norm):
        raise ValueError('Helper view changed official constructed boards')
    copied = []
    for name in ('run_official_leaderboard_eval.py', 'evaluate_paper_metrics.py'):
        shutil.copyfile(HELPERS/name, dest/name)
        if sha(HELPERS/name) != sha(dest/name):
            raise ValueError('Helper copy hash mismatch')
        copied.append({'source': str(HELPERS/name), 'copy': str(dest/name), 'sha256': sha(dest/name)})
    common = f'''from offline_support import *
RUN = Path({str(dest)!r})
BASE = RUN / 'helper_view'
GOLD = Path({str(board_path)!r})
NORMALIZED = BASE / 'normalized_output.json'
def verify_frozen():
    return verify(read(RUN / 'source_hashes.json'))
'''
    (dest/'common.py').write_text(common, encoding='utf-8')
    frozen = dict(hashes)
    for p in [dest/'common.py', dest/'helper_view/normalized_output.json', dest/'helper_view/merged/output.json']:
        frozen[str(p)] = sha(p)
    for c in copied:
        frozen[c['copy']] = c['sha256']
    save(dest/'source_hashes.json', frozen)
    previous = sys.modules.get('common')
    spec = importlib.util.spec_from_file_location('common', dest/'common.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules['common'] = module
    spec.loader.exec_module(module)
    try:
        for name in ('run_official_leaderboard_eval.py', 'evaluate_paper_metrics.py'):
            with (dest/(name+'.log')).open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                runpy.run_path(str(dest/name), run_name='__main__')
    finally:
        if previous is None: sys.modules.pop('common', None)
        else: sys.modules['common'] = previous
    import rbo
    save(dest/'adapter_audit.json', {'helpers': copied, 'source_integrity': verify(frozen), 'coverage': coverage,
         'formulas_modified': False, 'new_api_requests': 0, 'rbo_version': importlib.metadata.version('rbo'),
         'rbo_source': str(Path(rbo.__file__)), 'rbo_source_sha256': sha(rbo.__file__),
         'helper_only_empty_paper_ids': coverage['missing_normalized_ids'], 'constructed_boards_equal_without_placeholders': True,
         'conventions': {'LR': 'LR_exact_tdm_hit', 'nonempty': 'LR_nonempty_finite_result',
                         'RBO': 'Official deduplicated numeric-value rankings', 'AO': 'Paper IDs; all supplied Gold boards; empty=0; deterministic paper-ID tie break',
                         'legacy_helper_text': 'Copied unchanged; LR_primary prose is obsolete. Its literal 27 wording does not filter board scope. Missing unprocessed papers are identified in coverage, not inferred from null diagnostics.'}})


def evaluate(raw_path, normalized_path, out_path, gold_path=GOLD, board_path=BOARDS):
    boundary()
    out = fresh_directory(out_path)
    paths = {k: Path(v).resolve() for k, v in [('raw', raw_path), ('normalized', normalized_path), ('gold', gold_path), ('boards', board_path)]}
    status = {'status': 'FAILED', 'new_api_requests': 0, 'paths': {k: str(p) for k, p in paths.items()},
              'completion_scope': 'This normalized file only; not experiment/API completion.'}
    hashes = {}
    try:
        missing = [str(p) for p in paths.values() if not p.is_file()]
        if missing:
            status.update(status='INCOMPLETE', missing=missing)
            return status
        protected = list(paths.values()) + [GOLD, BOARDS, REPO/'tdm_eval.py', REPO/'leaderboard_eval.py', REPO/'utils.py',
                     HELPERS/'run_official_leaderboard_eval.py', HELPERS/'evaluate_paper_metrics.py',
                     PILOT/'gpt56_sol_variants/20261024/evaluate_variants.py', Path(__file__), ANALYSIS/'offline_support.py']
        hashes = {str(p): sha(p) for p in protected}
        save(out/'source_hashes.json', hashes)
        raw, normalized, gold, boards = (read(paths[k]) for k in ('raw', 'normalized', 'gold', 'boards'))
        if len(gold) != 43 or sum(len(x['TDMs']) for x in gold.values()) != 295:
            raise ValueError('Official Gold must be 43 papers / 295 annotations')
        if gold != read(GOLD):
            raise ValueError('Gold annotations differ from the official frozen 43/295 set')
        if not isinstance(boards, list) or not boards:
            raise ValueError('Gold leaderboards must be a nonempty list')
        official_boards = read(BOARDS)
        if len(official_boards) != 27 or any(b not in official_boards for b in boards):
            raise ValueError('Board targets must be unchanged members of the official 27-board set')
        keys = [str((b['Task'], b['Dataset'], b['Metric'])) for b in boards]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate Gold board')
        coverage = validate_inputs(raw, normalized, gold)
        coverage.update(gold_leaderboards=len(boards), board_ids=keys, board_scope='all27' if len(boards)==27 else 'explicit_subset',
                        gold_sha256=sha(paths['gold']), boards_sha256=sha(paths['boards']))
        status['coverage'] = coverage
        save(out/'coverage.json', coverage)
        if not normalized:
            status.update(status='INCOMPLETE', reason='No observed normalized papers; no scores generated')
            return status
        bind_official()
        evaluate_tuples(out, paths['gold'], paths['normalized'], normalized, gold, coverage)
        evaluate_boards(out, raw, normalized, gold, paths['boards'], coverage, hashes)
        status.update(status=coverage['status'], official_mains_executed=True,
                      utils_adapter='Isolated read_json only; no model dependencies imported')
    except Exception as error:
        status.update(status='FAILED', error_type=type(error).__name__, error=str(error))
    finally:
        try:
            status['source_integrity'] = verify(hashes)
        except Exception as error:
            status.update(status='FAILED', integrity_error=str(error))
        save(out/'status.json', status)
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('raw', 'normalized', 'out'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--gold', type=Path, default=GOLD)
    parser.add_argument('--boards', type=Path, default=BOARDS, help='Default official all27; optional unchanged Gold subset, e.g. masked10')
    args = parser.parse_args()
    try:
        status = evaluate(args.raw, args.normalized, args.out, args.gold, args.boards)
    except Exception as error:
        print(json.dumps({'status': 'FAILED', 'error': str(error)})); return 1
    print(json.dumps({'status': status['status'], 'out': str(args.out), 'coverage': status.get('coverage'), 'error': status.get('error')}, ensure_ascii=False))
    return {'COMPLETE': 0, 'INCOMPLETE': 2, 'FAILED': 1}[status['status']]


if __name__ == '__main__':
    sys.exit(main())
