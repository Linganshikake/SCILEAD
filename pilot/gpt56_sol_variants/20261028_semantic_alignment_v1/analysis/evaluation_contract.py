"""Readiness, provenance and scope checks around byte-identical audited scoring."""
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from offline_support import (ANALYSIS, GOLD, BOARDS, boundary, read, save, sha,
                             verify, require_output, within)
from evaluate_offline import METRICS, aggregate_results, per_paper_results, validate_inputs

boundary()
BASELINE = ANALYSIS.parent.with_name('20261024')
EXPERIMENT = ANALYSIS.parent
RAW = BASELINE/'inputs/output.json'
BRANCHES = ('partially', 'cold_default', 'cold_0', 'cold_42')
COLD = BRANCHES[1:]
CASES = tuple(f'{b}_stage{s}' for b in BRANCHES for s in (1, 2))
LB_KEYS = ('LR_exact_tdm_hit', 'LR_nonempty_finite_result', 'PC_official',
           'RC_official', 'RBO_official_value_rankings', 'AO_paper_id_macro_all_gold_boards')
SCORES = ('Precision', 'Recall', 'F1')


class Evidence:
    def __init__(self):
        self.hashes = {}

    def read(self, path):
        p = Path(path).resolve()
        before = sha(p)
        value = read(p)
        if sha(p) != before or (str(p) in self.hashes and self.hashes[str(p)] != before):
            raise ValueError(f'File changed while reading: {p}')
        self.hashes[str(p)] = before
        return value

    def absorb(self, hashes):
        verify(hashes)
        for p, h in hashes.items():
            p = str(Path(p).resolve())
            if p in self.hashes and self.hashes[p] != h:
                raise ValueError(f'Conflicting source hashes: {p}')
            self.hashes[p] = h


def verify_audit():
    manifest = read(ANALYSIS/'audit_manifest.json')
    result = verify(manifest['source_hashes'])
    for pair in manifest['copies']:
        if Path(pair['source']).read_bytes() != Path(pair['copy']).read_bytes():
            raise ValueError(f'Audited copy differs: {pair["copy"]}')
    return result


def stage_paths(root, case):
    if case not in CASES:
        raise ValueError(f'Unknown case: {case}')
    branch, stage = case.rsplit('_', 1)
    folder = Path(root)/branch/stage
    name = 'normalized_output.json' if stage == 'stage1' else 'leaderboard_normalized_output.json'
    return folder/name, folder/'summary.json'


def validate_summary(summary, output):
    if summary.get('status') != 'COMPLETE':
        raise ValueError('Stage summary is not COMPLETE')
    if summary.get('papers') != 43 or summary.get('records') != 335:
        raise ValueError('Stage summary must declare 43 papers / 335 records')
    if not isinstance(summary.get('output_path'), str) or Path(summary['output_path']).resolve() != Path(output).resolve():
        raise ValueError('Stage summary output_path mismatch')
    actual = sha(output)
    if summary.get('output_sha256') != actual:
        raise ValueError('Stage summary output_sha256 mismatch')
    return actual


def full_scope(coverage):
    expected = {'status':'COMPLETE', 'official_papers':43, 'official_gold_tdmrs':295,
                'raw_papers':43, 'evaluated_papers':43, 'tuple_macro_denominator':43,
                'evaluated_gold_tdmrs':295, 'predictions':335}
    for k, v in expected.items():
        if coverage.get(k) != v:
            raise ValueError(f'Full-scope mismatch: {k}={coverage.get(k)!r}, expected {v!r}')
    for k in ('missing_raw_ids', 'missing_normalized_ids', 'raw_without_normalization_ids'):
        if coverage.get(k) != []:
            raise ValueError(f'Incomplete paper scope: {k}')


def ready_stage(root, case, evidence=None):
    """Missing/unfinished/partially-written stages are pending; complete mismatches fail."""
    e = evidence if evidence is not None else Evidence()
    output, summary_path = stage_paths(root, case)
    if not summary_path.is_file():
        return {'status':'PENDING', 'reason':'Missing stage summary', 'missing':[str(summary_path)]}
    # JSON syntax errors can be a writer in progress. Duplicate keys remain errors.
    import json
    try:
        summary = e.read(summary_path)
    except json.JSONDecodeError:
        return {'status':'PENDING', 'reason':'Stage summary is not yet valid JSON'}
    if summary.get('status') != 'COMPLETE':
        return {'status':'PENDING', 'reason':f'Stage summary status: {summary.get("status")!r}'}
    if not output.is_file():
        raise ValueError('COMPLETE stage output is missing')
    validate_summary(summary, output)
    raw, normalized, gold = e.read(RAW), e.read(output), e.read(GOLD)
    coverage = validate_inputs(raw, normalized, gold)
    full_scope(coverage)
    if len(e.read(BOARDS)) != 27:
        raise ValueError('Expected all 27 Gold boards')
    branch = case.rsplit('_', 1)[0]
    config = e.read(Path(root)/branch/'config.json')
    input_path = (Path(root)/'inputs/output.json').resolve()
    if Path(config['input_path']).resolve() != input_path:
        raise ValueError('Config input_path must point to this experiment inputs/output.json')
    e.read(input_path)
    if sha(input_path) != sha(RAW):
        raise ValueError('Extraction must be byte-identical to the Sol baseline inputs/output.json')
    if config.get('input_sha256') != sha(input_path):
        raise ValueError('Config input_sha256 mismatch')
    for key, expected, filename in [('gold_path', GOLD, 'gold.json'), ('leaderboards_path', BOARDS, 'leaderboards.json')]:
        actual = Path(config[key]).resolve()
        if actual not in (expected.resolve(), (Path(root)/'inputs'/filename).resolve()):
            raise ValueError(f'Config {key} mismatch')
        e.read(actual)
        if sha(actual) != sha(expected):
            raise ValueError(f'Gold snapshot must be byte-identical: {key}')
    def paper_order(conf):
        order = conf['paper_order']
        if isinstance(order, str):
            order = e.read(order)['papers']
        if not isinstance(order, list) or len(order) != 43 or len(set(order)) != 43:
            raise ValueError('Config paper_order must contain 43 distinct paper IDs')
        return order
    order = paper_order(config)
    baseline_config = e.read(BASELINE/branch/'config.json')
    if list(normalized) != order or order != paper_order(baseline_config):
        raise ValueError('Config/normalized paper order differs from the paired baseline branch')
    validate_summary(e.read(summary_path), output)
    verify(e.hashes)
    return {'status':'READY', 'normalized':str(output.resolve()), 'summary':str(summary_path.resolve()),
            'coverage':coverage, 'input_hashes':dict(e.hashes)}


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'Nonfinite/non-numeric metric: {value!r}')
    return value


def close(actual, expected, label):
    if not math.isclose(finite(actual), finite(expected), rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f'Metric inconsistency at {label}: {actual} != {expected}')


def load_evaluation(folder, normalized_path, evidence=None):
    """Validate complete files, provenance, exact scope and metric aggregation."""
    e = evidence if evidence is not None else Evidence()
    folder = Path(folder).resolve()
    state = e.read(folder/'status.json')
    if state.get('status') != 'COMPLETE' or state.get('official_mains_executed') is not True:
        raise ValueError(f'Evaluation is not complete: {folder}')
    for k, p in {'raw':RAW, 'normalized':normalized_path, 'gold':GOLD, 'boards':BOARDS}.items():
        if Path(state['paths'][k]).resolve() != Path(p).resolve():
            raise ValueError(f'Evaluation input path mismatch: {k}')
    sources = e.read(folder/'source_hashes.json')
    for p in (RAW, normalized_path, GOLD, BOARDS):
        if sources.get(str(Path(p).resolve())) != sha(p):
            raise ValueError(f'Evaluation source hash mismatch: {p}')
    e.absorb(sources)
    e.absorb(e.read(folder/'leaderboard/source_hashes.json'))
    audit = e.read(folder/'leaderboard/adapter_audit.json')
    if audit.get('formulas_modified') is not False:
        raise ValueError('Unchanged-formula audit missing')
    e.absorb({audit['rbo_source']:audit['rbo_source_sha256']})
    for helper in audit['helpers']:
        e.absorb({helper['source']:helper['sha256'], helper['copy']:helper['sha256']})
    data = e.read(folder/'metrics_with_f1.json')
    coverage = e.read(folder/'coverage.json')
    full_scope(coverage)
    if coverage != state['coverage'] or coverage != data['coverage'] or data.get('status') != 'COMPLETE':
        raise ValueError('Conflicting evaluation coverage/status')
    if coverage.get('gold_leaderboards') != 27 or coverage.get('board_scope') != 'all27':
        raise ValueError('Expected unchanged all27 board scope')
    if coverage.get('gold_sha256') != sha(GOLD) or coverage.get('boards_sha256') != sha(BOARDS):
        raise ValueError('Gold hash mismatch')
    norm, gold, raw, boards = e.read(normalized_path), e.read(GOLD), e.read(RAW), e.read(BOARDS)
    actual_coverage = validate_inputs(raw, norm, gold)
    full_scope(actual_coverage)
    if any(coverage[k] != v for k, v in actual_coverage.items()):
        raise ValueError('Stored coverage differs from actual inputs')
    board_keys = {str((b['Task'], b['Dataset'], b['Metric'])) for b in boards}
    if set(coverage['board_ids']) != board_keys or len(coverage['board_ids']) != 27:
        raise ValueError('Board membership mismatch')
    if data.get('input_sha256') != sha(normalized_path) or Path(data['input_path']).resolve() != Path(normalized_path).resolve():
        raise ValueError('Stale tuple metrics')
    official = e.read(folder/'tdm_official/eval_results.json')
    values = e.read(folder/'tdm_official/eval_values.json')
    per = e.read(folder/'per_paper_metrics.json')
    if per != per_paper_results(values, norm) or set(per) != set(gold):
        raise ValueError('Per-paper metrics differ from official output')
    expected = aggregate_results(official)
    for name in METRICS:
        for score in SCORES:
            close(data['aggregate'][name][score], expected[name][score], name+'/'+score)
        for score in SCORES[:2]:
            close(data['aggregate'][name][score], sum(finite(p[name][score]) for p in per.values())/43, name+'/macro '+score)
    lb = e.read(folder/'leaderboard/paper_metrics/leaderboard_metrics.json')
    if lb['sources']['gold_sha256'] != sha(BOARDS):
        raise ValueError('Leaderboard Gold hash mismatch')
    helper_norm = folder/'leaderboard/helper_view/normalized_output.json'
    if lb['sources']['prediction_sha256'] != sha(helper_norm) or e.read(helper_norm) != norm:
        raise ValueError('Leaderboard predictions differ from tuple predictions')
    lb_official = e.read(folder/'leaderboard/official/eval_results.json')['gold_results']
    execution = e.read(folder/'leaderboard/official/execution_status.json')
    if execution.get('status') != 'COMPLETE' or execution.get('original_main_executed') is not True:
        raise ValueError('Official leaderboard execution incomplete')
    detail = e.read(folder/'leaderboard/leaderboards/gold_vs_predicted.json')
    if len(detail) != 27 or {b['tdm_key'] for b in detail} != board_keys:
        raise ValueError('Leaderboard diagnostic scope mismatch')
    a = lb['aggregate']
    if a['gold_leaderboards'] != 27:
        raise ValueError('Leaderboard denominator must be 27')
    for target, key in [('PC_official','Paper Coverage'), ('RC_official','Result Coverage'), ('RBO_official_value_rankings','RBO')]:
        close(a[target], lb_official[key], target)
    for target, key in [('LR_exact_tdm_hit','tdm_hit_before_numeric_conversion'), ('LR_nonempty_finite_result','valid_result_nonempty'),
                        ('PC_official','Paper Coverage'), ('RC_official','Result Coverage'),
                        ('RBO_official_value_rankings','official_RBO_value_ranking'), ('AO_paper_id_macro_all_gold_boards','AO_paper_id_ranking')]:
        close(a[target], sum(float(b[key]) for b in detail)/27, target+'/all27')
    for b in detail:
        for v in b['predicted_official_numeric'].values(): finite(v)
    verify(e.hashes)
    return {'coverage':coverage, 'tuple':data['aggregate'], 'leaderboard':a, 'per_paper':per,
            'source':str(folder), 'normalized':str(Path(normalized_path).resolve()), 'input_sha256':sha(normalized_path)}


def verify_baseline_parity(folder, case, evidence=None):
    """Exact numeric/JSON equality to Sol's historical outputs; never import runtime."""
    e = evidence if evidence is not None else Evidence()
    folder = Path(folder)
    branch, stage = case.rsplit('_', 1)
    historical = BASELINE/branch/'evaluation'
    pairs = [(folder/'tdm_official'/name, historical/stage/name)
             for name in ('eval_results.json', 'eval_values.json')]
    pairs.append((folder/'per_paper_metrics.json', historical/stage/'per_paper_metrics.json'))
    compared = []
    for new, old in pairs:
        if e.read(new) != e.read(old):
            raise ValueError(f'Baseline parity mismatch: {case}/{old.name}')
        compared.append(str(old))
    for name, fields in [('metrics_with_f1.json', ('aggregate', 'mean_per_paper_f1_SEPARATE')),
                         ('strict_result_metrics.json', ('aggregate', 'per_paper'))]:
        current, previous = e.read(folder/name), e.read(historical/stage/name)
        for field in fields:
            if current[field] != previous[field]:
                raise ValueError(f'Baseline parity mismatch: {case}/{name}/{field}')
        compared.append(str(historical/stage/name))
    if stage == 'stage2':
        for relative in ('official/eval_results.json', 'official/eval_values.json',
                         'official/generated_leaderboards.json', 'official/gold_after_official_conversion.json',
                         'paper_metrics/leaderboard_metrics_by_tdm.json', 'leaderboards/gold_vs_predicted.json'):
            if e.read(folder/'leaderboard'/relative) != e.read(historical/'all27'/relative):
                raise ValueError(f'Baseline parity mismatch: {case}/{relative}')
            compared.append(str(historical/'all27'/relative))
        relative = 'paper_metrics/leaderboard_metrics.json'
        if e.read(folder/'leaderboard'/relative)['aggregate'] != e.read(historical/'all27'/relative)['aggregate']:
            raise ValueError(f'Baseline leaderboard aggregate mismatch: {case}')
        compared.append(str(historical/'all27'/relative))
    verify(e.hashes)
    return {'status':'PASSED', 'case':case, 'comparison':'Exact equality; no tolerance or rounding',
            'historical_files_compared':compared,
            'stage1_leaderboards':'New offline diagnostics; historical baseline stored boards only for stage2'}


def seal_evaluation(folder, stage):
    folder = require_output(folder)
    manifest = folder/'verified_complete.json'
    if manifest.exists():
        raise ValueError('Refusing to replace completion seal')
    files = {str(p.relative_to(folder)):sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
    for name in ('status.json', 'metrics_with_f1.json', 'per_paper_metrics.json'):
        if name not in files:
            raise ValueError('Cannot seal missing evaluation artifacts')
    inputs = dict(stage['input_hashes'])
    for name in ('audit_manifest.json', 'evaluation_contract.py', 'evaluate_ready.py'):
        inputs[str(ANALYSIS/name)] = sha(ANALYSIS/name)
    verify(inputs)
    save(manifest, {'status':'COMPLETE', 'scope':'43 papers / 335 predictions / 295 Gold / all27',
                    'input_hashes':inputs, 'artifacts':files, 'new_api_requests':0})


def verified_evaluation(folder, normalized_path, evidence=None):
    e = evidence if evidence is not None else Evidence()
    folder = require_output(folder)
    seal = e.read(folder/'verified_complete.json')
    if seal.get('status') != 'COMPLETE' or not seal.get('artifacts'):
        raise ValueError('Missing verified completion seal')
    paths = {}
    for relative, digest in seal['artifacts'].items():
        p = (folder/relative).resolve()
        if not within(p, folder) or p == folder:
            raise ValueError('Artifact path escapes evaluation directory')
        paths[str(p)] = digest
    actual = {str(p.resolve()) for p in folder.rglob('*') if p.is_file() and p != folder/'verified_complete.json'}
    if set(paths) != actual:
        raise ValueError('Evaluation artifact inventory changed')
    e.absorb(paths)
    e.absorb(seal['input_hashes'])
    return load_evaluation(folder, normalized_path, e)
