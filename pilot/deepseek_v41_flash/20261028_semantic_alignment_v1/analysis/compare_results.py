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
                                 load_evaluation, verified_evaluation)


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
                stage = ready_stage(root, case, evidence)
                if stage['status'] != 'READY':
                    missing.append({'model':model, 'case':case, **stage})
                    continue
                dest = BASELINE/'analysis/evaluations'/case if model=='baseline' else evaluations/case
                if not (dest/'status.json').is_file():
                    missing.append({'model':model,'case':case,'status':'PENDING','reason':'Evaluation not present','path':str(dest)})
                    continue
                load = load_evaluation if model=='baseline' else verified_evaluation
                row = load(dest, stage['normalized'], evidence)
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
    prior_path = BASELINE/'analysis/comparison_final/comparison.json'
    prior = evidence.read(prior_path)
    references = {'source':str(prior_path), 'source_sha256':sha(prior_path),
                  'status':'Immutable prior-source reference; not rerun by these utilities.',
                  'local_rows':[r for r in prior['local_rows'] if r['model'] in ('Sol','GPT-4.1')],
                  'original_paper':prior['original_paper'], 'provenance':prior['provenance']}
    report = {'status':'ERROR' if any(x['status']=='ERROR' for x in missing) else 'INCOMPLETE' if missing else 'COMPLETE',
              'created_utc':datetime.now(timezone.utc).isoformat(), 'new_api_requests':0,
              'scope':{'papers':43,'predictions':295,'gold_annotations':295,'gold_boards':27,'primary_stage':'stage2','diagnostic_stage':'stage1'},
              'method':{'label':'Authorized semantic-alignment prompt-improvement variant; not the original baseline',
                        'declared_change':'Generic semantic matching additions only in masked-normalization and leaderboard-normalization system Prompts.',
                        'prompt_source_user_reported':str(EXPERIMENT/'prompts_semantic_v1.json'),
                        'unchanged_user_reported':['default MetricPrompt','exact candidate acceptance rules'],
                        'cold_observer_user_reported':'Copied prefix; only Prompt assertion binding changed.',
                        'method_statement_source':'User/main handoff; runtime/Prompt integrity audit is outside this utility.',
                        'raw_extraction':str(BASELINE/'fully/merged/output.json'),
                        'raw_sha256':sha(BASELINE/'fully/merged/output.json'),
                        'evaluation':'Unchanged official tdm_eval and leaderboard_eval via byte-identical prior audited evaluator/helpers.',
                        'tuple_f1':'Harmonic mean of official macro P/R; never mean of per-paper F1.',
                        'LR':'Exact normalized TDM hit before numeric conversion.',
                        'finite_nonempty':'At least one finite converted Result for a Gold board.',
                        'RBO':'Official deduplicated numeric-value rankings; not paper IDs.',
                        'AO':'Paper-ID rankings, deterministic paper-ID tie-break, empty boards=0; macro over all27.',
                        'global_audit':'Main task owns global usage/integrity, Prompt and runtime verification, and qualitative examples.'},
              'local_rows':rows,'paired_differences':differences,'cold_three_order_summaries':cold,
              'missing':missing,'immutable_prior_references':references}
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
    index = {(r['model'],r['case']):r for r in report['local_rows']}
    lines = ['# DeepSeek 语义对齐 Prompt 改进变体：离线比较', '',
             f"状态：**{report['status']}**；生成时间：{report['created_utc']}。",
             '比较对象：已授权的 Prompt 改进变体 semantic_alignment_v1 与原始基线 20261028。完成状态根据各阶段 summary、输出 SHA-256 和离线评估文件确定。', '',
             '方法变更（主任务提供）：仅 masked-normalization、leaderboard-normalization 的 system Prompt 增加通用语义匹配规则；默认 MetricPrompt、候选项精确接受规则不变。Cold observer 沿用复制前缀，仅调整 Prompt 断言绑定。具体 Prompt/运行完整性、API 用量及来源案例由主任务单独审计。', '',
             'Extraction 完全复用基线；每个可比较结果均为 43 篇论文、295 条预测、295 条 Gold、全部 27 个榜单。stage2 为主要结果，stage1 仅作诊断。', '',
             '## Stage2 元组指标', '',
             '数值为百分比，单元格为 P / R / F1。F1 由官方逐论文宏平均 P/R 求调和平均，不是论文 F1 的平均。', '',
             '| Case / 版本 | '+' | '.join(METRICS)+' |', '|---|'+'---|'*len(METRICS)]
    triple = lambda m:' / '.join(f'{100*m[s]:.2f}' for s in SCORES)
    for case in (c for c in CASES if c.endswith('stage2')):
        for model,label in [('baseline','原始基线'),('prompt_improvement_variant','Prompt 改进变体')]:
            r=index.get((model,case))
            lines.append(f'| {case} / {label} | '+' | '.join(triple(r['tuple'][m]) if r else '待完成' for m in METRICS)+' |')
        a,b=index.get(('prompt_improvement_variant',case)),index.get(('baseline',case))
        if a and b:
            lines.append(f'| {case} / Δ百分点 | '+' | '.join(triple(scalar_differences(a['tuple'][m],b['tuple'][m])) for m in METRICS)+' |')
    lines += ['', '## Stage2 榜单指标', '',
              'LR 为精确 TDM 命中率；finite nonempty 额外要求可转换的有限数值。PC/RC 保持官方定义；RBO 排列去重数值，AO 排列论文 ID。空榜单保留在 27 个榜单分母内。', '',
              '| Case / 版本 | LR | finite nonempty | PC | RC | RBO 数值 | AO 论文ID |','|---|---|---|---|---|---|---|']
    for case in (c for c in CASES if c.endswith('stage2')):
        for model,label in [('baseline','原始基线'),('prompt_improvement_variant','Prompt 改进变体')]:
            r=index.get((model,case))
            lines.append(f'| {case} / {label} | '+' | '.join(f'{100*r["leaderboard"][k]:.2f}' if r else '待完成' for k in LB_KEYS)+' |')
        a,b=index.get(('prompt_improvement_variant',case)),index.get(('baseline',case))
        if a and b:
            lines.append(f'| {case} / Δ百分点 | '+' | '.join(f'{100*(a["leaderboard"][k]-b["leaderboard"][k]):+.2f}' for k in LB_KEYS)+' |')
    lines += ['', '## Cold 三顺序', '', '仅三个顺序全部完成时计算均值与样本标准差（ddof=1）。下表为 stage2 榜单；两个阶段所有元组 P/R/F1、榜单指标和配对差值的 mean/sampleSD 见 JSON。', '',
              '| 版本 | LR | finite nonempty | PC | RC | RBO | AO |','|---|---|---|---|---|---|---|']
    for item in report['cold_three_order_summaries']:
        if item['stage']!='stage2': continue
        values=item['metrics']
        lines.append(f'| {item["model"]} | '+' | '.join(f'{100*values[k]["mean"]:.2f} ± {100*values[k]["sample_sd"]:.2f}' if values else '待三个顺序完成' for k in LB_KEYS)+' |')
    lines += ['', '## 逐论文改善与退化', '',
              '| Case | 指标 F1 | 改善 | 退化 | 不变 |', '|---|---|---|---|---|']
    for item in report['stage2_paper_changes']:
        lines.append(f'| {item["case"]} | {item["metric"]} | {item["improved"]} | {item["regressed"]} | {item["unchanged"]} |')
    if not report['stage2_paper_changes']:
        lines += ['', '尚无完成验证的 stage2 配对结果。']
    lines += ['', '## 待完成项', '']
    lines += [f'- {x["model"]} / {x["case"]}: {x["status"]}；{x.get("reason", "")}' for x in report['missing']] or ['全部八个阶段均有可验证评估结果。']
    lines += ['', '逐论文差异见 per_paper_differences.csv；Δ=变体−基线，缺失值留空，不能解释为零。comparison.csv 包含两个阶段全部指标；comparison.json 保留全精度结果及路径。',
              'Sol / GPT-4.1 及论文已发表数值保存在 comparison.json 的 immutable_prior_references 中，来自基线 comparison_final/comparison.json，保留其原有范围、定义与 SHA-256。', '']
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
        save(out/'per_paper_differences.json',paper)
        (out/'report_zh.md').write_text(render(report),encoding='utf-8')
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
