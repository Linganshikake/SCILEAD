"""Render audit findings; do not compute threshold2 experiment scores."""
from common import *
from datetime import datetime, timezone


def md(name, value):
    path = ROOT/name
    assert path.resolve().is_relative_to(ROOT.resolve())
    path.write_text(value.strip()+'\n', encoding='utf-8')


def main():
    setup()
    audit = read(ROOT/'data_audit.json')
    refs = read(ROOT/'threshold3_frozen_reference.json')
    reuse = read(ROOT/'reuse_manifest.json')
    verified = read(ROOT/'verification.json')
    assert verified['status'] == 'AUDIT_PASS_EXPERIMENT_BLOCKED'
    assert audit['status'] == 'BLOCKED'
    source = read(ROOT/'source_manifest.json')
    summary = '''| 范围 | 唯一 TDM / 榜数 | 原始记录数 | 不同论文数 | 性质 |
|---|---:|---:|---:|---|
| 完整冻结 Gold | 141 | 295 | 43 | 官方附件中的原始标注 |
| 作者独立提供的榜单 | 27 | 140 | 43 | 当前正式 threshold=3 评价输入 |
| 完整 Gold 按至少 3 个不同 paper_id 分组 | 33 | 158 | 43 | 数量/差异诊断 |
| 完整 Gold 按至少 2 个不同 paper_id 分组 | 62 | 216 | 43 | 数量/差异诊断，禁止正式评分 |
| 独立作者 threshold=2 文件 | 未找到 | 未核验 | 未核验 | BLOCKED |'''
    differences = ['| Task | Dataset | Metric | 1905.03197.pdf | 1910.13461.pdf | 1903.07785.pdf |',
                   '|---|---|---|---:|---:|---:|']
    for item in audit['ge3_groups_missing_from_provided27']:
        values = {r['paper_id']: r['Result'] for r in item['rows']}
        differences.append('| '+' | '.join(item['tdm'])+' | '+
            ' | '.join(str(values[p]) for p in ('1905.03197.pdf','1910.13461.pdf','1903.07785.pdf'))+' |')
    md('data_differences.md', f'''# Gold 版本与分组差异

状态：BLOCKED。以下均比较原始标注，未进行排行榜 Result 清洗、乘除 100、排序或模型输出修正。

{summary}

## 33 / 27：定位到六个分组，未解释作者排除原因

完整 Gold 中满足至少三篇条件的 33 个 TDM，包含全部作者 27 榜。额外六组如下，每组都是同三篇论文，合计 18 条原始记录。

{chr(10).join(differences)}

因此 33=27+6、158=140+18。没有证据表明应删除这些记录或合并名称；本轮未这样操作。六组的定位解释了数量差额，不能解释作者历史选择原因。

## 141 / 138：仍未解决

原论文 Table 1（本地参考文本 page-03.txt:55）报告 138 unique TDM；冻结 JSON、本次重新取得的官方 Data JSON、原始 TSV 都得到 141。
TDM 按三个原始字符串构成 tuple，未 strip、改大小写、改拼写或合并别名。没有找到另一版 138-TDM 标注，不能指定三组进行人为合并。

## 62 的来源边界

诊断分组有 16 个 Task、62 个 TDM、216 条原始记录、43 篇论文。其相对作者 27 榜增加 35 组/76 条记录，即 29 个两篇组和上述六个三篇组。
数量与原论文 threshold=2 描述相符，但来源只是本轮从当前 Gold 重建；不能据此宣称获得作者正式 62 榜。
诊断文件为 diagnostics/current_gold_ge2_NOT_FOR_SCORING.json，带禁止评分标识，并保留所有原始行和 paper_id。

## 共有 27 榜与结构检查

全部 27 榜的精确 TDM、论文成员、原始 Result 与完整 Gold 及诊断 62 组完全一致。没有未知论文 ID、重复榜单、重复 JSON 对象键、重复 Gold 行或同 paper/TDM 多 Result 冲突。
尚未进行 threshold=2 正式评价，所以不存在可报告的“共有榜单新旧逐榜得分比较”；这里只核实原始成员与数值。

## 官方附件版本比较

本次 Data ZIP 与本地原始 ZIP SHA256 完全相同。其 JSON 标注与冻结标注逐条相同：新增/删除/修改记录均为 0，名称集合仍为 23 Task、71 Dataset、26 Metric。
TSV 与 JSON 的结构化记录也一致；比较时仅将 TSV 数值 Result 解码为数字，原文件不变，名称字符串不变。具体差异数组和哈希保存在 data_audit.json、source_manifest.json、diagnostics/tsv_vs_json.json。
''')

    metric_rows = ['| 指标（0–1） | Fully LLM：旧 27 榜 | Fully CS：旧 27 榜 | threshold=2 |',
                   '|---|---:|---:|---|']
    keys = [('目标榜数','gold_leaderboards'),('Gold 榜内记录数',None),
            ('精确 TDM 命中榜数','tdm_hit_boards'),('有效数值非空榜数','nonempty_valid_result_boards'),
            ('LR：精确 TDM 命中率','LR_exact_tdm_hit'),('有效数值非空榜率','LR_nonempty_finite_result'),
            ('PC（官方）','PC_official'),('RC（官方）','RC_official'),
            ('RBO（官方数值列表）','RBO_official_value_rankings'),
            ('AO（论文 ID）','AO_paper_id_macro_all_gold_boards')]
    for label, key in keys:
        vals = [refs[k]['aggregate'][key] if key else 140 for k in ('fully_llm','fully_cs')]
        fmt = lambda x: str(x) if isinstance(x,int) else f'{x:.6f}'
        metric_rows.append(f'| {label} | {fmt(vals[0])} | {fmt(vals[1])} | 未运行：数据 BLOCKED |')
    md('comparison_threshold3_vs_threshold2.md', f'''# Threshold=3 与 Threshold=2 比较状态

本轮未获得可核验的作者 threshold=2 文件，未生成新的正式分数。下表只摘录冻结 threshold=3 结果；没有将诊断 62 组用作 Gold。

{chr(10).join(metric_rows)}

旧指标来源及 SHA256 已保存到 threshold3_frozen_reference.json。Fully LLM 来源 leaderboard_eval_full43_uncapped/paper_metrics/leaderboard_metrics.json；CS 来源 full43_cs/leaderboard_evaluation/paper_metrics/leaderboard_metrics.json。本轮没有重新执行其评测。

本表按本轮要求把 LR 明确列为“标准 TDM 精确命中率”，并另列非空有效数值榜率。历史文件 conventions.LR_primary 曾把非空数值率作为主口径，这里不覆盖旧字段，只显式区分两种口径，避免同名误比。

共有 27 榜的原始 Gold 与诊断分组一致；冻结预测文件哈希未变。由于正式 threshold=2 评价未运行，逐榜得分一致性为 NOT_RUN，不冒称已复算通过。以后应在已核验新 Gold 下比较同 27 榜，发现差异时检查重复数值缩放、对象复用、排序及缓存。

全部 43 篇的预测与 tdm_annotations 未变；因此本轮没有改变 TDMR/IIM 的评价输入，也没有产生新的 TDMR/IIM 分数。改变排行榜评价集合不代表抽取能力变化。

## 后续必须继承的评价边界

- 使用未修改的 leaderboard_eval.py 和已审计的独立 CLI/AO 补充入口；每次从原始文件新读对象，避免再次缩放。
- Result 沿用官方清洗/缩放，同 paper/TDM 使用原输入顺序中最后一个可转换记录；不替换复合数值、不修正名称或语言方向。
- 排序方向沿用官方实现；AO 的数值并列按 paper_id 升序确定次序，保留并列论文。
- 空榜 AO 为 0；全部目标 Gold 榜都计入 Macro 分母。没有“预测少于两篇则删榜”的额外规则。
- RBO 使用官方去重数值排名和已安装 rbo=0.1.3 的原调用；AO 使用论文 ID。两者不互换名称。
- 新目标榜单中的转换/覆盖边界尚未运行检查，不能宣称与旧范围完全相同；后续逐榜保存原值、转换值和排名。

对照原论文 Table 15 时，本地模型是 GPT-4.1 固定快照，原文是 GPT-4 Turbo；同时必须披露数据版本、LR 两种口径、官方 RBO 与论文 ID AO 的差别。本轮不计算相对 Table 15 的性能差异。
''')

    cold_rows = ['| 轮次 | cold_start_seed | 类型 | stage1 SHA256 | 复用结论 |',
                 '|---|---|---|---|---|']
    for order, info in reuse['cold_start'].items():
        cold_rows.append(f"| {order} | {json.dumps(info['cold_start_seed'])} | {info['seed_type']} | `{info['stage1']['sha256']}` | 可复用 stage1；重跑新目标 stage2 |")
    md('next_stage_plan.md', f'''# 后续阶段准备（未授权在本轮执行）

当前状态 BLOCKED。next_stage_configs.json 的 enabled=false，verified_threshold2_path/sha256 与 shared_masked_subset_path/sha256 均为 null；不会把诊断重建清单自动填入输入。

## 解锁材料

需要作者发布或作者提供的 threshold=2 榜单文件，以及可追溯下载页/版本/说明；结构应包含精确 Task、Dataset、Metric 和 paper_id→Result 映射。还需解释其与冻结 Gold、当前 27 榜的任何实质差异。
获得后原样另存并校验哈希、重复键、不同 paper_id 阈值、成员和数值。不能用“正好 62”代替来源核验。现有 141/138 与六个额外三篇组的历史差异应持续披露，不人工修正。

## 复用关系

| 分支/阶段 | 可复用 | 后续动作 |
|---|---|---|
| Zero-shot Extraction | 43 篇/284 条原始预测及全部 source_documents | 不重新抽取、解析、索引或检索 |
| Fully LLM | 现有名称标准化输出 | 数据 READY 后仅离线评价新榜单集合 |
| Fully CS | 现有名称标准化输出 | 数据 READY 后仅离线评价新榜单集合 |
| Partially stage1 | 不直接复用旧动态标准化 | 新 mask 与初始名称集合确定后重新运行 |
| Partially stage2 | 不复用旧 27 榜对齐结果 | 对新 stage1 使用完整新目标榜单进行对齐 |
| Cold Start 三轮 stage1 | 可复用，已核验顺序/种子类型/原输出 | 保持原记录顺序、Result 和证据 |
| Cold Start 三轮 stage2 | 不复用旧 27 榜对齐结果 | 对各自已冻结 stage1 使用完整新目标榜单 |
| Few-shot | 不参与本轮阈值对照 | 继续独立冻结 |

## Partially masking 的原始依赖

原函数 tdm_llm_masked_normalization.py:13–57 根据输入榜单顺序累计各 Task 榜数，从排除最多/最少榜数 Task 后的候选列表，用整数 masking seed=0 抽取 round(Task数/3) 个 Task。
同时 mask 这些 Task 榜中的 Dataset；Task 或 Dataset 满足 mask 的榜组成 masked 子集。初始 Task/Dataset 名称取完整 Gold 排除 mask 的集合，Metric 取完整 Gold。
数据 READY 后才调用原函数，保留作者文件顺序、PYTHONHASHSEED=0，保存候选列表及其顺序、Masked Task/Dataset、masked 榜和三类初始名称集合。使用适当末尾路径分隔符，输出仅写入新目录。
不沿用旧 Masked 10 榜，不预设新 masked 数量，也不为了匹配论文数字更改抽样。当前没有运行 masking_preview。

## Cold Start stage1 独立性

原函数 cold_start=True 分支仅把目标榜单写入 sidecar，三类初始候选集合始终为空；stage1 后续输入只由抽取结果、当前候选状态、Prompt 和论文顺序决定。
main 中 gold_leaderboards 只在读文件和调用 sample_tdms 两处出现（66、81 行），不进入后续模型请求。三轮原 initial_labels 均为空、原 stage1 重放验证 PASS，当前逐篇 Result 字符串、证据和记录数量仍与原始 284 条抽取一致。

{chr(10).join(cold_rows)}

使用原 dict key 顺序或 random.sample 重算后的顺序与各轮 paper_order.json 完全一致。字符串 "0"、"42" 不能改成整数；生成模型 seed 仍为整数 0。
未来可以重新生成描述新目标的 sidecar，但不把 sidecar 差异解释为需要重跑 stage1，也不改写原实验目录。

## Stage2 与共同 Masked 评价

leaderboard_llm_normalization.py:17–23 从完整目标榜单构造 TDM 候选集合，所以新目标会影响 stage2 请求。不能把旧 27 榜 stage2 当作 threshold=2 结果。
Stage2 候选是完整新目标集合，不是 masked 子集。后续 Partially 和三轮 Cold Start 都同时评全目标与同一个“新 Partially mask”子集；不能沿用旧 10 榜或把 Cold sidecar 中的全部目标榜当成共同 Masked 评价范围。
保留现有 GPT-4.1 快照、temperature=0、整数 seed=0、不传输出上限、原 Prompt/动态逻辑和无重试适配；不手工映射、不新增缓存。
本轮仅保存依赖与配置，新增模型/API 推理调用为 0，下一阶段尚未启动。
''')

    fetched = [x for x in source['fetches'] if x.get('status') == 'FETCHED']
    fetch_rows = ['| 官方来源 | 结果 |', '|---|---|']
    fetch_rows += [f"| [{Path(x['path']).name}]({x['url']}) | HTTP {x['http_status']}，{x['bytes']:,} bytes |" for x in fetched]
    md('report.md', f'''# SCILEAD threshold=2 数据审计与复用准备

**结论：BLOCKED。安全审计与复用准备已完成；正式 threshold=2 评价和 masking preview 未运行。新增 LLM/API 推理调用：0。**

## 数据来源

从 [ACL 论文页面](https://aclanthology.org/2024.emnlp-main.453/) 解析出目前有效的 `/attachments/` 下载路径，成功下载 Data 和 Software 附件。两份 ZIP 均与本地原始 ZIP SHA256 一致；本轮新记录因此补充了独立的官方来源验证，未修改历史来源记录。

{chr(10).join(fetch_rows)}

原请求给出的不带 `/attachments/` 的两个 ZIP 地址均返回 HTTP 404。作者 [TUdatalib 入口](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/4345) 在本会话正常证书验证下出现证书链错误或连接超时，未取得其文件列表；不能据此声称作者库不存在 threshold=2 文件。

Data ZIP 只有 README.md、27 榜 leaderboards.json、tdm_annotations.json 和 TSV；Software ZIP 为代码文件，没有 threshold=2 榜单。Data README 明确写最低三篇/27 榜。固定 commit 的 GitHub README 指向同一 TUdatalib 入口，没有另外的 threshold=2 下载链接。

官方 Data ZIP SHA256：`37db7fed3abec7b472ab3de408575bf428b5281adc8b78d39436df0c2c1318c2`。
各文件来源、大小、SHA256、归档成员、结构及版本比较完整保存在 source_manifest.json 和 data_audit.json。没有执行下载归档内的脚本。

## 实际计数与差异

{summary}

按原始 TDM 字符串 tuple、不同 paper_id 计数，未修正名称或缩放 Result。名称集合为 23 Task /71 Dataset /26 Metric。
共有 27 榜的成员和 Result 完全一致；未发现重复 JSON 键、重复榜、未知论文 ID、重复 Gold 行或同 paper/TDM 冲突。官方附件标注、冻结 JSON、TSV 结构化记录一致。

141/138 差异仍未解释。33/27 差额已定位为 CoLA、SST-2、MNLI-m、MNLI-mm、QNLI、RTE 的六组三篇 TDM，但作者为什么未将其纳入独立 27 榜尚无依据。精确任务/指标、三篇 ID 和原值见 [data_differences.md](data_differences.md)。

诊断得到 62 组/216 条，且包含全部旧 27 榜，只证明当前标注可生成这些分组。按本轮要求，它不能代替作者历史 threshold=2 文件，不能用于正式评分。

## 已完成的结果复用核验

从 manifest、已审计评价 invocation 和逐篇索引交叉定位 Fully LLM/CS 输出，确认二者共用同一份 Zero-shot Extraction：43 篇、284 条。逐篇标准化结果与各自合并文件一致；Result 字符串、记录顺序和 source_documents 保持不变。
三种 Cold Start 的 stage1 初始集合为空，顺序及种子类型复算一致，43 篇/284 条输出可复用；新目标 stage2 仍需后续执行。Partially 必须在已核验新榜单上重新生成 mask，再运行两个阶段。
详细文件索引和哈希：reuse_manifest.json；后续禁用配置：next_stage_configs.json；依赖说明：[next_stage_plan.md](next_stage_plan.md)。

## 评价状态

Fully LLM /Fully CS 的 threshold=2 正式指标：**未生成**。未创建 fully_llm_evaluation/、fully_cs_evaluation/、masking_preview/。
[comparison_threshold3_vs_threshold2.md](comparison_threshold3_vs_threshold2.md) 仅保留旧 27 榜分数及口径说明，threshold=2 一列标为未运行。共有 27 榜原始成员/数值检查通过，但新旧逐榜得分比较未运行，不宣称已验证其得分相同。
本轮没有改变 43 篇 TDMR/IIM 的输入，也没有将排行榜范围变化写成抽取指标变化。未来对照 Table 15 须注明本地 GPT-4.1 与论文 GPT-4 Turbo 不同，并保留 LR/RBO/AO 边界。

## 完整性与执行边界

最终 SHA256 核验通过：7 个冻结实验/参考目录共 {verified['total_frozen_files']:,} 个文件，文件集合及内容均未变；另核验 {verified['sources_prompt_gold_checked_files']} 个源码/Prompt/Gold/归档文件，依赖版本不变，Git 工作区干净。
Commit：`{verified['git_commit']}`。全部新增文件仅写入本目录。未读取 API Key、未请求任何推理接口、未初始化模型、未重跑解析/Embedding/检索/抽取/标准化、未安装包。
来源核验使用的是公开页面/小型附件 HTTP GET，不是模型推理。独立审计脚本启用网络/敏感配置读取保护；结果见 verification.json。

## 缺失材料与停止点

继续正式评价需要具有作者来源和版本记录的 threshold=2 榜单原文件，并通过与冻结标注及共有 27 榜的兼容性核验。当前已完成所有不依赖该材料的安全步骤，按要求在此停止；不使用诊断 62 组绕过门槛，也不启动 Partially/Cold Start API。
''')
    md('README.md', '''# 离线审计文件说明

当前为 BLOCKED，不是 threshold=2 复现成功。

- report.md：结论、数据范围、来源与缺失材料。
- source_manifest.json：原始路径、正式下载 URL、哈希、归档成员与获取失败。
- data_audit.json / data_differences.md：精确字符串/不同论文计数、差异和结构检查。
- verified_inputs/：仅核验过的冻结参考副本及 README，不包含已验证作者 threshold=2 文件。
- diagnostics/：只做数量/差异检查，禁止正式评分。
- reuse_manifest.json：Fully/Cold 复用文件索引、哈希和验证。
- threshold3_frozen_reference.json / comparison_threshold3_vs_threshold2.md：旧分数参考，不是新实验结果。
- next_stage_configs.json / next_stage_plan.md：禁用的未来配置及依赖关系。
- freeze_before.json / verification.json：运行前后 42,610 个历史文件及源码/Gold/依赖完整性。
- artifact_sha256.json：本轮文件清单（不含该清单自身）。

复核已有离线审计可依次执行 audit_data.py、prepare_reuse.py、verify.py、write_reports.py，解释器 D:\\miniconda3\\envs\\scilead\\python.exe，参数 -B -X utf8。脚本仅写本目录，不调用模型。freeze.py 是首次快照，不可覆盖运行。fetch_official.py 是单独公共来源下载器，不需在离线复核时运行。
如果未来获得另一官方数据版本，先另存并单独审核，不能直接让本轮诊断输出变成实验输入。本轮不提供会自动启动 API 的执行命令。
''')
    plan = (ROOT/'execution_plan.md').read_text(encoding='utf-8').replace('- [ ]', '- [x]')
    plan += '\nFinal: audit/reuse/integrity checks complete; READY gate failed. Conditional scoring and masking intentionally NOT RUN. No model inference.\n'
    md('execution_plan.md', plan)
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name != 'artifact_sha256.json')
    save(ROOT/'artifact_sha256.json', {str(p.relative_to(ROOT)): sha(p) for p in paths})
    print('REPORTS_SAVED', len(paths), 'hashed artifacts; BLOCKED; inference=0')


if __name__ == '__main__':
    main()
