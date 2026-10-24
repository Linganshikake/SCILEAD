# AxCell 阶段3：受控恢复与批量抽取（P3）

本次在用户批准适当放宽保护后执行。37篇可运行输入已完成 **37/37**；非空预测28篇，VALID_EMPTY 9篇，原始记录合计 **65条**。这里的完成仅指流程与结构校验，不表示预测正确。
本次新增34次模型抽取尝试：重试1912.08777.pdf一次，另处理33篇此前未启动论文。1911.10390.pdf、2001.04063.pdf、1511.08308.pdf原样复用。原阶段2失败的1905.03197.pdf、2203.16804.pdf保持FAILED，不解析、不抽取。
GPT请求0，未标准化、未正式评价。停在P3等待验收。作者原论文36篇子集成员仍UNVERIFIED，本轮37篇不能称为作者36篇准确范围的复现。37篇解析范围对应248条Gold，仅是覆盖范围，不是命中数。

## 保护调整与方法保持

旧保护把“约90秒内内存增长2GiB且无新管线事件”当成失去进展，可能误判长结构识别阶段。此次移除该启发式停止，保留内存曲线，新增cgroup CPU计数，最长单篇从30分钟延长至60分钟。模型14GiB提前停止/18GiB硬限制、ES2.4/3GiB、主机4GiB可用、磁盘20GiB与新增OOM停止条件不变。清理阶段监控只读procfs/cgroup，避免Docker状态查询阻塞采样，并持久化清理期异常。
9项保护/归属/异常清理测试、真实小型父子进程清理测试、原资源曲线重放通过。所有更改仅在独立编排层；旧目录、旧中止记录完整保留。
直接复用原单篇适配脚本的extract_results与原版ResultsExtractor；固定原AxCell源码、模型、taxonomy、abbreviations、置信度0.8/0.85及候选筛选。仍为每篇空初始Elasticsearch索引，保持已验收单篇设置；不预索引其他论文，官方查询参数不变。作者实际索引语料未核实，作为复现限制保留。

## 逐篇状态

| 论文ID | 状态 | 原始记录数 | 文本/表格区域 | 本次秒数 | 退出码 | 说明 |
|---|---|---:|---|---:|---|---|
| 1911.10390.pdf | EXTRACTION_COMPLETE | 6 | 98/6 | 0 | 0 | 复用，不重复生成 |
| 2001.04063.pdf | EXTRACTION_COMPLETE | 3 | 92/6 | 0 | 0 | 复用，不重复生成 |
| 1905.03197.pdf | FAILED | — | —/— | — | — | processing-error |
| 1912.08777.pdf | VALID_EMPTY | 0 | 144/43 | 215.73 | 0 | 本次授权重试一次 |
| 1906.05012.pdf | VALID_EMPTY | 0 | 89/8 | 55.33 | 0 | 原版抽取 |
| 2203.16804.pdf | FAILED | — | —/— | — | — | processing-error |
| 1910.13461.pdf | EXTRACTION_COMPLETE | 2 | 112/7 | 55.288 | 0 | 原版抽取 |
| 1908.08345.pdf | EXTRACTION_COMPLETE | 2 | 98/7 | 75.595 | 0 | 原版抽取 |
| 1808.08745.pdf | VALID_EMPTY | 0 | 99/8 | 45.129 | 0 | 原版抽取 |
| 2020.findings-emnlp.378.pdf | EXTRACTION_COMPLETE | 1 | 69/11 | 303.07 | 0 | 原版抽取 |
| 1809.08370.pdf | EXTRACTION_COMPLETE | 5 | 175/7 | 110.122 | 0 | 原版抽取 |
| 1806.03489.pdf | EXTRACTION_COMPLETE | 2 | 104/7 | 34.994 | 0 | 原版抽取 |
| 1702.02098.pdf | EXTRACTION_COMPLETE | 1 | 117/8 | 59.316 | 0 | 原版抽取 |
| 1511.08308.pdf | EXTRACTION_COMPLETE | 2 | 154/11 | 0 | 0 | 复用，不重复生成 |
| 2020.emnlp-main.523.pdf | EXTRACTION_COMPLETE | 2 | 119/12 | 73.552 | 0 | 原版抽取 |
| 2105.03654.pdf | EXTRACTION_COMPLETE | 4 | 102/8 | 45.107 | 0 | 原版抽取 |
| 1903.07785.pdf | EXTRACTION_COMPLETE | 4 | 97/6 | 63.393 | 0 | 原版抽取 |
| D18-1279.pdf | EXTRACTION_COMPLETE | 2 | 93/4 | 55.253 | 0 | 原版抽取 |
| 1703.06345.pdf | EXTRACTION_COMPLETE | 3 | 74/3 | 51.222 | 0 | 原版抽取 |
| 1603.01354.pdf | EXTRACTION_COMPLETE | 3 | 125/9 | 101.999 | 0 | 原版抽取 |
| 1709.04109.pdf | EXTRACTION_COMPLETE | 1 | 101/10 | 95.934 | 0 | 原版抽取 |
| 2008.07772.pdf | EXTRACTION_COMPLETE | 1 | 83/4 | 47.139 | 0 | 原版抽取 |
| 1911.09483.pdf | EXTRACTION_COMPLETE | 1 | 86/5 | 49.185 | 0 | 原版抽取 |
| 1901.10430.pdf | EXTRACTION_COMPLETE | 3 | 136/7 | 37.006 | 0 | 原版抽取 |
| 2002.03184.pdf | EXTRACTION_COMPLETE | 1 | 66/7 | 69.492 | 0 | 原版抽取 |
| wang19f.pdf | VALID_EMPTY | 0 | 58/5 | 53.241 | 0 | 原版抽取 |
| 1804.09849.pdf | EXTRACTION_COMPLETE | 1 | 124/6 | 55.268 | 0 | 原版抽取 |
| D18-1523.pdf | EXTRACTION_COMPLETE | 2 | 67/5 | 24.821 | 0 | 原版抽取 |
| 1905.12598.pdf | VALID_EMPTY | 0 | 73/5 | 22.792 | 0 | 原版抽取 |
| 1811.09242.pdf | VALID_EMPTY | 0 | 84/7 | 73.292 | 0 | 原版抽取 |
| 1812.10235.pdf | EXTRACTION_COMPLETE | 2 | 59/2 | 22.797 | 0 | 原版抽取 |
| 2020.emnlp-main.152.pdf | VALID_EMPTY | 0 | 36/3 | 51.205 | 0 | 原版抽取 |
| 1909.02188.pdf | EXTRACTION_COMPLETE | 4 | 94/4 | 75.57 | 0 | 原版抽取 |
| 1907.00390.pdf | EXTRACTION_COMPLETE | 1 | 38/3 | 30.907 | 0 | 原版抽取 |
| 1812.09471.pdf | EXTRACTION_COMPLETE | 4 | 86/3 | 22.779 | 0 | 原版抽取 |
| N19-1373.pdf | EXTRACTION_COMPLETE | 1 | 73/5 | 32.949 | 0 | 原版抽取 |
| K19-1036.pdf | VALID_EMPTY | 0 | 60/3 | 32.949 | 0 | 原版抽取 |
| 1811.05021.pdf | VALID_EMPTY | 0 | 115/4 | 22.786 | 0 | 原版抽取 |
| 1711.05568.pdf | EXTRACTION_COMPLETE | 1 | 112/7 | 43.123 | 0 | 原版抽取 |

## 资源与完整性

本次批次墙钟36.81分钟（不含前置配置与最终同步）。本次新增尝试34；累计阶段3尝试37（含上轮1次保护中止），另有原单篇成功生成1次。未自动重试失败或因低分重跑。
模型OS maxRSS最高5.936GiB，模型cgroup采样峰值4.042GiB，ES采样峰值1.310GiB。不同口径/时点不可相加作总峰值。最低MemAvailable 23.615GiB，结束28.906GiB。
OOM增量0，swap-in/out增量0/0。磁盘剩余55.803→55.742GiB（整盘变化含后台写入）。
哈希核验：本地冻结1990文件、远端冻结2476文件，643个解析产物、91个源码/模型文件；详情见stage3_verification.json。3篇复用结果逐文件与旧输出一致。依赖版本无变化。
旧中止不计入成功输出。VALID_EMPTY为流程成功的空预测，与程序FAILED和未运行BLOCKED分开。两篇解析失败保留，未静默排除。原预测及raw_outputs/events全部保留，未根据Gold筛选或修改。

## 输出与后续边界

extraction_status.csv、extraction_manifest.json、resource_usage.csv、resource_summary.json、stage3_verification.json；逐篇原始输出、provenance、中间候选、stdout/stderr、资源采样在remote_results/papers/<paper_id>/。预处理输入只复用，未重新解析。错误来源核查另见error_inspection.md。
有非空原始记录的28篇可在P3验收后进入标准化请求准备；VALID_EMPTY 9篇保留状态与分母，不虚构请求。标准化必须另经P4授权，固定gpt-4.1-2025-04-14。本轮到此停止。
远端目录：/root/scilead/axcell/runs/20261022_stage3_resume/；报告镜像在reports/。保留ECS及Docker daemon，不自动关机或新增云资源。
