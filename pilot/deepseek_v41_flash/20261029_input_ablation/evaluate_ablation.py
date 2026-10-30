"""Offline five-paper ablation evaluation. Exit 0 complete, 2 incomplete, 1 failed.

python -B -X utf8 evaluate_ablation.py --arms baseline_rag
python -B -X utf8 evaluate_ablation.py

Only evaluation/ is writable. No model/API/credential imports. Official evaluator
files remain unmodified; old helper functions are loaded by AST, never imported.
"""
import argparse
import ast
import contextlib
import copy
import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
EVALUATION = ROOT / 'evaluation'
SCILEAD = ROOT.parents[2]
REPO = SCILEAD / 'emnlp2024-leaderboard-generation'
GOLD = SCILEAD / 'pilot/autodl_setup/20261021/stage/data/gold/tdm_annotations.json'
BOARDS = GOLD.with_name('leaderboards.json')
OLD_ANALYSIS = ROOT.parent / '20261028/analysis'
TUPLE_HELPER = OLD_ANALYSIS / 'evaluate_offline.py'
BOARD_HELPER = OLD_ANALYSIS / 'evaluations/partially_stage2/leaderboard/evaluate_paper_metrics.py'
ARMS = {'baseline_rag': 'baseline_rag/merged',
        'parsed_full': 'parsed_full/fully/merged',
        'page_images': 'page_images/fully/merged'}
FIELDS = ('Task', 'Dataset', 'Metric', 'Result')
METRICS = ('Task IIM', 'Dataset IIM', 'Metric IIM', 'Result IIM',
           'TDM Exact Match', 'TDMR Exact Match', 'Strict Result numeric equality')
NETWORK_ATTEMPTS = []


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def writable(path):
    path = Path(path).resolve()
    if not path.is_relative_to(EVALUATION.resolve()):
        raise PermissionError('Evaluation writes must stay in ' + str(EVALUATION))
    return path


def save(path, value, frozen=False):
    path = writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if frozen and path.exists():
        if read(path) != value:
            raise ValueError('Frozen evaluation scope changed: ' + str(path))
        return
    with path.open('x' if frozen else 'w', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')


def install_boundary():
    def guard(event, args):
        if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind'):
            NETWORK_ATTEMPTS.append(event)
            raise PermissionError('Offline evaluator prohibits network access')
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            p = Path(os.fsdecode(args[0]))
            if p.name.lower().endswith('.env') or p.name.lower().startswith('.env.'):
                raise PermissionError('Credential files are outside evaluator scope')
            mode = args[1] or ''
            flags = args[2] or 0
            if any(c in mode for c in 'wax+') or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                writable(p)
        if event in ('os.mkdir', 'os.remove', 'os.rmdir'):
            writable(args[0])
        if event in ('os.rename', 'os.replace'):
            writable(args[0]); writable(args[1])
    sys.addaudithook(guard)


def load_pure_helpers():
    namespace = {'Decimal': Decimal, 'InvalidOperation': InvalidOperation, 'math': math}
    for path, names in [(TUPLE_HELPER, {'metric', 'number', 'strict_metric', 'aggregate_results', 'per_paper_results'}),
                        (BOARD_HELPER, {'ranking', 'ao'})]:
        tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        if {n.name for n in functions} != names:
            raise ValueError('Historical pure helper contract changed: ' + str(path))
        # No old module imports, globals, main(), boundary(), or writes execute.
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


HELPERS = load_pure_helpers()
metric = HELPERS['metric']
number = HELPERS['number']
strict_metric = HELPERS['strict_metric']


def derive_boards(original, selected):
    selected = set(selected)
    derived = []
    for source in original:
        board = copy.deepcopy(source)
        board['Leaderboard'] = {p: v for p, v in source['Leaderboard'].items() if p in selected}
        if board['Leaderboard']:
            derived.append(board)
    return derived, {'original_boards': len(original), 'boards_retained': len(derived),
                     'boards_dropped_empty': len(original)-len(derived),
                     'singleton_boards': sum(len(b['Leaderboard']) == 1 for b in derived),
                     'boards_ge2': sum(len(b['Leaderboard']) >= 2 for b in derived),
                     'membership_rule': 'Original board members intersect fixed selected IDs; empty discarded; singleton retained.'}


def raw_view(raw, selected):
    view = {}
    for paper in selected:
        if paper not in raw:
            continue
        entry = raw[paper]
        if not isinstance(entry.get('output'), str):
            raise ValueError(paper + ': raw output must be a JSON string')
        rows = json.loads(entry['output'], parse_float=Decimal, object_pairs_hook=unique_object)
        if not isinstance(rows, list):
            raise ValueError(paper + ': raw output must decode to a list')
        converted = []
        for row in rows:
            if not isinstance(row, dict) or not all(k in row for k in FIELDS):
                raise ValueError(paper + ': missing raw fields')
            row = dict(row)
            if any(row[k] is not None and not isinstance(row[k], str) for k in FIELDS[:3]):
                raise ValueError(paper + ': raw labels must be strings or null')
            if not isinstance(row['Result'], str):
                if isinstance(row['Result'], bool) or not isinstance(row['Result'], (int, Decimal)) or number(row['Result']) is None:
                    raise ValueError(paper + ': invalid raw Result')
                row['Result'] = str(row['Result'])
            converted.append(row)
        view[paper] = {'normalized_output': converted, 'source_documents': entry.get('source_documents', [])}
    return view


def scope_inputs(raw, normalized, selected):
    if not isinstance(raw, dict) or not isinstance(normalized, dict):
        raise ValueError('Merged inputs must be paper-ID objects')
    extraction = raw_view(raw, selected)
    scoped = {}
    for paper in selected:
        if paper not in normalized:
            continue
        if paper not in extraction:
            raise ValueError(paper + ': normalization without raw extraction')
        entry = normalized[paper]
        rows = entry.get('normalized_output')
        if not isinstance(rows, list) or len(rows) != len(extraction[paper]['normalized_output']):
            raise ValueError(paper + ': invalid normalized rows or changed row count')
        if entry.get('source_documents', []) != extraction[paper]['source_documents']:
            raise ValueError(paper + ': source_documents changed')
        original_rows = json.loads(raw[paper]['output'], parse_float=Decimal, object_pairs_hook=unique_object)
        for row_index, (before, after) in enumerate(zip(extraction[paper]['normalized_output'], rows)):
            if not isinstance(after, dict) or not all(k in after for k in FIELDS):
                raise ValueError(paper + ': missing normalized fields')
            if any(after[k] is not None and not isinstance(after[k], str) for k in FIELDS[:3]):
                raise ValueError(paper + ': invalid normalized label')
            if not isinstance(after['Result'], str) or after['Result'] != before['Result']:
                # Exact strings for strings; lossless Decimal equality for a raw JSON number.
                raw_original = original_rows[row_index]['Result']
                if isinstance(raw_original, str) or not isinstance(after['Result'], str) or number(after['Result']) != number(raw_original):
                    raise ValueError(paper + ': Result changed or unsupported type')
        scoped[paper] = entry
    coverage = {'status': 'COMPLETE' if len(scoped) == len(selected) and len(extraction) == len(selected) else 'INCOMPLETE',
                'selected_ids': list(selected), 'selected_papers': len(selected), 'raw_papers': len(extraction),
                'evaluated_papers': len(scoped), 'evaluated_ids': list(scoped), 'tuple_macro_denominator': len(scoped),
                'missing_raw_ids': [p for p in selected if p not in extraction],
                'missing_normalized_ids': [p for p in selected if p not in scoped],
                'excluded_unselected_raw_ids': sorted(set(raw)-set(selected)),
                'excluded_unselected_normalized_ids': sorted(set(normalized)-set(selected)),
                'tuple_scope': 'Observed selected papers only; missing papers are not zero-filled.',
                'completion_scope': 'Selected input artifacts only; not API or whole-experiment completion.'}
    return scoped, coverage


@contextlib.contextmanager
def official_modules():
    previous = sys.modules.get('utils')
    stub = ModuleType('utils')
    stub.read_json = read
    sys.modules['utils'] = stub
    try:
        loaded = []
        for name in ('tdm_eval', 'leaderboard_eval'):
            spec = importlib.util.spec_from_file_location('_ablation_official_' + name, REPO / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded.append(module)
        yield loaded
    finally:
        if previous is None:
            sys.modules.pop('utils', None)
        else:
            sys.modules['utils'] = previous


def evaluate_stage(out, normalized, gold, board_path, selected, official):
    out.mkdir(parents=True)
    status = 'COMPLETE' if set(normalized) == set(selected) else 'INCOMPLETE'
    result = {'status': status, 'new_api_requests': 0, 'evaluated_ids': list(normalized),
              'tuple_macro_denominator': len(normalized), 'aggregate': {}, 'per_paper': {}, 'leaderboard': None,
              'matching_semantics': {
                  'Task_Dataset_Metric': 'Exact label equality; no semantic matching.',
                  'TDM_Exact_Match': 'Original official unique exact (Task, Dataset, Metric) tuples.',
                  'TDMR_Exact_Match_and_Result_IIM': 'Original official legacy bidirectional Result substring rule; not strict numeric equality and not semantic matching.',
                  'Strict_Result_numeric_equality': 'Auxiliary finite Decimal Result-only equality; unique numerics; distinct invalid strings remain denominator entries; no percent stripping, scaling, tolerance, or tuple conditioning.'}}
    if not normalized:
        result['reason'] = 'No observed papers; no metrics generated.'
        save(out/'report.json', result)
        return result
    norm_path = out/'scoped_normalized_input.json'
    save(norm_path, normalized)
    tdm, lb = official
    args = SimpleNamespace(gold_data_path=str(GOLD), normalized_tdm_output_path=str(norm_path),
                           eval_results_path=str(out/'tdm_official_results.json'), eval_values_path=str(out/'tdm_official_values.json'))
    save(out/'tdm_invocation.json', vars(args))
    tdm.main(args)
    values = read(out/'tdm_official_values.json')
    aggregate = HELPERS['aggregate_results'](read(out/'tdm_official_results.json'))
    per = HELPERS['per_paper_results'](values, normalized)
    for paper in normalized:
        per[paper]['Strict Result numeric equality'] = strict_metric(normalized[paper]['normalized_output'], gold[paper]['TDMs'])
    strict = [v['Strict Result numeric equality'] for v in per.values()]
    aggregate['Strict Result numeric equality'] = metric(sum(x['Precision'] for x in strict)/len(strict), sum(x['Recall'] for x in strict)/len(strict))
    result.update(aggregate=aggregate, per_paper=per,
                  mean_per_paper_f1_SEPARATE={k: sum(v[k]['F1'] for v in per.values())/len(per) for k in METRICS},
                  f1_definition='Harmonic mean of official macro per-paper Precision/Recall; mean paper F1 is separate.')
    args = SimpleNamespace(gold_leaderboards_file=str(board_path), masked_leaderboards_file='',
                           normalized_output_file=str(norm_path), eval_results_file=str(out/'leaderboard_official_results.json'),
                           eval_values_file=str(out/'leaderboard_official_values.json'))
    save(out/'leaderboard_invocation.json', vars(args))
    lb.main(args)
    boards = read(board_path)
    predicted = lb.construct_output_leaderboards(boards, copy.deepcopy(normalized))
    if any(not math.isfinite(v) for values in predicted.values() for v in values.values()):
        raise ValueError('Nonfinite official board result; supplementary ranking refused')
    official_values = read(out/'leaderboard_official_values.json')['gold_results']
    hits = {str((x['Task'], x['Dataset'], x['Metric'])) for p in normalized.values() for x in p['normalized_output']}
    per_board = []
    for board in boards:
        key = str((board['Task'], board['Dataset'], board['Metric']))
        gr = HELPERS['ranking'](board['Leaderboard'], board['Metric'])
        pr = HELPERS['ranking'](predicted[key], board['Metric'])
        ao, depths = HELPERS['ao']([x['paper_id'] for x in gr], [x['paper_id'] for x in pr])
        per_board.append({'tdm_key': key, 'gold_members': board['Leaderboard'], 'predicted_members': predicted[key],
                          'gold_member_count': len(board['Leaderboard']), 'exact_tdm_hit': key in hits,
                          'nonempty_finite_result': bool(predicted[key]), 'PC': official_values['Paper Coverage'][key],
                          'RC': official_values['Result Coverage'][key], 'RBO': official_values['RBO'][key],
                          'AO': ao, 'AO_depths': depths, 'gold_ranking': gr, 'predicted_ranking': pr})
    count = len(per_board)
    board_aggregate = {'LR_exact_tdm_hit': sum(x['exact_tdm_hit'] for x in per_board)/count,
                       'LR_nonempty_finite_result': sum(x['nonempty_finite_result'] for x in per_board)/count,
                       **{key: sum(x[key] for x in per_board)/count for key in ('PC', 'RC', 'RBO', 'AO')}}
    for key, original in [('PC','Paper Coverage'), ('RC','Result Coverage'), ('RBO','RBO')]:
        if not math.isclose(board_aggregate[key], read(out/'leaderboard_official_results.json')['gold_results'][original], abs_tol=1e-12):
            raise AssertionError('Official leaderboard aggregation mismatch')
    result['leaderboard'] = {'aggregate': board_aggregate, 'per_board': per_board, 'board_macro_denominator': count,
                             'singleton_boards': sum(x['gold_member_count'] == 1 for x in per_board),
                             'boards_ge2': sum(x['gold_member_count'] >= 2 for x in per_board),
                             'prediction_nonempty_boards': sum(x['nonempty_finite_result'] for x in per_board),
                             'conventions': 'PC/RC/RBO unchanged official; RBO ranks distinct numeric values; AO uses paper IDs, official metric direction, ID tie-break; empty prediction=0; all retained boards in denominator.'}
    save(out/'aggregate.json', {'tuple': aggregate, 'leaderboard': board_aggregate})
    save(out/'per_paper.json', per)
    save(out/'report.json', result)
    return result


def compare_arms(arms, selected):
    comparisons = {}
    order = [a for a in ARMS if a in arms]
    for left, right in itertools.combinations(order, 2):
        key = right + '_minus_' + left
        complete = all(arms[a]['status'] == 'COMPLETE' for a in (left, right))
        pair = {'left': left, 'right': right, 'comparable_complete_scope': complete,
                'selected_ids': list(selected), 'delta': None}
        if complete:
            delta = {}
            for stage in ('raw_pre_normalization', 'fullyllm'):
                a, b = arms[left]['stages'][stage], arms[right]['stages'][stage]
                if set(a['evaluated_ids']) != set(selected) or set(b['evaluated_ids']) != set(selected):
                    raise AssertionError('Complete delta requires exactly selected papers')
                delta[stage] = {'tuple': {m: {k: b['aggregate'][m][k]-a['aggregate'][m][k] for k in ('Precision','Recall','F1')} for m in METRICS},
                                'leaderboard': {k: b['leaderboard']['aggregate'][k]-a['leaderboard']['aggregate'][k] for k in a['leaderboard']['aggregate']},
                                'per_paper': {p: {m: {k: b['per_paper'][p][m][k]-a['per_paper'][p][m][k] for k in ('Precision','Recall','F1')} for m in METRICS} for p in selected}}
            pair['delta'] = delta
        else:
            pair['reason'] = 'Missing/incomplete/failed arm; no complete five-paper aggregate delta.'
        comparisons[key] = pair
    return {'delta_direction': 'right minus left; raw fractions, not percentage points', 'pairs': comparisons}


def evaluate_arm(name, run, selected, gold, board_path, official):
    dest = run/name
    dest.mkdir()
    source = ROOT/ARMS[name]
    paths = {'raw': source/'output.json', 'normalized': source/'normalized_output.json'}
    report = {'arm': name, 'status': 'FAILED', 'new_api_requests': 0, 'stages': {},
              'input_paths': {k: str(p) for k,p in paths.items()}}
    try:
        hashes = {str(p): sha(p) for p in paths.values() if p.exists()}
        raw = read(paths['raw']) if paths['raw'].exists() else {}
        norm = read(paths['normalized']) if paths['normalized'].exists() else {}
        scoped, coverage = scope_inputs(raw, norm, selected)
        coverage['missing_files'] = [str(p) for p in paths.values() if not p.exists()]
        report.update(status=coverage['status'], coverage=coverage, input_sha256=hashes)
        views = {'raw_pre_normalization': raw_view(raw, selected), 'fullyllm': scoped}
        for stage, view in views.items():
            report['stages'][stage] = evaluate_stage(dest/stage, view, gold, board_path, selected, official)
        report['input_integrity_unchanged'] = all(sha(p) == h for p,h in hashes.items())
        if not report['input_integrity_unchanged']:
            raise RuntimeError('Input changed during evaluation; retry after producer finishes')
        save(dest/'coverage.json', coverage)
        save(dest/'aggregate.json', {k: {'tuple': v['aggregate'], 'leaderboard': v['leaderboard']['aggregate'] if v['leaderboard'] else None} for k,v in report['stages'].items()})
        save(dest/'per_paper.json', {k:v['per_paper'] for k,v in report['stages'].items()})
    except Exception as error:
        report.update(status='FAILED', error_type=type(error).__name__, error=str(error))
    save(dest/'api_audit.json', {'new_api_requests': 0, 'network_attempts': list(NETWORK_ATTEMPTS), 'network_prohibited': True})
    save(dest/'report.json', report)
    return report


def run_evaluation(arm_names):
    install_boundary()
    discovery = read(ROOT/'discovery.json')
    selected = [x['paper_id'] for x in discovery['selection']['selected']]
    if len(selected) != 5 or len(set(selected)) != 5:
        raise ValueError('Expected exactly five unique frozen selected papers')
    gold, original_boards = read(GOLD), read(BOARDS)
    if len(gold) != 43 or sum(len(x['TDMs']) for x in gold.values()) != 295 or len(original_boards) != 27:
        raise ValueError('Frozen full official Gold scope differs from 43/295/27')
    if set(selected)-set(gold):
        raise ValueError('Selected ID missing from official Gold')
    derived, board_scope = derive_boards(original_boards, selected)
    if not derived:
        raise ValueError('No retained leaderboard')
    scope_path = EVALUATION/'scope/leaderboards_selected.json'
    save(scope_path, derived, frozen=True)
    scope = {'selected_ids': selected, 'selected_papers': 5,
             'selected_gold_tdmrs': sum(len(gold[p]['TDMs']) for p in selected),
             'full_gold_path': str(GOLD), 'full_gold_sha256': sha(GOLD),
             'original_27_boards_path': str(BOARDS), 'original_27_boards_sha256': sha(BOARDS),
             'discovery_sha256': sha(ROOT/'discovery.json'), 'derived_boards_sha256': sha(scope_path), **board_scope}
    save(EVALUATION/'scope/manifest.json', scope, frozen=True)
    protected = [ROOT/'discovery.json', GOLD, BOARDS, scope_path, EVALUATION/'scope/manifest.json',
                 REPO/'tdm_eval.py', REPO/'leaderboard_eval.py', TUPLE_HELPER, BOARD_HELPER]
    hashes = {str(p): sha(p) for p in protected}
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')+'_'+uuid.uuid4().hex[:6]
    run = EVALUATION/'runs'/stamp
    run.mkdir(parents=True)
    with official_modules() as official:
        arms = {name: evaluate_arm(name, run, selected, gold, scope_path, official) for name in arm_names}
    unchanged = all(sha(p) == h for p,h in hashes.items())
    status = 'FAILED' if not unchanged or any(x['status']=='FAILED' for x in arms.values()) else ('COMPLETE' if all(x['status']=='COMPLETE' for x in arms.values()) else 'INCOMPLETE')
    report = {'schema_version': 1, 'status': status, 'run_directory': str(run), 'new_api_requests': 0,
              'completion_scope': 'Requested arms and selected input artifact coverage only; no claim of whole experiment completion.',
              'all_three_arms_complete': len(arms)==3 and status=='COMPLETE', 'scope': scope, 'arms': arms,
              'comparisons': compare_arms(arms, selected), 'protected_sha256': hashes,
              'protected_files_unchanged': unchanged, 'network_attempts': NETWORK_ATTEMPTS}
    save(run/'report.json', report)
    save(run/'comparisons.json', report['comparisons'])
    save(EVALUATION/'report.json', report)
    save(EVALUATION/'latest.json', {'report':str(run/'report.json'), 'status':status, 'new_api_requests':0})
    print(json.dumps({'status':status, 'all_three_arms_complete':report['all_three_arms_complete'], 'report':str(run/'report.json'),
                      'scope':scope, 'arms':{k:v['status'] for k,v in arms.items()}, 'new_api_requests':0}, ensure_ascii=False))
    return 1 if status=='FAILED' else 2 if status=='INCOMPLETE' else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arms', nargs='+', choices=list(ARMS), default=list(ARMS))
    args = parser.parse_args()
    raise SystemExit(run_evaluation(list(dict.fromkeys(args.arms))))
