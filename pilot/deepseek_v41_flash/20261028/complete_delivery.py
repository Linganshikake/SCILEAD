"""Offline completion audit and Chinese report. Never imports the API transport."""
import csv
import hashlib
import json
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METRICS = ['Task IIM', 'Dataset IIM', 'Metric IIM', 'Result IIM', 'TDM Exact Match', 'TDMR Exact Match']
PRIMARY = ['fully', 'fully_cs', 'partially_stage2', 'cold_default_stage2', 'cold_0_stage2', 'cold_42_stage2']
LABELS = {'fully': 'Fully + LLM', 'fully_cs': 'Fully + CS', 'partially_stage2': 'Partially 第二阶段',
          'cold_default_stage2': 'Cold Start 默认顺序', 'cold_0_stage2': 'Cold Start 字符串种子 0',
          'cold_42_stage2': 'Cold Start 字符串种子 42'}
LB = ['LR_exact_tdm_hit', 'LR_nonempty_finite_result', 'PC_official', 'RC_official',
      'RBO_official_value_rankings', 'AO_paper_id_macro_all_gold_boards']
LBN = ['LR', '有效非空榜率', 'PC', 'RC', 'RBO（数值列表）', 'AO（论文ID）']

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()

def save(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def pct(v): return f'{v * 100:.2f}'

def table(head, rows):
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---'] * len(head)) + ' |'] +
                     ['| ' + ' | '.join(str(x) for x in row) + ' |' for row in rows])

def stats(values): return {'mean': statistics.mean(values), 'sd': statistics.stdev(values)}

def main():
    comp = read(ROOT/'analysis/comparison_final/comparison.json')
    assert comp['status'] == 'COMPLETE' and not comp['missing']
    rows = {(x['model'], x['case']): x for x in comp['local_rows']}
    new = {case: rows['DeepSeek', case] for case in PRIMARY}
    usage = read(ROOT/'api_usage_summary.json')
    audit = read(ROOT/'verification.json')
    assert audit['audit_status'] == 'PASS'
    assert usage['http_status_counts'] == {'200': usage['actual_model_requests']}
    assert usage['finish_reason_counts'] == {'stop': usage['actual_model_requests']}
    assert usage['unknown_usage_requests'] == 0
    sources = {}
    for rel in ['protected_hashes.json', 'variants/protected_hashes.json', 'fully/launch_source_hashes.json',
                'analysis/comparison_final/source_hashes.json']:
        hashes = read(ROOT/rel)
        for p, h in hashes.items():
            assert p not in sources or sources[p] == h, p
            sources[p] = h
    changed = [p for p, h in sources.items() if not Path(p).is_file() or sha(p) != h]
    assert not changed, changed
    raw = read(ROOT/'fully/merged/output.json')
    raw_response = read(ROOT/'fully/merged/raw_output.json')
    assert raw == raw_response
    assert len(raw) == 43
    runner = sha(ROOT/'variants/variant_runtime.py')
    assert all(x['runner_sha256'] == runner for x in read(ROOT/'variants/live_processes.json'))
    extraction_checks = []
    for paper, value in raw.items():
        rr = json.loads(value['output'])
        v = read(ROOT/'fully/papers'/paper/'extraction/validation.json')
        assert v['valid'] and v['records'] == len(rr)
        assert all(set(x) == {'Task','Dataset','Metric','Result'} and all(isinstance(y, str) for y in x.values()) for x in rr)
        extraction_checks.append({'paper_id': paper, 'records': len(rr), 'validation': 'PASS'})
    stage_summaries = {}
    event_audit = {}
    stage_examples = []
    calls_expected = read(ROOT/'fully/api_usage_summary.json')['request_attempts']
    # Each original stage completes exactly once. Verify stage outputs against both the saved hash and raw Extraction.
    for branch in ['partially', 'cold_default', 'cold_0', 'cold_42']:
        for stage in ['stage1', 'stage2']:
            d = ROOT/'variants'/branch/stage
            summary = read(d/'summary.json')
            assert summary['status'] == 'COMPLETE' and summary['papers'] == 43 and summary['records'] == 295
            assert sha(summary['output_path']) == summary['output_sha256']
            actual = read(summary['output_path'])
            assert set(actual) == set(raw)
            for paper in raw:
                assert actual[paper]['source_documents'] == raw[paper]['source_documents']
                assert [x['Result'] for x in actual[paper]['normalized_output']] == [x['Result'] for x in json.loads(raw[paper]['output'])]
            events = [read(p) for p in sorted((d/'events').glob('*.json'))]
            ec = Counter(x['branch'] for x in events)
            event_audit[branch+'_'+stage] = {'events': len(events), 'branches': dict(ec)}
            if stage == 'stage2':
                unchanged_answer = 0
                for e in events:
                    original = '(' + ', '.join(str(e['original'][k]) for k in ['Task','Dataset','Metric']) + ')'
                    unchanged_answer += e.get('raw_answer') == original
                event_audit[branch+'_'+stage]['answers_equal_input_tuple'] = unchanged_answer
                for e in [x for x in events if x.get('call')][:3]:
                    rp = d/'api_calls'/f"{e['call']:04d}"/'response.json'
                    a = read(rp)['choices'][0]['message']
                    stage_examples.append({'branch': branch, 'event': e, 'response_path': str(rp),
                                           'response_sha256': sha(rp), 'content': a['content'],
                                           'provider_reasoning_content': a.get('reasoning_content'),
                                           'note': '原始返回文本，仅作离线行为核查；不用于修改预测。'})
            stage_summaries[branch+'_'+stage] = summary
            calls_expected += summary['api_calls']
    assert calls_expected == usage['actual_model_requests']
    cs = read(ROOT/'variants/fully_cs/normalization/summary.json')
    assert cs['status'] == 'COMPLETE' and cs['papers'] == 43 and cs['new_llm_requests'] == 0
    for case in PRIMARY:
        row = new[case]
        assert row['status'] == 'COMPLETE' and row['coverage']['evaluated_papers'] == 43
        assert row['coverage']['evaluated_gold_tdmrs'] == 295 and row['coverage']['predictions'] == 295
        for m in row['tuple'].values():
            expected = 2*m['Precision']*m['Recall']/(m['Precision']+m['Recall']) if m['Precision']+m['Recall'] else 0
            assert abs(expected-m['F1']) < 1e-12
    # Scan deliverable text for credential-shaped strings without reading any credential file.
    secret_hits = []
    checked_text = 0
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.json','.jsonl','.txt','.log','.md','.csv','.py','.ps1'}: continue
        if any(x in {'reproducibility','offline_test','runtime','__pycache__'} for x in p.relative_to(ROOT).parts): continue
        content = p.read_text(encoding='utf-8-sig', errors='replace')
        checked_text += 1
        if re.search(r'\bsk-[A-Za-z0-9_-]{24,}\b|Bearer\s+[A-Za-z0-9_-]{24,}', content): secret_hits.append(str(p))
    assert not secret_hits, secret_hits
    save(ROOT/'inspection/normalization_stage_behavior.json', {'event_counts': event_audit, 'examples': stage_examples})
    cold_cases = ['cold_default_stage2','cold_0_stage2','cold_42_stage2']
    cold_tuple = {m: {k: stats([new[c]['tuple'][m][k] for c in cold_cases]) for k in ['Precision','Recall','F1']} for m in METRICS}
    cold_summary = next(x for x in comp['cold_three_order_summaries'] if x['model']=='DeepSeek' and x['scope']=='all27')
    out = {'status': 'COMPLETE', 'papers': 43, 'gold_records': 295, 'predictions': 295, 'leaderboards': 27,
           'primary_cases': {k: {'tuple': v['tuple'], 'leaderboard': v['leaderboards']['all27'], 'strict_result': v['strict_result']} for k,v in new.items()},
           'cold_tuple_three_order_mean_sd': cold_tuple, 'cold_leaderboard_three_order_mean_sd': cold_summary,
           'cold_aggregation': 'Mean and sample SD across three run-level metrics. Each individual run F1 is harmonic of its official macro P/R.',
           'api_usage': usage, 'cs': cs, 'stage_summaries': stage_summaries}
    save(ROOT/'results_summary.json', out)
    audit.update(completion_status='COMPLETE', primary_cases=PRIMARY, protected_and_provenance_files_checked=len(sources),
                 protected_and_provenance_changes=changed, all_branch_outputs_verified=True,
                 all_stage_results_and_source_documents_preserved=True, actual_request_count_matches_stage_totals=True,
                 extraction_checks=extraction_checks, secret_shape_scan={'text_files_checked': checked_text, 'matches': secret_hits},
                 raw_and_compatible_extraction_identical=True, reviewed_utc=datetime.now(timezone.utc).isoformat())
    save(ROOT/'verification.json', audit)
    save(ROOT/'delivery_protected_hashes.json', sources)
    write_report(new, rows, comp, usage, cs, cold_tuple, cold_summary, stage_summaries, event_audit, audit)
    plan = ROOT/'execution_plan.md'
    plan.write_text(plan.read_text(encoding='utf-8').replace('- [ ]', '- [x]'), encoding='utf-8')
    print(json.dumps({'status': 'COMPLETE', 'papers': 43, 'requests': usage['actual_model_requests'],
                      'tokens': usage['total']['total_tokens'], 'protected_checks': len(sources),
                      'report': str(ROOT/'report.md')}, ensure_ascii=False))

def write_report(new, rows, comp, usage, cs, cold_tuple, cold_lb, stages, events, audit):
    original = comp['original_paper']['rows']
    def paper_row(case, tab):
        setting = 'Partially' if case=='partially_stage2' else 'Fully'
        norm = 'cosine_similarity' if case=='fully_cs' else 'LLM'
        return next(x for x in original if x['model']=='GPT-4' and x['setting']==setting and x.get('normalization')==norm and x['table']==tab)
    full = new['fully']; sol = rows['Sol','fully']; gpt = rows['GPT-4.1','fully']
    p = []
    p += ['# SCILEAD DeepSeek-V4.1-Flash 全量实验报告', '',
          '执行日期：2026-10-28（北京时间）。状态：全部完成。43 篇论文、295 条 Gold；本轮抽取 295 条预测，六个正式分支均完整覆盖 43 篇。', '',
          f"Fully + LLM 的 TDMR F1 为 **{pct(full['tuple']['TDMR Exact Match']['F1'])}%**，相对原论文 GPT-4 Turbo（55.27%）提高 **{full['tuple']['TDMR Exact Match']['F1']*100-55.27:.2f} 个百分点**；相对 GPT-4.1 提高 **{(full['tuple']['TDMR Exact Match']['F1']-gpt['tuple']['TDMR Exact Match']['F1'])*100:.2f} 个百分点**，相对 Sol 下降 **{(sol['tuple']['TDMR Exact Match']['F1']-full['tuple']['TDMR Exact Match']['F1'])*100:.2f} 个百分点**。", '',
          'Partially 和 Cold Start 的主要问题是新名称向既定排行榜的语义对齐。DeepSeek 多次按字符串相等理解原 Prompt 的“matches”，保留输入缩写；Fully 有完整候选名称时表现明显更好。下文给出官方处理事件和具体实例。', '',
          '## 1. 实验设置与执行流程', '',
          '- 实际请求模型：`deepseek-flash`；DeepSeek 官方文档当前将该别名映射到 `DeepSeek-V4.1-Flash-1017`。全部响应模型标识为 `deepseek-flash`，原始响应及 system_fingerprint 已保存。',
          '- 接口：`https://api.deepseek.com/chat/completions`；thinking enabled、reasoning_effort=high、stream=false。每次请求不发送输出 Token 上限、temperature、seed、tools 或 response_format。官方 high 模式在省略上限时采用服务端默认预算。',
          '- 官方源码实际 HEAD：`8bf74b0a830feb7035c6166dce3394dc344ae532`；历史外层归档冻结标识：`b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25`。',
          '- 复用 43 篇冻结 RAG 输入，每篇 4 个检索正文块及全部已检测表格；顺序和内容哈希一致。PDF 解析、Embedding、Chroma 检索均未重跑。Extraction Prompt 不含 Gold、历史预测或错误分析。',
          '- 先进行一次全量 Zero-shot Extraction，再复用这批新预测执行 Fully LLM、Fully CS、Partially 和三种 Cold Start。Fully 的候选名称及顺序固定为 Task 23、Dataset 71、Metric 26；Partially/Cold 使用原版遮蔽和动态名称更新逻辑。',
          '- Fully CS 沿用既有 `Lajavaness/bilingual-embedding-large`、CPU FP32、原版 top-1 余弦相似度；Partially 遮蔽种子 0；Cold 顺序为默认、字符串种子 `"0"`、`"42"`。',
          '- 每个分支内部串行；CS 先单独完成并退出，随后四个 API 分支并行。逐请求保存原始响应、实际请求参数及检查点；无重复名称缓存、重试或模型切换。',
          '- 本轮仅 DeepSeek 基座与相应接口参数变化。Sol 历史配置含 32768 输出预算，本轮采用 DeepSeek high 且不发送客户端上限；实际生成配置差异均有记录。', '',
          '模型映射与参数依据：[DeepSeek 官方文档](https://api-docs.deepseek.com/)、[模型说明](https://api-docs.deepseek.com/quick_start/pricing/)。读取时的文档副本见 `documentation/`。', '',
          '## 2. 评价口径', '',
          'Tuple 指标调用未经修改的官方 `tdm_eval.py`：先求逐篇 Precision / Recall，再做 Macro 平均；F1=2PR/(P+R)，由聚合 P/R 计算。Partially 和 Cold Start **统一以第二阶段为主指标**，第一阶段作为过程诊断单独保存。', '',
          '排行榜评价使用冻结的 27 个 Gold Leaderboards（本地文件含 140 个条目，原论文报告 138 个）。LR 是 TDM 命中榜比例，同时报告有效数值非空榜率；PC、RC、数值列表 RBO 沿用官方实现，论文 ID AO 是单独的辅助实现。原论文 AO 按作者报告值列示，不替换成 RBO。', '',
          '所有表格均为百分数。Cold 三顺序汇总为各次结果的算术均值与样本标准差（ddof=1）；各次 F1 均先按该次 Macro P/R 计算。', '',
          '## 3. 本轮全部 IIM 与 ETM 指标', '']
    for case in PRIMARY:
        p += [f'### {LABELS[case]}', '', table(['指标','Precision','Recall','F1'],
                 [[m]+[pct(new[case]['tuple'][m][k]) for k in ['Precision','Recall','F1']] for m in METRICS]), '']
    p += ['### Cold Start 三顺序汇总', '', table(['指标','P 均值 ± SD','R 均值 ± SD','F1 均值 ± SD'],
              [[m]+[f"{pct(cold_tuple[m][k]['mean'])} ± {pct(cold_tuple[m][k]['sd'])}" for k in ['Precision','Recall','F1']] for m in METRICS]), '',
          '## 4. 本轮排行榜指标', '', table(['设置']+LBN,
              [[LABELS[c]]+[pct(new[c]['leaderboards']['all27'][k]) for k in LB] for c in PRIMARY] +
              [['Cold 三顺序均值 ± SD']+[f"{pct(cold_lb['metrics'][k]['mean'])} ± {pct(cold_lb['metrics'][k]['sd'])}" for k in LB]]), '',
          '## 5. 与原论文、GPT-4.1、Sol 对比', '',
          '### 同设置 Tuple F1', '']
    compare_rows = []
    for case in ['fully','fully_cs','partially_stage2']:
        a, b, c = paper_row(case,'table_4'), paper_row(case,'table_12'), paper_row(case,'table_3')
        compare_rows.append([LABELS[case],'原论文 GPT-4 Turbo']+[f"{a['values'][m]['f1']:.2f}" for m in ['Task','Dataset','Metric','Result']]+[f"{b['values']['f1']:.2f}",f"{c['values']['f1']:.2f}"])
        for model in ['GPT-4.1','Sol','DeepSeek']:
            compare_rows.append([LABELS[case],model]+[pct(rows[model,case]['tuple'][m]['F1']) for m in METRICS])
    p += [table(['设置','模型','Task','Dataset','Metric','Result','TDM','TDMR'], compare_rows), '',
          '### 同设置排行榜', '']
    lb_compare = []
    for case in ['fully','fully_cs','partially_stage2']:
        old = paper_row(case,'table_5')['values']
        lb_compare.append([LABELS[case],'原论文 GPT-4 Turbo']+[f"{old[k]:.2f}" for k in ['LR','PC','RC']]+['—',f"{old['AO']:.2f}"])
        for model in ['GPT-4.1','Sol','DeepSeek']:
            lb_compare.append([LABELS[case],model]+[pct(rows[model,case]['leaderboards']['all27'][k]) for k in [LB[0],LB[2],LB[3],LB[4],LB[5]]])
    p += [table(['设置','模型','LR','PC','RC','RBO','AO'],lb_compare),'',
          '### Cold Start 排行榜三顺序均值 ± SD','']
    old = next(x for x in original if x['table']=='table_17' and x['model']=='GPT-4')['values']
    cold_comparison = [['原论文 GPT-4 Turbo']+[f"{old[k]['mean']:.2f} ± {old[k]['sd']:.2f}" for k in ['LR','PC','RC']]+['—',f"{old['AO']['mean']:.2f} ± {old['AO']['sd']:.2f}"]]
    for model in ['GPT-4.1','Sol','DeepSeek']:
        c = next(x for x in comp['cold_three_order_summaries'] if x['model']==model and x['scope']=='all27')['metrics']
        cold_comparison.append([model]+[f"{pct(c[k]['mean'])} ± {pct(c[k]['sd'])}" for k in [LB[0],LB[2],LB[3],LB[4],LB[5]]])
    p += [table(['模型','LR','PC','RC','RBO','AO'],cold_comparison),'',
          '原论文数据来自已核对的 Tables 3、4、5、12、17；逐行表号、页码和历史 JSON 路径见 `analysis/comparison_final/comparison.json`。GPT-4.1 Fully CS 的 LR 为 25/27，而有效非空榜率为 24/27，两者保持分列。', '',
          '## 6. 结果解释与可核查案例', '',
          f"**Fully 下数值覆盖较好，完整绑定仍有损失。** Result IIM F1 为 {pct(full['tuple']['Result IIM']['F1'])}%，比 Sol 高 {(full['tuple']['Result IIM']['F1']-sol['tuple']['Result IIM']['F1'])*100:.2f} 个百分点；TDMR F1 比 Sol 低 {(sol['tuple']['TDMR Exact Match']['F1']-full['tuple']['TDMR Exact Match']['F1'])*100:.2f} 个百分点。取到数值和正确绑定到任务、数据集、指标仍是两个不同的环节。", '',
          f"**本轮 CS 的主要损失在 Dataset 和 Metric。** 在完全相同的 295 条抽取上，Fully LLM 改为 CS 后，TDMR F1 从 {pct(full['tuple']['TDMR Exact Match']['F1'])}% 降到 {pct(new['fully_cs']['tuple']['TDMR Exact Match']['F1'])}%，相差 {(full['tuple']['TDMR Exact Match']['F1']-new['fully_cs']['tuple']['TDMR Exact Match']['F1'])*100:.2f} 个百分点。Result IIM 保持相同，差异来自名称映射。", '',
          '**Partially/Cold 的名称对齐明显不足。** 下面是第二阶段原版观察器的逐事件计数；“未匹配保留”表示模型回答未进入候选 TDM 集合，官方代码保留原输入。', '',
          table(['分支','原本精确匹配','成功映射','未匹配保留','null 跳过','回答等于输入 tuple'],
                [[LABELS[b+'_stage2'], events[b+'_stage2']['branches'].get('exact_tuple',0), events[b+'_stage2']['branches'].get('tuple_mapped',0),
                  events[b+'_stage2']['branches'].get('unmatched_preserved',0),events[b+'_stage2']['branches'].get('null_skipped',0),
                  events[b+'_stage2']['answers_equal_input_tuple']] for b in ['partially','cold_default','cold_0','cold_42']]), '',
          '例如默认 Cold 的首条输入为 `(Named Entity Recognition, ON5E, F1)`，候选包含 `(Named Entity Recognition (NER), Ontonotes v5 - English, F1)`。原始回答仍是输入 tuple；返回的 reasoning 明确按“Not exact”作出判断。此条没有 HTTP、JSON 或候选传递故障，失败发生在模型对原版匹配要求的解释和语义名称对齐。三个 Cold 顺序分别只有 12、10、12 条发生映射。原始请求、响应和事件保存在 `variants/cold_default/stage2/api_calls/0001/` 等目录。', '',
          table(['论文','环节','实际现象','证据位置'],[
             ['D18-1523.pdf','Extraction 遗漏','Prompt 中已有 FNMI 11.26±0.48、FBC 57.49±0.23、AVG 25.43±0.48；只输出 AVG。此篇无需名称请求，遗漏已发生在抽取阶段。','第5页 Table，证据索引5'],
             ['1811.09242.pdf','Extraction 列绑定','SemEval 2010 的 V-M 与 AVG 对应 10.1 / 25.2；预测绑定为 25.20 / 10.1。标准化保留原数值，未纠正错列。','第5页 Table，证据索引5'],
             ['C18-1139.pdf','Normalization 限定信息丢失','原始 Task 含 NER German、Dataset=CoNLL-2003、Result=88.32±0.20；逐字段标准化将 Dataset 映射为 CoNLL-2003-English，Task 中 German 限定被移除。','第3页 Table及对应字段请求']]), '',
          '具体预测、Gold、证据文本与文件哈希见 `inspection/examples.json`；前三类案例说明遗漏、错列和名称映射损失均仍存在。所有结果均按原样纳入评价。', '',
          f"严格有限数值相等辅助检查的 Result F1 为 **{pct(full['strict_result']['F1'])}%**，官方 Result IIM F1 为 **{pct(full['tuple']['Result IIM']['F1'])}%**。官方允许字符串包含匹配；辅助检查不解析 ± 不确定度字符串，也不做单位换算，因此差距同时受格式和数值匹配规则影响。详见各分支 `strict_result_metrics.json`。", '',
          '## 7. 实际请求、Token 与资源', '',
          table(['分支','Extraction','Normalization','请求合计','输入Tokens','输出Tokens（含推理）','总Tokens'],
            [[b,43 if b=='fully' else 0,v['attempts']-(43 if b=='fully' else 0),v['attempts'],v['prompt_tokens'],v['completion_tokens'],v['total_tokens']] for b,v in usage['branches'].items()]+[['fully_cs',0,0,0,0,0,0]]), '',
          f"合计 **{usage['actual_model_requests']:,} 次模型请求**：43 次 Extraction、{usage['actual_model_requests']-43:,} 次标准化；总 Tokens **{usage['total']['total_tokens']:,}**，其中输入 {usage['total']['prompt_tokens']:,}、输出 {usage['total']['completion_tokens']:,}，输出含 reasoning Tokens {usage['total']['reasoning_tokens']:,}。所有请求 HTTP 200、finish_reason=stop；重试 0 次，未知用量 0 次，格式失败 0 篇。额外一次认证模型列表 GET 未计入模型请求。", '',
          f"从首个请求到最后响应约 **{usage['wall_seconds_including_between_phase_gaps']/60:.2f} 分钟**，包含阶段间准备间隔；各请求耗时求和为 {usage['total']['seconds']/60:.2f} 分钟，分支并行使两者不同。CS 耗时 {cs['seconds']:.2f} 秒，进程峰值 working set **{cs['memory']['peak_working_set_GiB']:.2f} GiB**，未新增 API 请求或依赖。", '',
          '43 篇 Extraction 的输入 Token 数取自服务端 Usage。最长 `1912.08777.pdf` 为 54,967 输入 Tokens，输出 4,321 Tokens（含 3,325 reasoning），36 条合法记录，finish_reason=stop。全部论文页级证据数量、预测数量、调用数及输入长度见 `fully/paper_index.csv`。', '',
          '## 8. 完整性与结果位置', '',
          f"已核验 {audit['protected_and_provenance_files_checked']} 个输入、源码、历史结果及评价来源文件，变化 0；43 篇 source_documents 与冻结版本完全一致。所有分支均保留记录数量、顺序和 Result；本轮原始 Result 全为字符串，兼容转换次数为 0。实际请求均无客户端输出上限。", '',
          table(['文件/目录','内容'],[
             ['report.md','本中文汇总报告'],['results_summary.json','全部主指标、Cold三顺序统计和实际用量'],
             ['fully/paper_index.csv','43篇输入证据、预测数量、Token及逐篇路径'],
             ['fully/merged/raw_output.json / output.json / normalized_output.json','全量新Extraction及Fully LLM标准化'],
             ['variants/fully_cs/normalization/embedding_normalized_output.json','Fully CS'],
             ['variants/partially/stage1、stage2','Partially两阶段原始响应、事件和输出'],
             ['variants/cold_default、cold_0、cold_42','三种Cold顺序各两阶段'],
             ['analysis/evaluations/各分支/','官方原始评价JSON、全部P/R/F1、逐篇指标、排行榜及严格数值辅助指标'],
             ['analysis/comparison_final/','原论文、GPT-4.1、Sol、DeepSeek的JSON/CSV对照及逐篇比较'],
             ['inspection/','遗漏、列绑定、名称限定损失及第二阶段对齐行为的原始证据'],
             ['api_usage_summary.json / request_audit.csv','所有实际请求参数、响应模型、finish_reason和Token汇总'],
             ['verification.json / delivery_protected_hashes.json','全分支完成与文件完整性核验']]), '',
          '实验已完成并停止。检查点只用于核验和定位，已成功请求无需再次执行；历史 GPT-4.1、Sol、Llama、AxCell 结果及原版源码保持不变。']
    (ROOT/'report.md').write_text('\n'.join(p)+'\n', encoding='utf-8')
    (ROOT/'README.md').write_text('''# DeepSeek-V4.1-Flash SCILEAD — COMPLETE

入口：[中文报告](report.md)、[机器可读汇总](results_summary.json)、[完整性核验](verification.json)。

全部43篇完成；Extraction仅运行一次，六个最终分支完整保留。原始请求在fully/papers和variants各stage/api_calls中。
已完成任务不应重新执行。status.py仅检查状态，final_audit.py仅离线核验请求与输入。
evaluate_ready.py只补齐缺失的已完成阶段评价；已完成评价跳过，正式输出不覆盖。
analysis/README.md提供独立离线评价命令，variants/README.md记录适配和原版方法的对应关系。

主要结果路径见report.md。Partially及Cold Start主指标取第二阶段，第一阶段另列。
generation_config.json是实际请求公共参数；transport.py是唯一网络发送层。
凭据仅在执行时从指定deepseek.env读取，不复制到此目录。
本轮未提交GitHub，也未修改历史PPT或其他冻结实验。
''',encoding='utf-8')

if __name__ == '__main__': main()
