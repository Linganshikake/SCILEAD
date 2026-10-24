# AxCell ECS 单篇分阶段资源验证

实验名称：**AxCell Extraction + GPT-4.1 Fully Normalization**。本轮只执行前半段的单篇 CPU 验证，已完成并停止；GPT Normalization、SCILEAD Evaluation、39 篇批量均未执行，付费 API 调用为 0。

## 实际完成范围

在阿里云 ECS `/root/scilead/axcell` 使用冻结源码 `f4648d8fee1aa8482d007a38828da9dc06630f0e`、原版 7 个模型文件与固定 Engrafo/Elasticsearch 镜像，完成 `PaperExtractor → ResultsExtractor`。论文固定为 `1511.08308.pdf`（TeX `1511.08308v5`，Named Entity Recognition with Bidirectional LSTM-CNNs），延用先前按输入可用性选定的清单，没有按得分挑选。

只传输了这一篇既有 TeX，没有重新下载 39 篇 TeX 或 AxCell 模型。39 是本地取得的输入数，**原论文 36 篇 AxCell 子集的成员关系仍未核实**。

## 环境与保护条件

ECS 实测 Ubuntu 22.04.5、8 vCPU、30.689 GiB RAM；无 swap。使用已有 Docker Engine 29.9.2，未改全局 Docker 配置。80 GiB 系统盘挂载 `/`、ext4；无独立数据盘。结束时可用 RAM 28.939 GiB、磁盘余量 56.161 GiB。

执行环境为 `/root/scilead/axcell/envs/axcell-original`：Python 3.7.1、PyTorch 1.3.1+cpu、torchvision 0.4.2+cpu、NumPy 1.18.1、fastai 1.0.55、spaCy 2.2.3、fastprogress 0.1.21。官方所有显式版本约束通过核对；torch/torchvision 使用相同版本的官方 CPU 构建。最终 `pip check`：`No broken requirements found.`

启动门槛为实际执行主机可用 RAM ≥6 GiB、磁盘工作余量 ≥20 GiB。运行保护：可用 RAM 连续 15 秒低于 2 GiB、任务容器连续 15 秒达到限额 95%、OOM、手动停止标记或阶段超时，保存日志后只停止任务所属进程/容器。转换容器上限 20 GiB/6 CPU、网络关闭；ES 上限 3 GiB/2 CPU、JVM heap 1 GiB、只绑定 127.0.0.1。转换容器退出后才启用 ES。模型计算为 CPU，OMP/MKL 线程为 6。

本轮实际运行在 ECS，未启动 Windows WSL/Docker，未修改本机 WSL、swap 或分页配置；不能把 ECS 的内存测量当成 Windows 本机测量。

## 分阶段实测

| 阶段 | 完成情况 | 进程内存 / 容器采样峰值（GiB） | 耗时 | 产物或错误 |
| --- | --- | --- | --- | --- |
| TeX 转换及解析 | 完成，exit=0 | 进程组采样 0.119；子进程 maxRSS 0.141；容器 /axcell-single-convert: 0.275 | 27.37 秒 | 154 文本片段、11 区域 |
| ES 首次启动 | 完成，exit=0 | 进程组采样 0.022；子进程 maxRSS 0.032；容器 /axcell-single-es: 1.232 | 12.22 秒 | 6.7.1，127.0.0.1:9200 |
| 首次模型初始化 | 失败，exit=1 | 进程组采样 0.007；子进程 maxRSS 0.437；容器 /axcell-single-es: 1.232 | 3.64 秒 | 空进度条除零；未生成预测 |
| ES 受控恢复 | 完成，exit=0 | 进程组采样 0.021；子进程 maxRSS 0.032；容器 /axcell-single-es: 1.238 | 12.21 秒 | 原服务恢复，确认索引为空 |
| 模型抽取与退出清理 | 完成，exit=0 | 进程组采样 3.651；子进程 maxRSS 4.813；容器 /axcell-single-es: 1.304 | 74.05 秒 | 2 条原始预测，服务正常停止 |

成功抽取内部计时：模型加载 4.643 秒，实际推理 65.271 秒。内存峰值在模型抽取阶段：OS 记录的子进程最大 RSS 为 4.813 GiB；3 秒采样的任务进程组 RSS 最大为 3.651 GiB。两者口径不同，不可互相替代。ES 在该阶段采样峰值为 1.304 GiB；与模型数值不构成精确的同步总峰值。

容器内核没有提供 `memory.peak`，因此表中容器数据是采样峰值，不是精确峰值。进程组 RSS 相加可能重复计算共享页。整个模型阶段最低主机 MemAvailable 为 24.167 GiB；所有实验阶段 OOM 计数和 swap-in/out 增长均为 0。ES 退出码 143 来自正常 SIGTERM 停止，Docker stop 返回 0，非 OOM。

## 解析及原始预测

解析产物为 154 个文本片段、11 个 table/tabular 区域，其中包含原解析器输出的 Figure 4 区域，未人工删改。表格分类为 {'IRRELEVANT': 5, 'ABLATION': 4, 'SOTA': 2}。原版过滤流程从 179 个候选，经结构过滤 128、第一层置信度过滤 121、BestResult 2、最终置信度过滤保留 2 条。

| Task | Dataset | Metric | Result | 原版 model 字段 | 来源 |
| --- | --- | --- | --- | --- | --- |
| Named Entity Recognition | CoNLL 2003 (English) | F1 | 91.85 | BLSTM-CNN + emb + lex | 1511.08308v5/table_06.csv/6.2 |
| Named Entity Recognition | Ontonotes v5 (English) | F1 | 4696.0 | Test set size (# entities) | 1511.08308v5/table_11.csv/2.4 |

以上是未经人工修改的模型返回结果。JSON/CSV/PKL、原始单元格、过滤事件及 provenance 均保留；SCILEAD 兼容文件只映射字段名并把 Result 转为字符串。`source_documents=[]` 明确表示这里使用 AxCell 表格单元格来源，并未引入 PDF Retriever。

输出后的原表复核发现：

- `table_06.csv/6.2` 的 91.85 对应 CoNLL-2003 的 **Recall** 列，原模型却绑定到 F1；该行 F1 实际列为 `91.62 (+- 0.33)`。这是指标/数值绑定错误，保留预测 91.85。
- `table_11.csv/2.4` 的 4,696 是 NW 类别的 **Test set size (# entities)**，被保留为 Ontonotes F1=4696.0。数据集统计行被当成实验结果，同时丢失细分列语义。原记录不删不改。

上述核对只用已解析表格，不读取该论文 Gold 答案，不计算准确率。两条预测不等于两条正确结果。模型完成后没有为改善质量再次推理。

## 工程问题及处理

1. 旧版依赖与跨境下载：固定镜像及官方软件包传输慢、部分超时，保留各次退出状态和缓存，有限续传。GitHub/PyTorch/PyPI 官方文件通过本地 HTTPS 与 SSH 转送；PyPI 下载产物逐项与官方 SHA256 校验，临时转发已关闭。没有替换模型或浮动镜像。
2. 官方显式依赖版本保留，初次求解出的 7 个未固定传递依赖不兼容旧 Docker SDK/IPython/Compose 或 awscli；只在独立环境中作如下调整，没有使用 `--no-deps`，最终依赖检查通过。

| 未固定的传递依赖 | 初次求解 | 最终兼容版本 |
| --- | --- | --- |
| colorama | 0.4.6 | 0.4.4 |
| jsonschema | 4.17.3 | 3.2.0 |
| prompt-toolkit | 3.0.48 | 2.0.10 |
| pyyaml | 6.0 | 5.4.1 |
| requests | 2.32.2 | 2.31.0 |
| urllib3 | 2.2.1 | 1.26.20 |
| websocket-client | 1.6.1 | 0.59.0 |

3. Docker SDK 4.1.0 与 Engine 29.9.2 的协议协商，通过独立适配层设置 `version=auto`；源码不变。转换调用同样只附加任务标识、CPU/内存/网络保护。
4. 首次模型初始化因 `fastprogress 0.1.21` 对空序列绘制进度条除零而失败，尚未进入论文推理。保留首次日志，在独立适配层仅跳过 total=0 的控制台绘制；空/非空迭代等价性已验证。第二次初始化使用新目录 `attempts/console_progress_compat`，只进行一次成功推理。没有更换框架、权重、阈值或输入。
5. 原版权重加载出现 PyTorch `SourceChangeWarning`，警告完整保留；未改权重或生成补丁。当前验证不宣称与原作者运行环境逐位一致。

## 完整性与停止状态

远端 91 个源码/输入/模型/启动文件与传输清单 SHA256 全部一致；本地 91 个原源码、模型、模型压缩包及选定 TeX 与已有清单一致；同步的 192 个远端报告文件逐一校验大小和 SHA256。官方环境文件未改。D 盘历史 SCILEAD 冻结结果、Gold、Prompt 和 E 盘原始实验资源未写入；本轮未重新计算全部历史实验文件哈希，不作超出审计范围的声明。

任务容器已全部停止，转换容器由原调用自动移除；没有运行中的任务 tmux/进程，临时 PyPI 转发监听已关闭。保留已有 Docker daemon、镜像、模型、环境和 ES 数据；未关机或更改云实例。后续批量和付费调用均仍需确认。

## 资源判断和下一步边界

**ECS 已满足这篇论文的完整 CPU 流程，适合把串行处理作为后续验证方向；一篇不足以证明全部输入的峰值和稳定性。** 当前内存余量充足，未发现需要扩容或 swap 的依据。若后续获得批量授权，应继续逐篇隔离、相同资源保护、成功产物跳过，先核对 39 个来源版本及与作者 36 篇子集的关系。

本机 16 GiB Windows 未在本轮重新验证。已观测模型子进程峰值约 4.81 GiB，另有 ES 约 1.30 GiB 及 WSL/Docker/系统开销，原先 6 GiB 仅是启动保护，不能据此承诺本机串行稳定；本轮不建议仅调高 WSL 限额来认定物理内存问题已解决。

在依赖和镜像已准备好、同等复杂度的假设下，本篇转换+模型加载+推理+一次 ES 启动约 107.6 秒。纯线性外推 39 篇约 70.0 分钟，仅作粗略参照，未包含下载、失败排查、复杂表格差异、Normalization 和评价，不能作为可靠批量工期。后续 GPT Fully Normalization 固定 `gpt-4.1-2025-04-14`，必须先提交实际待映射字段请求量与费用估算，再等待授权。

## 文件入口

- 本地报告目录：`D:\C++\SCILEAD\pilot\axcell_aliyun\20261022_single_paper`。
- 远端运行目录：`/root/scilead/axcell/runs/20261022_single_paper`。
- `manifest.json`：论文与输出索引；`final_config.json`：实际配置和兼容性差异。
- `remote_reports/attempts/console_progress_compat/raw_outputs/records.json`、`records.csv`、`records.pkl`：原始预测；同目录 `provenance.json`、`pipeline_events.json`：来源及过滤记录。
- `remote_reports/attempts/console_progress_compat/scilead_compatible_outputs/output.json`：只作字段格式映射，未标准化。
- `parsed_paper/`、`parsed_html/`：原解析产物；`output_inspection.json`：离线错误定位。
- `resource_summary.json`、`verification.json`、`local_asset_integrity.json`、`report_sync_manifest.json`：资源与完整性证据。
- `remote_reports/dependency_freeze.txt`、`conda-explicit.txt`、`dependency_pin_verification.json`、`pip_check_final.txt`：环境记录。

单篇阶段完成后停止；没有自动启动批量、GPT 标准化或其他模型实验。
