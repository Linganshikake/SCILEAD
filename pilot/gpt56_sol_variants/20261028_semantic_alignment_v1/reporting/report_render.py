"""Chinese report from audited artifacts and an existing paired comparison."""
import json
from pathlib import Path

from audit_and_report import BRANCHES, METRICS, PRF, LB, SCALARS, read, sha

LABELS = {'partially': 'Partially', 'cold_default': 'Cold 默认顺序', 'cold_0': 'Cold 字符串种子 0', 'cold_42': 'Cold 字符串种子 42'}
LB_LABELS = ('LR 精确TDM命中', '有限非空榜率', 'PC', 'RC', 'RBO 数值排名', 'AO 论文ID排名')


def cell(value):
    return str(value).replace('|', '\\|').replace('\r', '').replace('\n', '<br>')


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(map(cell, headers)) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def pct(value):
    return f'{100 * value:.4f}'


def delta(value):
    return f'{100 * value:+.4f}'


def brief(record):
    return json.dumps(record, ensure_ascii=False)


def response_proof(directory, call):
    if call is None:
        return None
    folder = directory / 'api_calls' / f'{call:04d}'
    acc = read(folder / 'accepted.json')
    path = folder / acc.get('response_relative_path', 'response.json')
    if not path.resolve().is_relative_to(folder.resolve()) or sha(path) != acc['response_sha256']:
        raise ValueError('baseline example accepted response hash/path mismatch')
    return {'path': str(path), 'sha256': sha(path), 'content': read(path)['choices'][0]['message']['content']}


def select_examples(comparison, events, gold, baseline):
    selected, seen = [], set()
    # Include a genuine paired-paper regression first if one is present, then improvements.
    for direction in ('regression', 'improvement', 'other'):
        for metric in ('TDMR Exact Match', 'TDM Exact Match'):
            for row in comparison['stage2_paper_changes']:
                if row['metric'] != metric:
                    continue
                case = row['case']
                branch = case.removesuffix('_stage2')
                papers = row['top_regressions'] if direction == 'regression' else row['top_improvements'] if direction == 'improvement' else []
                candidates = [(p, change) for p in papers for change in events[case]['changes'] if change['paper'] == p['paper_id']]
                if direction == 'other':
                    candidates = [(None, change) for change in events[case]['changes']]
                for paper_score, change in candidates:
                    identity = (change['paper'], change['record'])
                    if identity in seen:
                        continue
                    seen.add(identity)
                    ex = dict(change, branch=branch, stage='stage2', direction=direction, metric=metric, paired_paper_score=paper_score)
                    ex['baseline_accepted_response'] = response_proof(baseline / branch / 'stage2', change['baseline_call'])
                    ex['gold_tdmrs_offline_only'] = gold[change['paper']]['TDMs']
                    gold_tdm = {tuple(g[k] for k in ('Task', 'Dataset', 'Metric')) for g in gold[change['paper']]['TDMs']}
                    ex['before_exact_gold_tdm'] = tuple(change['before'][k] for k in ('Task', 'Dataset', 'Metric')) in gold_tdm
                    ex['after_exact_gold_tdm'] = tuple(change['after'][k] for k in ('Task', 'Dataset', 'Metric')) in gold_tdm
                    ex['interpretation'] = 'Observed label/tuple change; exact Gold name matching is evidence about alignment, not proof of semantic equivalence. Paper-score association does not isolate this record as the cause.'
                    selected.append(ex)
                    # At most one regression example; remaining slots show other observed changes.
                    break
                if len(selected) >= 3:
                    return selected
                if direction == 'regression' and selected:
                    break
            if direction == 'regression' and selected:
                break
    return selected


def render(verification, usage, comparison, events, gold, root, baseline):
    status = verification['report_status']
    lines = ['# GPT-5.6 Sol：语义对齐 Prompt 补充实验', '',
             f'报告状态：**{status}**；审计状态：**{verification["status"]}**；比较状态：**{verification["comparison_status"]}**。', '',
             f'生成时间 UTC：{verification["checked_utc"]}；Asia/Shanghai：{verification["checked_shanghai"]}。目录名称是实验标识，不代表全部执行日期。', '',
             '固定范围：43 篇论文、335 条既有 Extraction 预测、295 条 Gold、27 个 Gold 排行榜。主要比较为 Sol 原版与本轮 Sol Prompt 补充版的第二阶段；第一阶段仅用于诊断。', '',
             '配置：`gpt-5.6-sol`、`reasoning_effort=medium`、`max_completion_tokens=32768`、`stream=false`。本轮仅追加 masked-normalization 和 leaderboard-normalization 两处 system Prompt；Partially 的 Metric 原 Prompt 保留。', '',
             f'Prompt 文件 SHA-256：`{verification["prompt_sha256"]}`。与 DeepSeek 补充版逐字节一致；预测输入使用 Sol 自己的冻结 Extraction，核验记录见 verification.json。', '']
    if comparison is None:
        lines += ['**尚不能给出本轮最终改善结论。** 未完成阶段或缺失比较结果不会补零，也不会标记为全部完成。正式指标和 2–3 条实际事件案例将在全部审计及 comparison 通过后生成。', '']
    else:
        index = {(r['model'], r['case']): r for r in comparison['local_rows']}
        cold = {(r['model'], r['stage']): r['metrics'] for r in comparison['cold_three_order_summaries']}
        lines += ['## 第二阶段主要结论', '']
        summary_rows = []
        for branch in BRANCHES:
            old, new = index['baseline', branch + '_stage2'], index['prompt_improvement_variant', branch + '_stage2']
            before, after = old['tuple']['TDMR Exact Match']['F1'], new['tuple']['TDMR Exact Match']['F1']
            direction = '提高' if after > before else '下降' if after < before else '不变'
            summary_rows.append([LABELS[branch], pct(before), pct(after), delta(after - before), direction])
        lines += [table(['设置', '原版 TDMR F1/%', '补充后 TDMR F1/%', '变化/百分点', '配对结果'], summary_rows), '',
                  'Cold 三顺序的第二阶段 TDMR F1：' + pct(cold['baseline', 'stage2']['TDMR Exact Match/F1']['mean']) + '% → ' + pct(cold['prompt_improvement_variant', 'stage2']['TDMR Exact Match/F1']['mean']) + '%；平均配对变化 ' + delta(cold['paired_delta', 'stage2']['TDMR Exact Match/F1']['mean']) + ' 个百分点。', '',
                  '两阶段 Prompt 同时补充，第一阶段的回答也改变了动态候选集。因此，本次比较衡量整套补充规则及其候选集演变的联合效果。', '']
        for stage, label in [('stage2', '第二阶段：主要结果'), ('stage1', '第一阶段：诊断结果')]:
            lines += ['## ' + label, '', '数值为百分数；Tuple P/R 是官方逐篇 Macro，F1 是该 Macro P/R 的调和平均，并非逐篇 F1 的平均。', '']
            for branch in BRANCHES:
                old, new = index['baseline', branch + '_' + stage], index['prompt_improvement_variant', branch + '_' + stage]
                rows = [[m] + [pct(old['tuple'][m][k]) for k in PRF] + [pct(new['tuple'][m][k]) for k in PRF] + [delta(new['tuple'][m]['F1'] - old['tuple'][m]['F1'])] for m in METRICS]
                lines += ['### ' + LABELS[branch], '', table(['指标', '原P', '原R', '原F1', '新P', '新R', '新F1', 'F1变化/百分点'], rows), '']
            lb_rows = []
            for branch in BRANCHES:
                for model, version in [('baseline', '原版'), ('prompt_improvement_variant', '补充后')]:
                    lb_rows.append([LABELS[branch], version] + [pct(index[model, branch + '_' + stage]['leaderboard'][key]) for key in LB])
            lines += ['### 全部排行榜指标', '', table(['设置', '版本', *LB_LABELS], lb_rows), '',
                      'LR 为数值转换前的精确 TDM 命中；有限非空榜率单列。PC/RC 和数值排名 RBO 沿用官方方法；AO 按论文 ID 排名。27 榜全部进入分母，包括空榜。', '',
                      '### Cold 三顺序：所有指标的均值与样本标准差', '']
            rows = []
            for key in SCALARS:
                values = [cold[m, stage][key] for m in ('baseline', 'prompt_improvement_variant', 'paired_delta')]
                rows.append([key] + [f'{pct(v["mean"])} ± {pct(v["sample_sd"])}' for v in values])
            lines += [table(['指标', '原版均值 ± SD/%', '补充后均值 ± SD/%', '配对差均值 ± SD/百分点'], rows), '',
                      'SD 为三个固定论文顺序之间的样本标准差（ddof=1）；配对差 SD 从三条配对差计算。', '']
        lines += ['## 逐篇变化与实际对齐案例', '', table(['设置', '指标', '提高篇数', '回退篇数', '不变篇数'], [[LABELS[r['case'].removesuffix('_stage2')], r['metric'], r['improved'], r['regressed'], r['unchanged']] for r in comparison['stage2_paper_changes']]), '']
        examples = select_examples(comparison, events, gold, baseline)
        for number, ex in enumerate(examples, 1):
            score = ex['paired_paper_score']
            label = '回退关联案例' if ex['direction'] == 'regression' else '改善关联案例' if ex['direction'] == 'improvement' else '其他实际变化'
            lines += [f'### 案例 {number}：{label} · {LABELS[ex["branch"]]} · {ex["paper"]} 第 {ex["record"]} 条', '',
                      table(['证据', '内容'], [['原始 Extraction', brief(ex['raw_extraction'])], ['原版第二阶段', brief(ex['before'])], ['补充后第二阶段', brief(ex['after'])], ['处理分支', ex['before_branch'] + ' → ' + ex['after_branch']], ['精确命中该篇 Gold TDM', str(ex['before_exact_gold_tdm']) + ' → ' + str(ex['after_exact_gold_tdm'])]]), '']
            if score:
                lines += [f'该篇整体 {ex["metric"]} F1：{pct(score["baseline_F1"])}% → {pct(score["variant_F1"])}%（{delta(score["delta_F1"])} 个百分点）；上表展示其中一条发生变化的记录。', '']
            lines += [f'事件证据：`{ex["baseline_event"]["path"]}`（SHA-256 `{ex["baseline_event"]["sha256"]}`）；`{ex["variant_event"]["path"]}`（SHA-256 `{ex["variant_event"]["sha256"]}`）。原始回答路径、accepted 引用及 Gold 对照保存于 [alignment_examples.json](alignment_examples.json)。', '']
        if not any(r['regressed'] for r in comparison['stage2_paper_changes']):
            lines += ['本轮第二阶段逐篇 TDM/TDMR F1 配对表中未观察到回退；这不表示所有标签的实体身份均已人工验证。', '']
        result_f1 = index['baseline', 'partially_stage2']['tuple']['Result IIM']['F1']
        lines += [f'335 条原始记录的 Result、source_documents 和记录顺序通过核验；Result IIM F1 在配对结果中保持 {pct(result_f1)}%。没有重新生成 Extraction，也没有人工改写预测。', '']
    if comparison is None:
        examples = []
    lines += ['## 请求用量与完整性', '',
              table(['分支', '逻辑请求', '已接受逻辑请求', '尝试记录', '客户端post调用', '缺失发送状态记录', '用量未知', '已知总Tokens'], [[LABELS[b], x['logical_normalization_requests'], x['logical_accepted'], x['attempt_records'], x['known_post_calls'], x['unknown_send_attempts'], x['unknown_usage_attempts'], x['totals']['total_tokens']] for b, x in usage['branches'].items()]), '',
              f'额外重试记录 {usage["retry_attempt_records"]}；授权重试 {usage["authorized_additional_attempts"]}；自动重试 {usage["automatic_retries"] if usage["automatic_retries"] is not None else "尚不能确定"}。未知用量保留为未知；已知 Token 合计不包含失败/未知尝试可能产生的服务端费用。只累计 top-level usage，不重复累计 billing_usage。', '',
              f'物理 HTTP200 尝试 {usage["physical_http200_attempts"]}；实际模型 stop 有效响应 {usage["physical_valid_model_stop_responses"]}；已接受逻辑请求 {usage["logical_accepted"]}。三个计数独立核验，不使用 runtime api_usage.json 的成功计数，也不要求 retry 子目录有 accepted.json。', '',
              f'核验保护清单 {verification["protected_file_count"]} 项；与清单不符 {len(verification["protected_changes"])} 项；审计期间变化 {len(verification["protected_changes_during_audit"])} 项。', '',
              table(['阶段', '审计状态', '当前观察状态', 'summary状态', '已接受/逻辑请求', '尝试记录'], [[case, v['status'], v['observed_runtime_status'], v['summary_status'], f'{v["logical_accepted"]}/{v["logical_requests"]}', v['physical_attempt_records']] for case, v in verification['stage_checks'].items()]), '']
    if usage.get('first_request_utc'):
        lines += [f'日志时间窗口：首个请求 {usage["first_request_utc"]}；最后观察到的请求结束时间 {usage["last_observed_attempt_end_utc"]}。窗口包含接口等待及人工授权暂停时间。', '']
    if verification['issues'] or verification['comparison_issues']:
        lines += ['## 待处理项', '']
        lines.extend('- ' + cell(x['check']) + '：`' + x['path'] + '`' for x in verification['issues'])
        lines.extend('- ' + cell(x) for x in verification['comparison_issues'])
        lines.append('')
    lines += ['## 产物索引', '', '- [index.md](index.md)：全部审计产物。', '- [verification.json](verification.json)：状态、问题、83 项保护哈希前后核验及比较来源。', '- [request_audit.csv](request_audit.csv)：成功、失败及恢复尝试的逐条记录。', '- [alignment_event_summary.json](alignment_event_summary.json)：各阶段事件计数和实际变化。',
              f'- 配对指标来源：`{verification["comparison_path"]}`；SHA-256：`{verification["comparison_sha256"]}`。', '',
              '本工具只读已有实验与分析产物；仅写 reporting，不运行评测、API 或模型。重新调用会刷新当前快照；仅当八阶段审计及完整配对分析均通过时标为 COMPLETE。', '']
    return '\n'.join(lines), examples
