# P2：AxCell 批量 TeX 转换与解析

已按冻结的 39 篇可用输入清单执行阶段 2，当前停在 **P2，未授权阶段 3**。成功 37/39，失败 2/39；其余状态见表。成功产物覆盖 248/283 条本范围 Gold，仅表示论文覆盖，不是抽取命中。原数据集另有 4 篇无 TeX（12 Gold），未新增输入或混入队列。

相对于完整 SciLead，当前解析成功覆盖 37/43 篇、248/295 条 Gold。两篇失败合计 35 条 Gold，不能在后续比较中忽略其覆盖差异。

实际新增转换尝试 38 次，已有单篇 `1511.08308.pdf` / TeX v5 原样复用，不重新转换或抽取。没有自动重试、没有 Elasticsearch、没有模型加载或 ResultsExtractor、GPT 请求 0。没有因输出质量筛选论文。

## 固定配置与范围

AxCell commit `f4648d8fee1aa8482d007a38828da9dc06630f0e`；原版 `PaperExtractor(data_root)(source)` → `PaperText.from_html` → 原版表格提取与保存。Engrafo 镜像 `arxivvanity/engrafo:b3db888fefa118eacf4f13566204b68ce100b3a6`，digest `sha256:1ca3ffa0951005b11e56adba9ecef2aac2c03765a89fc1dbf1f1d31de72ee07e`。沿用已验证 Docker SDK `version=auto` 适配和稳定 containers 集合上的运行保护；源码/TeX/模型不改。

串行，一次一篇；转换容器 20 GiB、6 CPU、网络关闭、官方 remove=True。启动门槛可用 RAM ≥6 GiB、磁盘余量 ≥20 GiB；持续低内存/容器接近上限/OOM 保护沿用 P0/P1；每篇最长 600 秒，失败保留状态。4 项本地及远端保护/断点测试通过；实际超时清理测试仅运行无模型测试进程，其所属子进程全部退出。

**作者 36 篇子集的确切成员仍 UNVERIFIED，确认属于作者范围的数量仍无法给出；39 篇不能称为作者 36 篇复现。** 输入及 Gold 数量仅用于范围记录，不参与解析。

## 逐篇结果

| 论文 ID | Gold 数 | 状态 | 文本片段 | table/tabular 区域 | 耗时秒（见口径） | 错误 |
|---|---:|---|---:|---:|---:|---|
| 1911.10390.pdf | 8 | PARSE_COMPLETE | 98 | 6 | 13.5 | — |
| 2001.04063.pdf | 9 | PARSE_COMPLETE | 92 | 6 | 12.9 | — |
| 1905.03197.pdf | 26 | FAILED | — | — | 6.1 | processing-error |
| 1912.08777.pdf | 36 | PARSE_COMPLETE | 144 | 43 | 23.3 | — |
| 1906.05012.pdf | 3 | PARSE_COMPLETE | 89 | 8 | 6.5 | — |
| 2203.16804.pdf | 9 | FAILED | — | — | 304.6 | processing-error |
| 1910.13461.pdf | 25 | PARSE_COMPLETE | 112 | 7 | 16.3 | — |
| 1908.08345.pdf | 9 | PARSE_COMPLETE | 98 | 7 | 8.7 | — |
| 1808.08745.pdf | 3 | PARSE_COMPLETE | 99 | 8 | 10.0 | — |
| 2020.findings-emnlp.378.pdf | 6 | PARSE_COMPLETE | 69 | 11 | 12.6 | — |
| 1809.08370.pdf | 8 | PARSE_COMPLETE | 175 | 7 | 12.7 | — |
| 1806.03489.pdf | 2 | PARSE_COMPLETE | 104 | 7 | 11.1 | — |
| 1702.02098.pdf | 2 | PARSE_COMPLETE | 117 | 8 | 6.2 | — |
| 1511.08308.pdf | 2 | PARSE_COMPLETE（复用） | 154 | 11 | 0.0 | — |
| 2020.emnlp-main.523.pdf | 11 | PARSE_COMPLETE | 119 | 12 | 8.0 | — |
| 2105.03654.pdf | 7 | PARSE_COMPLETE | 102 | 8 | 36.6 | — |
| 1903.07785.pdf | 11 | PARSE_COMPLETE | 97 | 6 | 29.2 | — |
| D18-1279.pdf | 6 | PARSE_COMPLETE | 93 | 4 | 8.0 | — |
| 1703.06345.pdf | 5 | PARSE_COMPLETE | 74 | 3 | 5.2 | — |
| 1603.01354.pdf | 4 | PARSE_COMPLETE | 125 | 9 | 8.7 | — |
| 1709.04109.pdf | 3 | PARSE_COMPLETE | 101 | 10 | 8.6 | — |
| 2008.07772.pdf | 6 | PARSE_COMPLETE | 83 | 4 | 6.4 | — |
| 1911.09483.pdf | 4 | PARSE_COMPLETE | 86 | 5 | 68.2 | — |
| 1901.10430.pdf | 8 | PARSE_COMPLETE | 136 | 7 | 31.4 | — |
| 2002.03184.pdf | 7 | PARSE_COMPLETE | 66 | 7 | 11.2 | — |
| wang19f.pdf | 5 | PARSE_COMPLETE | 58 | 5 | 14.4 | — |
| 1804.09849.pdf | 2 | PARSE_COMPLETE | 124 | 6 | 9.1 | — |
| D18-1523.pdf | 3 | PARSE_COMPLETE | 67 | 5 | 4.6 | — |
| 1905.12598.pdf | 6 | PARSE_COMPLETE | 73 | 5 | 5.6 | — |
| 1811.09242.pdf | 6 | PARSE_COMPLETE | 84 | 7 | 9.9 | — |
| 1812.10235.pdf | 8 | PARSE_COMPLETE | 59 | 2 | 12.5 | — |
| 2020.emnlp-main.152.pdf | 6 | PARSE_COMPLETE | 36 | 3 | 4.8 | — |
| 1909.02188.pdf | 6 | PARSE_COMPLETE | 94 | 4 | 11.4 | — |
| 1907.00390.pdf | 6 | PARSE_COMPLETE | 38 | 3 | 4.5 | — |
| 1812.09471.pdf | 6 | PARSE_COMPLETE | 86 | 3 | 10.2 | — |
| N19-1373.pdf | 2 | PARSE_COMPLETE | 73 | 5 | 9.9 | — |
| K19-1036.pdf | 3 | PARSE_COMPLETE | 60 | 3 | 7.2 | — |
| 1811.05021.pdf | 2 | PARSE_COMPLETE | 115 | 4 | 13.1 | — |
| 1711.05568.pdf | 2 | PARSE_COMPLETE | 112 | 7 | 9.4 | — |

区域数是原解析器的 table/tabular 产物数量，不等于结果表数量或正确表格数；包含图形/统计表等时保持原样，未人工删改。合计 3512 个片段、266 个区域。这里没有给出抽取记录数或准确率，因为尚未运行阶段 3。

## 失败诊断与保留策略

- **1905.03197.pdf**：`processing-error` / `LATEXML_TOO_MANY_ERRORS`，容器退出信息 `{'exit_code': 117, 'error_type': 'ContainerError'}`。原始日志：`stage2/parse_logs/1905.03197.pdf/`。末尾诊断：Conversion complete: 4 warnings; 101 errors; 1 fatal error; 8 undefined macros[\scan, \tl, \bool, \clist, \cs, \keys, \ExplSyntaxOn, \msg]; 3 missing files[capt-of.sty, scalerel.sty, adjustbox.sty]. / Error! Did not write file /files/output/index.html / Engrafo rendering failed: Error: latexmlc exited with status 1
- **2203.16804.pdf**：`processing-error` / `OFFICIAL_CONVERTER_300S_TIMEOUT`，容器退出信息 `{'exit_code': 117, 'error_type': 'ContainerError'}`。原始日志：`stage2/parse_logs/2203.16804.pdf/`。末尾诊断：Error:undefined:\belowrulesep The token T_CS[\belowrulesep] is not defined. / Conversion complete: 6 warnings; 4 errors; 3 undefined macros[\DeclareUnicodeCharacter, \belowrulesep, \aboverulesep]; 1 missing file[acl.sty]. / /files/latex2html.sh: line 32:    16 Killed                  timeout -s KILL 300 engrafo "$MAINTEX" /files/output

完整日志优先于以上摘要。仅归类原失败，不升级镜像、不补装 TeX 样式、不改宏、不更换输入版本，不为了通过而重跑。失败论文不会默默剔除；正式后续评价范围需在后续验收中说明。

独立审查发现调度保护边界问题后，曾暂停控制器，让当前转换自然结束并保存检查点。只修复 owner 写失败时的 finally 清理、先停止生产进程后清理容器、清理失败优先停止后续队列、恢复未尝试的 BLOCKED 与已完成子进程对应的 RUNNING 状态。7 项策略测试及两项 Linux 实际进程清理 RED→GREEN 回归通过。v1 脚本/检查点保留，revision2 单独记录；原 `parse_one.py`、TeX、镜像、解析方法均未改变。恢复时跳过所有已成功或已失败的论文，没有重新生成挑选结果。

## 资源与完整性

- 从首次批次启动到最终结束的墙钟时间 1075.8 秒（含检查点暂停/工程处理）；两次控制器调用计时合计 1050.3 秒；38 次新增尝试的监控包络总计 881.5 秒，平均 23.2 秒（含失败）。逐篇表中成功项使用原入口内部秒数，失败项使用监控包络秒数；复用项为 0，表示本轮未再次转换。
- 转换容器 cgroup 采样峰值 10.702 GiB；Python/监控子进程 OS maxRSS 最大 0.154 GiB；不把二者相加当作同步精确总峰值。
- 最低 MemAvailable 18.176 GiB；结束复测 28.931 GiB。
- OOM 计数增长 0，swap-in/out 增长 0/0；最大采样 swap 增长 0.000 GiB。
- 磁盘剩余由 56.160 GiB 到 55.907 GiB；全盘净占用增加 0.253 GiB（含后台写入，非精确独占任务占用）。
- 分项实际分配磁盘：TeX归档 56.43 MiB，解包输入 184.11 MiB，HTML 10.62 MiB，文本/表格 4.19 MiB，逐篇日志 2.01 MiB。字节明细见 `stage2/resource_summary.json`，没有删除失败产物腾空间。
- 远端独立核验 643 个解析产物哈希；本地新同步产物 618 个匹配。39 篇输入、原源码/模型/单篇产物、P0/P1 报告及保护文件均经核验未改；依赖无变化，pip check 通过。
- 任务容器全部退出；不关闭既有 Docker daemon/服务器，不新增云实例/存储，不产生 GPT 费用。ECS 自身正常计费不因本报告而停止。

## 产物与断点

`parse_manifest.json`、`parse_status.csv`、`parse_resource_usage.csv`、`stage2_verification.json`、`stage2_gate.json`；详细索引 `stage2/parsed_output_index.json`，新解析产物 `stage2/parsed/papers/`、`stage2/parsed/htmls/`，逐篇日志 `stage2/parse_logs/`。复用单篇索引指向原只读产物，不伪造新运行。

远端 `/root/scilead/axcell/runs/20261022_formal/stage2/` 保留解包输入、中间产物、日志和状态。成功阶段只有输入/配置/全部产物哈希一致才可跳过；FAILED、RUNNING 或已有 attempt 不自动再次生成。进程独占锁避免双启动。不要直接删除 attempt 或状态以强行重跑。

本轮到此停止。下一步仅在 P2 明确确认后，基于验收通过的解析产物进入原版 AxCell 抽取，并停在 P3；不能自动调用 GPT。失败项的处理边界需要保留在批准范围中。
