"""Same-case offline comparison. Stage2 primary; incomplete variants stay missing."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

sys.dont_write_bytecode = True
from offline_support import ANALYSIS, boundary, fresh_directory, save, verify, sha
from evaluation_contract import (BASELINE, EXPERIMENT, CASES, COLD, METRICS, SCORES, LB_KEYS,
                                 Evidence, finite, verify_audit, ready_stage, stage_paths,
                                 load_evaluation, verified_evaluation, verify_baseline_parity)


def scalar_differences(variant, baseline):
    if set(variant) != set(baseline):
        raise ValueError('Cannot subtract different metric sets')
    return {k:finite(variant[k])-finite(baseline[k]) for k in baseline}


def three_order_stats(runs):
    if set(runs) != set(COLD):
        raise ValueError('Cold statistics require exactly cold_default, cold_0, cold_42')
    keys = set(runs[COLD[0]])
    if not keys or any(set(runs[b]) != keys for b in COLD):
        raise ValueError('Cold metric sets must agree and be nonempty')
    return {k:{'mean':statistics.mean(finite(runs[b][k]) for b in COLD),
               'sample_sd':statistics.stdev(finite(runs[b][k]) for b in COLD), 'n':3}
            for k in runs[COLD[0]]}


def flatten(row):
    return {**{f'{m}/{s}':finite(row['tuple'][m][s]) for m in METRICS for s in SCORES},
            **{k:finite(row['leaderboard'][k]) for k in LB_KEYS}}


def paper_change_summary(rows):
    """Count both directions and retain exact paired paper examples, without attribution."""
    result=[]
    for case in (c for c in CASES if c.endswith('stage2')):
        for metric in ('TDM Exact Match','TDMR Exact Match'):
            paired=[r for r in rows if r['case']==case and r['metric']==metric and r['status']=='PAIRED_COMPLETE']
            if not paired:
                continue
            up=sorted((r for r in paired if r['delta_F1']>1e-12), key=lambda r:(-r['delta_F1'],r['paper_id']))
            down=sorted((r for r in paired if r['delta_F1'] < -1e-12), key=lambda r:(r['delta_F1'],r['paper_id']))
            brief=lambda r:{'paper_id':r['paper_id'],'baseline_F1':r['baseline_F1'],'variant_F1':r['variant_F1'],'delta_F1':r['delta_F1']}
            result.append({'case':case,'metric':metric,'paired_papers':len(paired),
                           'improved':len(up),'regressed':len(down),'unchanged':len(paired)-len(up)-len(down),
                           'top_improvements':[brief(r) for r in up[:3]],'top_regressions':[brief(r) for r in down[:3]],
                           'equality_tolerance':1e-12})
    return result


def compare(evaluations):
    verify_audit()
    evidence = Evidence()
    evidence.read(ANALYSIS/'audit_manifest.json')
    rows, missing, differences = [], [], []
    indexed = {}
    for model, root in [('baseline', BASELINE), ('prompt_improvement_variant', EXPERIMENT)]:
        for case in CASES:
            try:
                dest = ANALYSIS/'baseline_evaluations'/case if model=='baseline' else evaluations/case
                if dest.exists() and any(dest.iterdir()):
                    verified_evaluation(dest, stage_paths(root, case)[0], evidence)
                stage = ready_stage(root, case, evidence)
                if stage['status'] != 'READY':
                    missing.append({'model':model, 'case':case, **stage})
                    continue
                if not (dest/'status.json').is_file():
                    missing.append({'model':model,'case':case,'status':'PENDING','reason':'Evaluation not present','path':str(dest)})
                    continue
                row = verified_evaluation(dest, stage['normalized'], evidence)
                if model == 'baseline':
                    verify_baseline_parity(dest, case, evidence)
                row.update(model=model, case=case, role='primary' if case.endswith('stage2') else 'diagnostic', status='COMPLETE')
                rows.append(row)
                indexed[model, case] = row
            except Exception as error:
                missing.append({'model':model,'case':case,'status':'ERROR','reason':str(error)})
    for case in CASES:
        baseline, variant = indexed.get(('baseline',case)), indexed.get(('prompt_improvement_variant',case))
        if baseline and variant:
            if set(baseline['per_paper']) != set(variant['per_paper']):
                raise ValueError('Paired paper sets differ')
            differences.append({'case':case, 'role':variant['role'], 'unit':'fraction; delta=variant-baseline',
                                'metrics':scalar_differences(flatten(variant),flatten(baseline))})
    cold = []
    for stage in ('stage1','stage2'):
        for model in ('baseline','prompt_improvement_variant','paired_delta'):
            runs = {}
            for branch in COLD:
                case = branch+'_'+stage
                if model == 'paired_delta':
                    a, b = indexed.get(('prompt_improvement_variant',case)), indexed.get(('baseline',case))
                    if a and b: runs[branch] = scalar_differences(flatten(a),flatten(b))
                elif (model,case) in indexed:
                    runs[branch] = flatten(indexed[model,case])
            cold.append({'model':model,'stage':stage,'status':'COMPLETE' if len(runs)==3 else 'INCOMPLETE',
                         'orders_present':list(runs), 'metrics':three_order_stats(runs) if len(runs)==3 else None,
                         'definition':'Three run-level metrics; arithmetic mean and sample SD (ddof=1). Paired delta SD is the SD of three paired differences.'})
    report = {'status':'ERROR' if any(x['status']=='ERROR' for x in missing) else 'INCOMPLETE' if missing else 'COMPLETE',
              'created_utc':datetime.now(timezone.utc).isoformat(), 'new_api_requests':0,
              'scope':{'papers':43,'predictions':335,'gold_annotations':295,'gold_boards':27,'primary_stage':'stage2','diagnostic_stage':'stage1'},
              'method':{'label':'Authorized semantic-alignment prompt-improvement variant; not the original baseline',
                        'declared_change':'Generic semantic matching additions only in masked-normalization and leaderboard-normalization system Prompts.',
                        'prompt_additions_user_reported':'Same additions as DeepSeek semantic_alignment_v1; no new design.',
                        'generation_user_reported':{'model':'gpt-5.6-sol','reasoning_effort':'medium','max_completion_tokens':32768},
                        'method_statement_source':'User/main handoff; runtime/Prompt integrity audit is outside this utility.',
                        'raw_extraction':str(BASELINE/'inputs/output.json'),
                        'raw_sha256':sha(BASELINE/'inputs/output.json'),
                        'evaluation':'Unchanged official tdm_eval and leaderboard_eval via byte-identical prior audited evaluator/helpers.',
                        'tuple_f1':'Harmonic mean of official macro P/R; never mean of per-paper F1.',
                        'LR':'Exact normalized TDM hit before numeric conversion.',
                        'finite_nonempty':'At least one finite converted Result for a Gold board.',
                        'RBO':'Official deduplicated numeric-value rankings; not paper IDs.',
                        'AO':'Paper-ID rankings, deterministic paper-ID tie-break, empty boards=0; macro over all27.',
                        'global_audit':'Main task owns global usage/integrity, Prompt and runtime verification, and qualitative examples.'},
              'local_rows':rows,'paired_differences':differences,'cold_three_order_summaries':cold,
              'missing':missing,'cross_model_references':[],
              'cross_model_note':'DeepSeek results are excluded from paired Sol statistics (295 vs 335 predictions).'}
    for stage, label in [('stage2','primary'), ('stage1','diagnostic')]:
        absent = [x for x in missing if x['case'].endswith(stage)]
        report[label+'_status'] = 'ERROR' if any(x['status']=='ERROR' for x in absent) else 'INCOMPLETE' if absent else 'COMPLETE'
    report['stage2_paper_changes']=paper_change_summary(list(per_paper_rows(report)))
    report['source_integrity'] = verify(evidence.hashes)
    return report, evidence


def per_paper_rows(report):
    index = {(r['model'],r['case']):r for r in report['local_rows']}
    for case in CASES:
        base, var = index.get(('baseline',case)), index.get(('prompt_improvement_variant',case))
        if not base:
            continue
        for paper in sorted(base['per_paper']):
            for metric in METRICS:
                a = base['per_paper'][paper][metric]
                b = var['per_paper'][paper][metric] if var else None
                delta = scalar_differences(b,a) if b else None
                yield {'case':case,'role':base['role'],'paper_id':paper,'metric':metric,
                       'status':'PAIRED_COMPLETE' if var else 'VARIANT_UNAVAILABLE',
                       **{f'baseline_{s}':a[s] for s in SCORES},
                       **{f'variant_{s}':b[s] if b else None for s in SCORES},
                       **{f'delta_{s}':delta[s] if delta else None for s in SCORES}}


def write_csv(path, rows, fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def render(report):
    index = {(r['model'], r['case']):r for r in report['local_rows']}
    lines = ['# GPT-5.6 Sol paired semantic-alignment comparison', '',
             f"Status: **{report['status']}**. Primary stage2: **{report['primary_status']}**. Diagnostic stage1: **{report['diagnostic_status']}**.",
             f"Generated UTC: {report['created_utc']}", '',
             'Baseline: 20261024. Variant directory identifier: 20261028_semantic_alignment_v1 (not a claim about execution dates).',
             'Each scored stage has 43 papers, 335 predictions, 295 Gold annotations and all 27 Gold boards. Extraction bytes match the Sol baseline.',
             'Main-agent handoff: the same semantic-alignment Prompt additions as DeepSeek; Sol medium / 32768 generation settings unchanged. Runtime and Prompt audit remain with the main agent.', '',
             'Tuple P/R are official per-paper macros; F1 is their harmonic mean. LR is exact TDM hit; finite nonempty is separate. Official RBO ranks deduplicated numeric values. AO ranks paper IDs with deterministic ties; empty boards count as zero in all27.',
             'Tables show percentages; deltas are percentage points (variant minus baseline). Pending values are missing, never zero.', '']
    for stage, role in [('stage2','Primary'), ('stage1','Diagnostic')]:
        lines += [f'## {role}: {stage}', '', 'Tuple cells: P / R / F1.', '',
                  '| Case / version | '+' | '.join(METRICS)+' |', '|---|'+'---|'*len(METRICS)]
        for case in (c for c in CASES if c.endswith(stage)):
            before, after = index.get(('baseline',case)), index.get(('prompt_improvement_variant',case))
            for label, row in [('baseline',before),('variant',after)]:
                values = [' / '.join(f'{100*row["tuple"][m][s]:.4f}' for s in SCORES) if row else 'pending' for m in METRICS]
                lines.append(f'| {case} / {label} | '+' | '.join(values)+' |')
            if before and after:
                values = [' / '.join(f'{100*(after["tuple"][m][s]-before["tuple"][m][s]):+.4f}' for s in SCORES) for m in METRICS]
                lines.append(f'| {case} / delta | '+' | '.join(values)+' |')
        lines += ['', '| Case / version | LR | finite nonempty | PC | RC | RBO | AO |', '|---|'+'---|'*6]
        for case in (c for c in CASES if c.endswith(stage)):
            before, after = index.get(('baseline',case)), index.get(('prompt_improvement_variant',case))
            for label, row in [('baseline',before),('variant',after)]:
                lines.append(f'| {case} / {label} | '+' | '.join(f'{100*row["leaderboard"][k]:.4f}' if row else 'pending' for k in LB_KEYS)+' |')
            if before and after:
                lines.append(f'| {case} / delta | '+' | '.join(f'{100*(after["leaderboard"][k]-before["leaderboard"][k]):+.4f}' for k in LB_KEYS)+' |')
        lines += ['', f'### {stage} three-Cold mean / sample SD', '',
                  'Exactly cold_default, cold_0 and cold_42. SD uses ddof=1; delta SD is computed from the three paired differences. These orders are not independent model replicates.', '',
                  '| Metric | Baseline mean / SD | Variant mean / SD | Paired delta mean / SD |', '|---|---|---|---|']
        stats = {x['model']:x['metrics'] for x in report['cold_three_order_summaries'] if x['stage']==stage}
        for key in [f'{m}/{s}' for m in METRICS for s in SCORES]+list(LB_KEYS):
            values = []
            for model in ('baseline','prompt_improvement_variant','paired_delta'):
                v = stats[model]
                values.append(f'{100*v[key]["mean"]:.4f} / {100*v[key]["sample_sd"]:.4f}' if v else 'pending (requires all three)')
            lines.append('| '+key+' | '+' | '.join(values)+' |')
        lines += ['']
    lines += ['## Per-paper changes and pending work', '',
              'per_paper_differences.csv/JSON contains all six tuple metrics, all P/R/F1 and both stages for each of the 43 papers. comparison.csv and cold_statistics.csv retain full precision.', '']
    lines += [f'- {x["model"]} / {x["case"]}: {x["status"]}; {x.get("reason", "")}' for x in report['missing']] or ['All eight paired stages verified.']
    lines += ['', report['cross_model_note'], '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evaluations',type=Path,default=ANALYSIS/'evaluations')
    p.add_argument('--out',type=Path,default=ANALYSIS/'comparisons'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'), help='New or empty directory strictly below analysis')
    args=p.parse_args()
    boundary()
    try:
        out=fresh_directory(args.out)
        report,evidence=compare(args.evaluations)
        paper=list(per_paper_rows(report))
        fields=['case','role','paper_id','metric','status']+[f'{prefix}_{s}' for prefix in ('baseline','variant','delta') for s in SCORES]
        write_csv(out/'per_paper_differences.csv',paper,fields)
        index={(r['model'],r['case']):r for r in report['local_rows']}
        scalar_rows=[]
        for case in CASES:
            b,v=index.get(('baseline',case)),index.get(('prompt_improvement_variant',case))
            bf,vf=flatten(b) if b else {},flatten(v) if v else {}
            for k in dict.fromkeys([*bf,*vf]):
                scalar_rows.append({'case':case,'role':'primary' if case.endswith('stage2') else 'diagnostic','metric':k,
                                    'baseline':bf.get(k),'variant':vf.get(k),'delta':vf[k]-bf[k] if k in bf and k in vf else None,
                                    'unit':'fraction; multiply by 100 for percent/percentage points'})
        write_csv(out/'comparison.csv',scalar_rows,['case','role','metric','baseline','variant','delta','unit'])
        cold_rows=[]
        metric_names=[f'{m}/{s}' for m in METRICS for s in SCORES]+list(LB_KEYS)
        for item in report['cold_three_order_summaries']:
            for key in metric_names:
                stats=item['metrics'][key] if item['metrics'] else {'mean':None,'sample_sd':None,'n':len(item['orders_present'])}
                cold_rows.append({'model':item['model'],'stage':item['stage'],'status':item['status'],'metric':key,**stats})
        write_csv(out/'cold_statistics.csv',cold_rows,['model','stage','status','metric','mean','sample_sd','n'])
        save(out/'per_paper_differences.json',paper)
        (out/'report.md').write_text(render(report),encoding='utf-8')
        report['source_integrity']=verify(evidence.hashes)
        save(out/'source_hashes.json',evidence.hashes)
        save(out/'comparison.json',report)
        save(out/'report_status.json',{'status':report['status'],'files':{str(p.relative_to(out)):sha(p) for p in out.iterdir() if p.is_file()}})
        print(json.dumps({'status':report['status'],'verified_local_rows':len(report['local_rows']), 'paired_cases':len(report['paired_differences']), 'missing':len(report['missing']), 'out':str(out)},ensure_ascii=False))
        return {'COMPLETE':0,'INCOMPLETE':2,'ERROR':1}[report['status']]
    except Exception as error:
        print(json.dumps({'status':'ERROR','error':str(error)},ensure_ascii=False))
        return 1


if __name__=='__main__':
    sys.exit(main())
