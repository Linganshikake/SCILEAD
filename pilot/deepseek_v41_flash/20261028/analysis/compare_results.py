"""Read frozen GPT-4.1/Sol and original-paper metrics; compare explicit scopes.

No model imports or calls. Missing DeepSeek results produce an incomplete report.
"""
import argparse
import csv
import math
from pathlib import Path
import statistics
import sys
sys.dont_write_bytecode = True
from offline_support import ANALYSIS, PILOT, GOLD, BOARDS, boundary, fresh_directory, read, save, sha, verify
from evaluate_offline import METRICS, metric, strict_metric, validate_inputs, per_paper_results
from inspect_runs import CASE_IDS, BRANCHES, MASK

SOL = PILOT/'gpt56_sol_fully/20261024_A2_result_type_recovery'
VAR = PILOT/'gpt56_sol_variants/20261024'
LB_KEYS = ('LR_exact_tdm_hit', 'LR_nonempty_finite_result', 'PC_official', 'RC_official',
           'RBO_official_value_rankings', 'AO_paper_id_macro_all_gold_boards')


def tuple_metrics(data):
    if 'aggregate' in data:
        return data['aggregate']
    names = dict(zip(('Task', 'Dataset', 'Metric', 'Result', 'TDM', 'TDMR'), METRICS))
    return {names[k]: v for k, v in data['metrics'].items()}


def historical_specs():
    for model, base, variants in [('GPT-4.1', PILOT/'full43_uncapped', None), ('Sol', SOL, VAR)]:
        lb = PILOT/'leaderboard_eval_full43_uncapped' if variants is None else VAR/'evaluation_references/gpt56_fully/all27'
        yield model, 'fully', base/'evaluation/metrics_with_f1.json', base/'merged/normalized_output.json', base/'merged/output.json', {'all27': lb/'paper_metrics/leaderboard_metrics.json'}
        cs = PILOT/'full43_cs' if variants is None else VAR/'fully_cs'
        yield model, 'fully_cs', cs/'evaluation/metrics_with_f1.json', cs/'normalization/embedding_normalized_output.json', base/'merged/output.json', {'all27': cs/'leaderboard_evaluation/paper_metrics/leaderboard_metrics.json'}
        for branch in BRANCHES:
            run = (PILOT/'full43_partially' if branch=='partially' else PILOT/'full43_cold_start'/branch.replace('cold_', 'order_')) if variants is None else VAR/branch
            for stage, name in [('stage1', 'normalized_output.json'), ('stage2', 'leaderboard_normalized_output.json')]:
                lbs = {scope: run/'evaluation'/scope/'paper_metrics/leaderboard_metrics.json' for scope in ('all27', 'masked10')} if stage=='stage2' else {}
                if variants is None and branch=='partially' and stage=='stage2':
                    lbs = {scope: run/'leaderboard_evaluation'/folder/'paper_metrics/leaderboard_metrics.json' for scope,folder in [('all27','all27'), ('masked10','masked_subset')]}
                yield model, branch+'_'+stage, run/'evaluation'/stage/'metrics_with_f1.json', run/stage/name, base/'merged/output.json', lbs


class Sources:
    def __init__(self): self.hashes = {}

    def read(self, path):
        path = Path(path).resolve()
        self.hashes[str(path)] = sha(path)
        return read(path)


def load_historical(sources):
    rows, missing = [], []
    gold = sources.read(GOLD)
    for model, case, mp, np, rp, lbs in historical_specs():
        try:
            data, norm, raw = sources.read(mp), sources.read(np), sources.read(rp)
            coverage = validate_inputs(raw, norm, gold)
            if data.get('input_sha256') and data['input_sha256'] != sha(np):
                raise ValueError(f'Stale tuple metrics: {mp}')
            strict = {p: strict_metric(norm[p]['normalized_output'], gold[p]['TDMs']) for p in norm}
            per = per_paper_results(sources.read(mp.parent/'eval_values.json'), norm)
            for p in per: per[p]['Strict Result numeric equality'] = strict[p]
            record = {'model': model, 'case': case, 'status': coverage['status'], 'coverage': coverage,
                      'tuple': tuple_metrics(data), 'tuple_source': str(mp),
                      'role': case_role(case), 'per_paper': per,
                      'strict_result': metric(statistics.mean(x['Precision'] for x in strict.values()), statistics.mean(x['Recall'] for x in strict.values())),
                      'leaderboards': {}, 'leaderboard_sources': {}}
            for scope, path in lbs.items():
                lb = sources.read(path)
                expected = BOARDS if scope=='all27' else MASK
                board_set = sources.read(expected)
                if lb['aggregate']['gold_leaderboards'] != len(board_set) or lb['sources']['gold_sha256'] != sha(expected):
                    raise ValueError(f'Leaderboard scope mismatch: {path}')
                if lb['sources']['prediction_sha256'] != sha(np):
                    raise ValueError(f'Stale leaderboard predictions: {path}')
                record['leaderboards'][scope] = lb['aggregate']
                record['leaderboard_sources'][scope] = str(path)
            rows.append(record)
        except FileNotFoundError as error:
            missing.append({'model': model, 'case': case, 'reason': str(error)})
    return rows, missing


def load_new(sources, evaluations, overrides):
    rows, missing = [], []
    for case in CASE_IDS:
        direct = evaluations/case
        # Main worker's direct case layout is primary; retain old all27 nesting.
        default = direct if (direct/'status.json').is_file() or not (direct/'all27/status.json').is_file() else direct/'all27'
        path = overrides.get(case, default)
        status_path = path/'status.json'
        if not status_path.is_file():
            missing.append({'model': 'DeepSeek', 'case': case, 'reason': 'Evaluation not present', 'path': str(path)})
            continue
        state = sources.read(status_path)
        if state['status'] not in ('COMPLETE', 'INCOMPLETE') or not (path/'metrics_with_f1.json').is_file():
            missing.append({'model': 'DeepSeek', 'case': case, 'reason': state['status'], 'path': str(path)})
            continue
        # Validate evaluator provenance, including original raw/normalized inputs.
        verify(sources.read(path/'source_hashes.json'))
        data = sources.read(path/'metrics_with_f1.json')
        strict = sources.read(path/'strict_result_metrics.json')
        per = sources.read(path/'per_paper_metrics.json')
        for paper in per: per[paper]['Strict Result numeric equality'] = strict['per_paper'][paper]
        record = {'model': 'DeepSeek', 'case': case, 'status': state['status'], 'coverage': data['coverage'],
                  'tuple': data['aggregate'], 'tuple_source': str(path/'metrics_with_f1.json'),
                  'role': case_role(case), 'per_paper': per, 'strict_result': strict['aggregate'],
                  'leaderboards': {}, 'leaderboard_sources': {}}
        for scope in ('all27', 'masked10'):
            lp = path if scope=='all27' else (path.parent/'masked10' if path.name=='all27' else path/'masked10')
            fp = lp/'leaderboard/paper_metrics/leaderboard_metrics.json'
            if not fp.is_file(): continue
            s = sources.read(lp/'status.json')
            if s['status'] not in ('COMPLETE', 'INCOMPLETE'): continue
            expected = BOARDS if scope=='all27' else MASK
            if s['coverage']['boards_sha256'] != sha(expected):
                raise ValueError(f'Cannot label these boards as {scope}: {lp}')
            if sha(s['paths']['normalized']) != data['input_sha256']:
                raise ValueError(f'Leaderboard and tuple predictions differ: {lp}')
            verify(sources.read(lp/'source_hashes.json'))
            record['leaderboards'][scope] = sources.read(fp)['aggregate']
            record['leaderboard_sources'][scope] = str(fp)
        rows.append(record)
    return rows, missing


def case_role(case):
    return 'stage1_diagnostic' if case.endswith('_stage1') else 'primary'


def provenance(sources):
    frozen = sources.read(VAR/'experiment_manifest.json')
    return {'original_repository': str(PILOT.parent/'emnlp2024-leaderboard-generation'),
            'original_repository_HEAD': frozen['upstream_commit'],
            'frozen_outer_archive_commit': frozen['archive_commit'],
            'distinction': 'Original evaluator repository HEAD and historical outer/archive freeze are distinct commits.',
            'partially_primary': 'stage2; supersedes the 24-Oct report stage1-primary wording',
            'generation_context_user_confirmed': {'api_model_and_response_alias': 'deepseek-flash',
                'documented_model': 'DeepSeek-V4.1-Flash-1017', 'thinking': 'enabled', 'reasoning_effort': 'high',
                'output_cap': None, 'scope': 'Generation context only; this utility makes no API calls and does not certify execution/usage.'}}


def original_paper(sources):
    path = PILOT/'weekly_report_20261024/sources/paper_reference.json'
    ref = sources.read(path)
    # Local verified transcription; preserve row scopes, reported F1 and SD.
    rows = []
    for table in ('table_3', 'table_4', 'table_12', 'table_5', 'table_17'):
        for r in ref['tables'][table]['rows']:
            rows.append({'table': table, **r})
    return {'source': str(path), 'source_sha256': sha(path), 'unit': 'percent_0_to_100',
            'rows': rows, 'other_scopes_separate': ref.get('supplemental_GPT4_leaderboard_scopes', []),
            'comparability': 'Published reference, not re-evaluation. AxCell=36 papers; other main rows=43. Table5/17 main boards=27 where stated. ColdStart is a three-order mean. Masked and threshold2/62-board appendix rows are separate; never merged with all27. Published AO is not the official code numeric-value RBO.'}


def cold_summaries(rows):
    summaries = []
    for model in ('GPT-4.1', 'Sol', 'DeepSeek'):
        for scope in ('all27', 'masked10'):
            runs = [r for r in rows if r['model']==model and r['case'] in ('cold_default_stage2', 'cold_0_stage2', 'cold_42_stage2') and r['status']=='COMPLETE' and scope in r['leaderboards']]
            if len(runs)!=3: continue
            summaries.append({'model': model, 'scope': scope, 'orders': [r['case'] for r in runs], 'runs': 3,
                              'statistic': 'Arithmetic mean of three run-level leaderboard metrics; SD is sample SD, ddof=1',
                              'metrics': {k: {'mean': statistics.mean(r['leaderboards'][scope][k] for r in runs),
                                              'sd': statistics.stdev(r['leaderboards'][scope][k] for r in runs)} for k in LB_KEYS}})
    return summaries


def render(report):
    lines = ['# Offline experiment comparison', '', f"Status: **{report['status']}**. {report['readiness_note']}", '',
             'Partially **stage2 is the primary result**; stage1 is retained as a diagnostic. Both stages and source files remain in comparison.json and CSV. This supersedes the 24-Oct report convention.', '',
             f"Original repository HEAD: `{report['provenance']['original_repository_HEAD']}`. Frozen outer/archive commit: `{report['provenance']['frozen_outer_archive_commit']}`. These are distinct provenance fields.", '',
             'Local scores below are percentages. Tuple cells show P / R / F1; macro F1 uses macro P/R. Partial rows use only the displayed observed-paper denominator. No full-scope improvement claim is made for partial rows.', '',
             '## Local tuple metrics', '', '| Model / case | Status; papers; Gold; predictions | '+' | '.join(METRICS)+' | Strict Result |',
             '|---|---|'+'---|'*7]
    def triple(x): return ' / '.join(f'{100*x[k]:.2f}' for k in ('Precision', 'Recall', 'F1'))
    for r in report['local_rows']:
        c = r['coverage']
        lines.append(f"| {r['model']} / {r['case']} ({r['role']}) | {r['status']}; {c['evaluated_papers']}/{c['official_papers']}; {c['evaluated_gold_tdmrs']}/{c['official_gold_tdmrs']}; {c['predictions']} | "+' | '.join(triple(r['tuple'][k]) for k in METRICS)+' | '+triple(r['strict_result'])+' |')
    lines += ['', '## Local leaderboards', '', 'LR means exact normalized TDM hit. Nonempty additionally requires a finite converted Result. PC/RC/RBO use unchanged official code; AO ranks paper IDs. All target boards, including empty boards, stay in each macro denominator. The copied helper’s old LR_primary prose does not override these labels.', '',
              '| Model / case | Scope / boards | Papers | LR | Nonempty | PC | RC | RBO (values) | AO (paper IDs) |', '|---|---|---|---|---|---|---|---|---|']
    for r in report['local_rows']:
        for scope, b in r['leaderboards'].items():
            lines.append(f"| {r['model']} / {r['case']} | {scope} / {b['gold_leaderboards']} | {r['coverage']['evaluated_papers']}/43 | "+' | '.join(f'{100*b[k]:.2f}' for k in LB_KEYS)+' |')
    lines += ['', 'Sol Fully CS all27 LR is read from its own source: 24/27 = 88.89%. GPT-4.1 Fully CS has 25/27 exact TDM hits; its 24/27 nonempty rate is a different column.', '', '## Cold-order means', '', '| Model | Scope | LR | Nonempty | PC | RC | RBO | AO |', '|---|---|---|---|---|---|---|---|']
    for s in report['cold_three_order_summaries']:
        lines.append(f"| {s['model']} | {s['scope']} | "+' | '.join(f"{100*s['metrics'][k]['mean']:.2f} ± {100*s['metrics'][k]['sd']:.2f}" for k in LB_KEYS)+' |')
    lines += ['', 'Mean ± sample SD across all three completed orders. Individual order rows above are not directly equivalent to the published ColdStart mean.', '', '## Original-paper reference (published percentages)', '', report['original_paper']['comparability'], '',
              '| Table | Model / setting / normalization | Papers / boards | Metric | P | R | F1 | LR | PC | RC | AO |', '|---|---|---|---|---|---|---|---|---|---|---|']
    def val(v):
        if v is None: return '—'
        if isinstance(v, dict): return f"{v['mean']:.2f} ± {v['sd']:.2f}"
        return f'{v:.2f}'
    for r in report['original_paper']['rows']:
        vs = r['values']
        metrics = {k+' IIM': v for k,v in vs.items()} if r['table']=='table_4' else { {'table_3':'TDMR','table_12':'TDM','table_5':'Leaderboard','table_17':'Leaderboard mean ± SD'}[r['table']]: vs}
        for name, values in metrics.items():
            lines.append(f"| {r['table']} | {r['model']} / {r['setting']} / {r.get('normalization','LLM')} | {r['paper_count']} / {r.get('gold_leaderboard_count') or 'n/a'} | {name} | "+' | '.join(val(values.get(k)) for k in ('precision','recall','f1','LR','PC','RC','AO'))+' |')
    lines += ['', 'Published scores are retained as reported, including F1 and SD. They do not establish equality between paper definitions and code quirks (Result substring matching; numeric-value RBO versus paper-ID AO). Masked/threshold-2 appendix values are retained separately in comparison.json.', '', '## Missing or unfinished inputs', '']
    lines += ['- '+str(x) for x in report['missing']] or ['None.']
    lines += ['', 'Sources and SHA-256 hashes: source_hashes.json. Exact per-row source paths, coverage IDs, and full precision values: comparison.json.', '']
    return '\n'.join(lines)


def write_csv(out, rows):
    """Long CSVs include every observed paper; never assume an extraction count."""
    with (out/'per_paper_comparison.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['model','case','role','status','paper_id','metric','Precision','Recall','F1','tuple_source'])
        writer.writeheader()
        for r in rows:
            for paper, metrics in r['per_paper'].items():
                for name, values in metrics.items():
                    writer.writerow({k:r[k] for k in ('model','case','role','status','tuple_source')} | {'paper_id':paper,'metric':name} | values)
    fields = ['model','case','role','status','scope','papers','gold_tdmrs','predictions','metric','Precision','Recall','F1','value','source']
    with (out/'comparison.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for r in rows:
            c=r['coverage']; base={k:r[k] for k in ('model','case','role','status')}
            base.update(papers=c['evaluated_papers'],gold_tdmrs=c['evaluated_gold_tdmrs'],predictions=c['predictions'])
            for name, values in {**r['tuple'], 'Strict Result numeric equality':r['strict_result']}.items():
                writer.writerow(base | {'scope':'observed_papers','metric':name,'source':r['tuple_source']} | values)
            for scope, lb in r['leaderboards'].items():
                for name in LB_KEYS:
                    writer.writerow(base | {'scope':scope,'metric':name,'value':lb[name],'source':r['leaderboard_sources'][scope]})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evaluations', type=Path, default=ANALYSIS/'evaluations')
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--run', action='append', default=[], metavar='CASE=PATH', help='Override one all27 evaluation directory')
    args = p.parse_args()
    boundary()
    out = fresh_directory(args.out)
    overrides = {}
    for item in args.run:
        case, path = item.split('=', 1)
        if case not in CASE_IDS: raise ValueError(f'Unknown case: {case}')
        overrides[case] = Path(path)
    sources = Sources()
    historical, hm = load_historical(sources)
    current, cm = load_new(sources, args.evaluations, overrides)
    required_scopes = lambda r: {'all27'}
    unfinished = [{'model':'DeepSeek', 'case':r['case'], 'reason':'Partial coverage or missing leaderboard scope'} for r in current if r['status']!='COMPLETE' or not required_scopes(r).issubset(r['leaderboards'])]
    rows = historical+current
    missing = hm+cm+unfinished
    report = {'status': 'INCOMPLETE' if missing else 'COMPLETE', 'new_api_requests': 0,
              'readiness_note': 'Completion covers ten 43-paper/295-Gold evaluations and their all27 boards. Masked10 is optional and separately labeled. Evaluation report only; not an audit of API generation, replay, usage, or normalization semantics.',
              'local_rows': rows, 'original_paper': original_paper(sources), 'missing': missing,
              'provenance': provenance(sources),
              'cold_three_order_summaries': cold_summaries(rows)}
    report['source_integrity'] = verify(sources.hashes)
    save(out/'comparison.json', report)
    save(out/'source_hashes.json', sources.hashes)
    write_csv(out, rows)
    (out/'report.md').write_text(render(report), encoding='utf-8')
    print(f"{report['status']}: {len(historical)} historical rows, {len(current)} DeepSeek rows, {len(missing)} unavailable/unfinished")
    return 0 if report['status']=='COMPLETE' else 2


if __name__ == '__main__':
    sys.exit(main())
