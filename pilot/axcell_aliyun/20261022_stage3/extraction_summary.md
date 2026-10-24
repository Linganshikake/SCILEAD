# AxCell 阶段3：批量 Extraction（P3阶段性检查点）

**本轮未完成37篇批量任务。** 1912.08777.pdf触发编排保护后，按用户要求停止整批，33篇未启动。原因详见 resource_stop_analysis.md；不能将该保护中止称为已证实的内存耗尽或AxCell算法错误。

37 篇可运行输入中，流程完成 3 篇；非空预测 3 篇，VALID_EMPTY 0 篇。原始记录共 **11 条**，其中新增 9 条、复用单篇 2 条。这里的“完成/记录有效”仅表示程序及结构检查通过，不表示预测正确。

新增模型抽取尝试 3 次，串行运行；1511.08308.pdf 完整复用，未再次生成。1905.03197.pdf、2203.16804.pdf 保持阶段2 FAILED，未重试解析或抽取。GPT 请求 **0**，未标准化、未正式评价。

**作者原论文36篇子集成员仍未完全核实（UNVERIFIED）**。本轮不能称为作者36篇范围复现。37篇解析范围覆盖248条Gold，仅表示范围，不是抽取命中。另两篇解析失败与4篇无TeX仍是全量覆盖限制。

## 逐篇状态

| 论文ID | 状态 | 原始记录 | 文本/表格区域 | 本轮耗时秒 | 最大RSS GiB | 说明 |
|---|---|---:|---|---:|---:|---|
| 1911.10390.pdf | EXTRACTION_COMPLETE | 6 | 98/6 | 57.45 | 4.087 | 原版抽取 |
| 2001.04063.pdf | EXTRACTION_COMPLETE | 3 | 92/6 | 73.741 | 4.063 | 原版抽取 |
| 1905.03197.pdf | FAILED | — | —/— | — | — | processing-error |
| 1912.08777.pdf | FAILED | — | 144/43 | 116.56 | — | RuntimeError: SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1906.05012.pdf | BLOCKED | — | 89/8 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 2203.16804.pdf | FAILED | — | —/— | — | — | processing-error |
| 1910.13461.pdf | BLOCKED | — | 112/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1908.08345.pdf | BLOCKED | — | 98/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1808.08745.pdf | BLOCKED | — | 99/8 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 2020.findings-emnlp.378.pdf | BLOCKED | — | 69/11 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1809.08370.pdf | BLOCKED | — | 175/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1806.03489.pdf | BLOCKED | — | 104/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1702.02098.pdf | BLOCKED | — | 117/8 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1511.08308.pdf | EXTRACTION_COMPLETE | 2 | 154/11 | 0 | — | 复用历史成功结果，零新增生成 |
| 2020.emnlp-main.523.pdf | BLOCKED | — | 119/12 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 2105.03654.pdf | BLOCKED | — | 102/8 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1903.07785.pdf | BLOCKED | — | 97/6 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| D18-1279.pdf | BLOCKED | — | 93/4 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1703.06345.pdf | BLOCKED | — | 74/3 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1603.01354.pdf | BLOCKED | — | 125/9 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1709.04109.pdf | BLOCKED | — | 101/10 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 2008.07772.pdf | BLOCKED | — | 83/4 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1911.09483.pdf | BLOCKED | — | 86/5 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1901.10430.pdf | BLOCKED | — | 136/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 2002.03184.pdf | BLOCKED | — | 66/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| wang19f.pdf | BLOCKED | — | 58/5 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1804.09849.pdf | BLOCKED | — | 124/6 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| D18-1523.pdf | BLOCKED | — | 67/5 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1905.12598.pdf | BLOCKED | — | 73/5 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1811.09242.pdf | BLOCKED | — | 84/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1812.10235.pdf | BLOCKED | — | 59/2 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 2020.emnlp-main.152.pdf | BLOCKED | — | 36/3 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1909.02188.pdf | BLOCKED | — | 94/4 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1907.00390.pdf | BLOCKED | — | 38/3 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1812.09471.pdf | BLOCKED | — | 86/3 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| N19-1373.pdf | BLOCKED | — | 73/5 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| K19-1036.pdf | BLOCKED | — | 60/3 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1811.05021.pdf | BLOCKED | — | 115/4 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |
| 1711.05568.pdf | BLOCKED | — | 112/7 | — | — | SUSTAINED_MEMORY_GROWTH_NO_PROGRESS |

## 方法与资源

固定 AxCell commit f4648d8fee1aa8482d007a38828da9dc06630f0e。直接导入已验收单篇 run_single.py 并校验SHA256，调用相同 ResultsExtractor；仅绑定论文ID、冻结解析产物副本和独立输出目录。继续使用相同模型、taxonomy、abbreviations、结构/置信度/最佳结果过滤器（0.8、0.85），只保留已验证的空进度条显示兼容层。没有重新解析、训练、修正或根据Gold筛选。

每篇使用独立空初始 Elasticsearch 6.7.1 索引，与单篇验证相同；原 paper_limit=30、corpus_limit=10 查询参数不变，索引只由该论文的官方流程写入。作者完整ES索引语料尚未核实，不能声称这一语料条件已完全复现。ES和模型串行启动/停止，不并发预加载。

本轮墙钟 4.13 分钟；已正常退出的新抽取进程OS最大RSS 4.087 GiB（被保护中止的进程没有最终rusage记录，另见采样值）；进程组cgroup采样峰值 4.149 GiB；ES cgroup采样峰值 1.304 GiB。口径不同且不一定同时出现，不相加当作精确总峰值。最低主机可用RAM 23.500 GiB，结束 28.926 GiB。
内核OOM增量 0（运行前历史计数为1），swap-in/out增量 0/0。磁盘可用 55.811 → 55.804 GiB（全盘变化含后台写入）。

启动保护≥6GiB可用RAM、≥20GiB磁盘；运行低于4GiB可用RAM即停；模型cgroup达到14GiB、ES达到2.4GiB提前停止（硬限制18/3GiB）；持续增长且无进展、OOM和1800秒墙钟保护均停批。独立任务服务2秒退出宽限，监控清理过程。没有修改系统全局内存/swap或安装依赖。

## 错误保留与后续边界

1511.08308.pdf 的两条原始错误完整保留：Table 6 的Recall 91.85被绑定为F1；Table 11测试集实体数量4696被当成F1分数。原值、来源cell_ext_id和中间候选保存在raw_outputs，未用于人工修正规则。其他结果须结合来源表格审查，不把高数值或零预测直接等同程序错误。

原模型序列化对象加载时出现的SourceChangeWarning与空生成器警告原样保留，未因此替换依赖或修补模型。具体异常以逐篇worker.stderr.log、controller_error.log及state.json为准。

成功非空论文可在P3验收后进入标准化请求准备；VALID_EMPTY属于成功空预测，应保留分母和状态，不需要为其虚构标准化请求。失败/阻塞论文不能冒充已完成结果。标准化须遵循后续P4付费授权；模型将固定gpt-4.1-2025-04-14。

## 完整性与产物

本地历史文件检查 1661 个，远端冻结文件检查 1850 个；详见stage3_verification.json。所有解析产物、源码、模型和依赖均单独核验。原正式阶段2报告未更新、两篇失败记录未改写。
本目录包含extraction_status.csv、extraction_manifest.json、resource_usage.csv、resource_summary.json、stage3_verification.json。remote_results/papers/<paper_id>/保存输入副本、原始记录/表格来源/全部候选与筛选轨迹、运行日志和资源检查点。服务索引数据仅保留远端，不复制模型。
远端：/root/scilead/axcell/runs/20261022_stage3/。所有本任务容器已停止（以verification实际清单为准），Docker daemon与ECS保留。没有自动关机或新增云资源。

**本轮在P3阶段性检查点停止，待用户复核保护规则与后续恢复范围；尚未达到37篇全部完成的P3验收条件，不启动GPT标准化或正式评价。**
