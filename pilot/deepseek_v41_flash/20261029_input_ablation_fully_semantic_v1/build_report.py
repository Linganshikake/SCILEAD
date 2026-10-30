"""Assemble the completed paired experiment into inspectable Chinese tables."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text('utf8'))
NAMES={'baseline_rag':'历史 RAG','parsed_full':'完整解析文本','page_images':'整页图片'}
METRICS=['Task IIM','Dataset IIM','Metric IIM','Result IIM','TDM Exact Match','TDMR Exact Match']
BOARDS={'LR_exact_tdm_hit':'LR（TDM命中）','LR_nonempty_finite_result':'有效非空榜率','PC':'PC','RC':'RC','RBO':'官方数值 RBO','AO':'论文ID AO'}
def pct(x):return f'{100*x:.2f}'
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def csvsave(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    e=load(ROOT/'evaluation/report.json');assert e['status']=='COMPLETE' and e['all_three_arms_complete']
    v=load(ROOT/'verification.json');assert v['status']=='COMPLETE' and not v['protected_changed']
    u=load(ROOT/'api_usage_summary.json');m=load(ROOT/'experiment_manifest.json');changes=load(ROOT/'inspection/change_summary.json')
    lines=['# DeepSeek 五篇子集：Fully LLM 语义增强 Prompt 对照',
      '', '本轮把既有 Partially / Cold Start Prompt 中的语义对齐要求迁入 **Fully 名称标准化**。没有运行 Partially 或 Cold Start；三组抽取结果原样复用。',
      '', '## 实验设置', '',
      '- 固定五篇、28 条 Gold：D19-1367.pdf（2）、1901.10430.pdf（8）、1808.08745.pdf（3）、2020.emnlp-main.523.pdf（11）、1911.09483.pdf（4）。',
      '- 输入组：历史 RAG、完整解析文本、整页图片。分别复用 28、28、30 条原始 Extraction；本轮新增 Extraction 请求为 0。',
      '- Fully 固定完整候选集：Task 23、Dataset 71、Metric 26。逐字段处理；原样命中直接保留，其余分别调用；回答精确属于候选才接受，其他为 null；Result 不变。',
      '- 仅更换 normalization-system-prompt。每条新旧请求的用户消息、候选字符串及顺序、生成参数均已逐项比对一致；不加入论文上下文、Gold 对应关系或第二阶段联合 TDM 映射。',
      '- 模型请求与响应均为 deepseek-flash；thinking=enabled，reasoning_effort=high，stream=false；不传客户端输出上限，不添加工具或结构化输出格式。',
      '- 官方 tuple 指标沿用逐篇 Macro P/R；F1=2PR/(P+R)。排行榜沿用同一子集的 10 个榜、14 个榜内条目，其中 6 个单成员榜、4 个双成员榜。',
      '', '## Prompt 迁移', '',
      '新增要求包括：按实体含义匹配缩写、别名、同义表述和表面拼写差异；更具体的任务名称可匹配同一任务的标准名称；保留语言、版本、split、指标定义等有意义差异；输出候选项原文且不加引号。',
      '', '为保持 Fully 方法，源增强 Prompt 中“无匹配返回原输入”的规则改为“无匹配或含糊时返回 None”；不迁入动态扩充名称集合和第二阶段联合 tuple 的处理逻辑。',
      '', f"源增强文件 SHA256：`{load(ROOT/'prompt_migration.json')['source_sha256']}`。本轮 Prompt SHA256：`{m['prompt_sha256']}`。全文见 `enhanced_prompt.txt`，新增与适配记录见 `prompt_migration.json`，逐行变化见 `prompt_diff.txt`。",
      '', '## 汇总结果（百分数）', '', '| 输入组 | Result IIM F1 原→增强 | TDM F1 原→增强 | TDMR F1 原→增强 | TDMR变化（百分点） | null字段 原→增强 |',
      '|---|---:|---:|---:|---:|---:|']
    metric_rows=[];board_rows=[];paper_rows=[]
    for arm,a in e['arm_results'].items():
        o=a['old_fully'];n=a['enhanced_fully'];c=changes[arm]
        vals=[f"{pct(o['aggregate'][k]['F1'])} → **{pct(n['aggregate'][k]['F1'])}**" for k in ['Result IIM','TDM Exact Match','TDMR Exact Match']]
        delta=100*(n['aggregate']['TDMR Exact Match']['F1']-o['aggregate']['TDMR Exact Match']['F1'])
        lines.append(f"| {NAMES[arm]} | {' | '.join(vals)} | {delta:+.2f} | {c['old_null_fields']} → {c['new_null_fields']} |")
        for method,stage in [('original',o),('enhanced',n)]:
            for metric in METRICS+['Strict Result numeric equality']:
                metric_rows.append({'arm':arm,'method':method,'metric':metric,**stage['aggregate'][metric]})
            for k,val in stage['leaderboard']['aggregate'].items():board_rows.append({'arm':arm,'method':method,'metric':k,'value':val})
            for pid,per in stage['per_paper'].items():
                for k,val in per.items():paper_rows.append({'arm':arm,'method':method,'paper_id':pid,'metric':k,**val})
        assert o['aggregate']['Result IIM']==n['aggregate']['Result IIM']
        assert o['aggregate']['Strict Result numeric equality']==n['aggregate']['Strict Result numeric equality']
    lines+=['', '## 结果解释与具体变化', '',
      '本轮新增 Prompt 没有提高三组的总体 TDMR F1。名称匹配更强调实验限定信息后，13 个原有候选映射变成 null，2 个 null 被恢复为候选。三组 Result IIM 全部不变：本轮只处理名称，没有重抽数值或改写 Result。',
      '', '| 论文 / 场景 | 原始字段 | 原 Fully | 增强 Fully | 可确认的影响 |',
      '|---|---|---|---|---|',
      '| 1808.08745 / RAG | ROUGE-L F1；25.75 | null | ROGUE-L | 恢复了 Gold 的指标名称匹配 |',
      '| 1808.08745 / 图片 | ROUGE-1 F1；31.89 | null | ROGUE-1 | 修复旧响应带引号、无法精确接受的问题；保留 Gold 的 ROGUE 拼写 |',
      '| 2020.emnlp-main.523 / 图片 | Micro-F1；Open Entity 78.2、TACRED 72.7 | F1 | null | Gold 采用 F1，细粒度名称被拒绝后失去两条完整匹配 |',
      '| 2020.emnlp-main.523 / 三组 | CoNLL-2003；94.3 | CoNLL-2003 - English | null | 原输入未注明语言，增强后不再映射到 English 候选，损失官方命中 |',
      '| 1911.09483 / RAG、解析文本 | IWSLT 2014 De-En；36.3 | IWSLT’14 EN-DE | null | 输入语言方向与候选标签相反；拒绝映射降低官方命中，也暴露名称与实验条件的冲突 |',
      '| 1901.10430 / 解析文本 | Chinese-English；24.4；German-English；35.2 | WMT’17 EN-ZH；IWSLT’14 EN-DE | null | 两处方向信息与 Gold 候选标签相反，增强匹配予以拒绝 |',
      '| D19-1367 / 解析文本 | Validation Perplexity；58.0 | Perplexity | null | 更强调 split 差异；该值原本就不是该论文 Gold 的测试结果56.0 |',
      '', '这些变化显示：语义增强包含“更主动识别别名”和“更严格保留实验条件”两个方向。在 Fully 的逐字段输入中，缺少论文上下文去补足语言、split 和指标实现；后者容易增加拒绝映射。对当前 Gold 的较粗标签，保守拒绝会降低精确匹配分数。',
      '', '抽取端仍保留此前的错误和遗漏：例如 LUKE 的 Dev/Test 数值选择、遗漏 Precision/Recall，以及 RAG 中未抽到的数值。名称 Prompt 的修改不会补回这些记录。此次同时重发了名称请求，个别回答也可能有运行波动；所有原始响应均保留，可逐项复核。',
      '', '## 全部 tuple 指标（P / R / F1，百分数）', '', '| 输入组 | 指标 | 原 Fully P/R/F1 | 增强 Fully P/R/F1 |', '|---|---|---:|---:|']
    for arm,a in e['arm_results'].items():
        for k in METRICS:
            vals=[' / '.join(pct(a[s]['aggregate'][k][x]) for x in ['Precision','Recall','F1']) for s in ['old_fully','enhanced_fully']]
            lines.append(f"| {NAMES[arm]} | {k} | {' | '.join(vals)} |")
    lines+=['', '## Leaderboard 指标（百分数）', '', '| 输入组 | 指标 | 原 Fully | 增强 Fully | 变化（百分点） |','|---|---|---:|---:|---:|']
    for arm,a in e['arm_results'].items():
        for k,name in BOARDS.items():
            o=a['old_fully']['leaderboard']['aggregate'][k];n=a['enhanced_fully']['leaderboard']['aggregate'][k]
            lines.append(f'| {NAMES[arm]} | {name} | {pct(o)} | {pct(n)} | {100*(n-o):+.2f} |')
    lines+=['', 'PC、RC、数值 RBO 由官方代码原样生成。LR 分别记录 TDM 命中和有效非空榜率；AO 是沿用的论文 ID 辅助排序指标。榜单较短，排序变化需结合逐榜预测成员查看。',
      '', '## 逐篇指标（F1，原→增强；百分数）', '', '| 输入组 | 论文 | Result IIM | TDM | TDMR |', '|---|---|---:|---:|---:|']
    for arm,a in e['arm_results'].items():
        for pid in m['paper_ids']:
            vals=[f"{pct(a['old_fully']['per_paper'][pid][k]['F1'])} → {pct(a['enhanced_fully']['per_paper'][pid][k]['F1'])}" for k in ['Result IIM','TDM Exact Match','TDMR Exact Match']]
            lines.append(f"| {NAMES[arm]} | {pid} | {' | '.join(vals)} |")
    lines+=['', '## 运行与完整性', '',
      f"- 新请求144次，全部HTTP200 / finish_reason=stop，无重试。输入{u['tokens']['prompt_tokens']:,}、输出{u['tokens']['completion_tokens']:,}，合计{u['tokens']['total_tokens']:,} Tokens；三组并行请求区间{u['wall_seconds']:.2f}秒。",
      f"- {v['protected_files_checked']}个保护文件哈希未变；原始Extraction、Result、记录顺序、source_documents、Gold和官方源码均保持不变。",
      '- 六项离线回归检查通过，包括与未经改动的官方 Fully main 的合成样例逐项一致、无损重放和失败不自动重发。',
      '- 所有模型响应和标准化结果先写入完成。随后收尾扫描读取仍持有的 Windows process.lock 出现 PermissionError；进程退出后由独立离线程序完成相同哈希及凭据泄漏检查。未重发请求，原错误日志保留。',
      '- 本轮到此结束，不启动其他标准化分支。',
      '', '## 文件索引', '',
      '- `evaluation/report.json` / `evaluation/comparison.json`：官方原始计算、全部P/R/F1、逐篇/逐榜值与新旧差值。',
      '- `metrics.csv`、`leaderboard_metrics.csv`、`per_paper_metrics.csv`：便于制表的完整数值。',
      '- `inspection/changed_records.json`：15条发生字段变化的记录；`inspection/field_response_pairs.csv`：144次新旧回答逐项对应。',
      '- `baseline_rag/merged/`、`parsed_full/merged/`、`page_images/merged/`：原样复用的抽取和新的标准化输出。',
      '- 各组 `papers/<paper_id>/requests/`：脱敏请求、响应、Token Usage、字段映射和检查点。',
      '- `prompt_diff.txt`、`enhanced_prompt.txt`、`prompt_migration.json`：Prompt全文、修改文字及Fully适配依据。',
      '- `api_usage_summary.json`、`verification.json`、`engineering_finalization.json`：调用汇总、完整性及离线收尾记录。']
    (ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    csvsave(ROOT/'metrics.csv',metric_rows);csvsave(ROOT/'leaderboard_metrics.csv',board_rows);csvsave(ROOT/'per_paper_metrics.csv',paper_rows)
    v.update(evaluation_status='COMPLETE',official_evaluation_sources_unchanged=e['protected_files_unchanged'],
        evaluation_report_sha256=hashlib.sha256((ROOT/'evaluation/report.json').read_bytes()).hexdigest(),
        result_iim_and_strict_numeric_unchanged=True)
    save(ROOT/'verification.json',v)
    print(json.dumps({'report':str(ROOT/'report.md'),'metric_rows':len(metric_rows),'leaderboard_rows':len(board_rows),'per_paper_metric_rows':len(paper_rows)}))
if __name__=='__main__':main()
