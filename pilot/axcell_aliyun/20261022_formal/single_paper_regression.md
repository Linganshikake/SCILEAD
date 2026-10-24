# P1：AxCell 单篇回归验收

阶段 1 已通过，停在 **P1，等待确认后才进入阶段 2**。执行主机为阿里云 ECS；本轮只复用 `1511.08308.pdf` / `1511.08308v5`，没有新转换、模型权重加载、预测生成或 GPT 调用。

## 回归结果

从未经修改的既有 `scripts/run_single.py` 导入 `collection()`，实际调用原版 `PaperCollection.from_files(jobs=1)` 读取文件。读回的标题、154 个文本片段、11 个 table/tabular 区域及全部表格单元格，与原 `parsed_artifacts.json` 一致。此处没有重新解析 HTML/TeX。11 个区域仍包含原解析器输出的 Figure 4，不人工删除。

JSON、CSV、PKL 的两条记录一致；SCILEAD 包装中的论文 ID、字段映射和 Result 字符串一致，`source_documents=[]` 保持原样，AxCell 的来源另存 provenance。374 条既有 pipeline 事件可读，最终过滤的两个单元格 ID 与返回记录对应。读取检查进程临时禁止网络连接与 `torch.load`，只读产物不依赖模型加载或外部调用。

| 记录 | 原始 Task / Dataset / Metric / Result | 原始来源 | 离线核查结论 |
|---|---|---|---|
| 1 | Named Entity Recognition / CoNLL 2003 (English) / F1 / 91.85 | `table_06.csv/6.2` | 对应表头是 Recall；指标绑定错误仍保留 |
| 2 | Named Entity Recognition / Ontonotes v5 (English) / F1 / 4696.0 | `table_11.csv/2.4` | 原文为 Test set size (# entities)，属于 NW 列实体数；统计量误抽仍保留 |

这些核查只读取原表及既有输出，不用 Gold 修正或重新生成结果。流程与文件一致性通过不代表两条预测正确。

## 固定配置与完整性

- AxCell commit：`f4648d8fee1aa8482d007a38828da9dc06630f0e`；SCILEAD commit：`8bf74b0a830feb7035c6166dce3394dc344ae532`。
- TeX v5 SHA256：`e0483008622131070662aafc040258a8fe97f50d7039cea85c6f690473625aea`。
- 原始 records.json SHA256：`c7ae025fb281d86eb97d241aafc2b7257763dfad38248bf9fa54362ca8b5005b`。
- Engrafo、Elasticsearch 的固定镜像 ID/digest 不变；7 个模型、taxonomy、abbreviations、tokenizer 文件 SHA256 不变。
- 依赖无差异，`pip check` 通过。Python 3.7.1、PyTorch 1.3.1+cpu、fastai 1.0.55 保持不变。
- 原阈值保留：表类型 0.5；结构筛选 → 置信度 0.8 → paper 范围 BestResult → 置信度 0.85；CPU、`use_crf=False`、OMP/MKL 6 线程。原显示兼容适配不变。
- 前后复核远端 91 个源码/输入/模型/启动资产、46 个脚本/解析文件、192 个历史报告文件；本地 353 个保护文件及 28 个 P0 交付文件，全部匹配。既有 GPT/Llama 比较输入索引哈希亦匹配。没有宣称重新哈希全部历史实验资源。

## 本轮资源测量

启动保护为可用 RAM ≥6 GiB、磁盘保留 ≥20 GiB；连续 15 秒可用 RAM <2 GiB 或容器使用率 ≥95%、OOM、超时均停止本任务。使用 tmux、独占锁和单次 attempt 标记；失败不会自动重跑。

| 检查阶段 | 结果 | 内存 | 耗时 | 产物/状态 |
|---|---|---|---|---|
| 既有产物读回与结构回归 | 通过，exit=0 | 子进程 OS maxRSS 0.186 GiB | 子进程 0.938 秒；监控包络 2.011 秒 | 154 片段、11 区域、2 条原始记录一致 |
| ES 6.7.1 服务启动 | 通过，exit=0 | 生命周期 cgroup 采样峰值 1.262 GiB / 3 GiB 限额 | 10.385 秒 | 仅监听 127.0.0.1:9200 |
| ES 健康与空闲观察 | green，空索引 | JVM heap 1 GiB；2 CPU | 15.183 秒 | 独立 P1 数据目录，没有索引论文 |
| 正常停止 | Docker stop exit=0 | 容器已停止 | 0.565 秒 | 容器 exit=143（SIGTERM），OOMKilled=false |

ES 容器进程树 RSS 采样峰值为 1.277 GiB，与 cgroup 使用量口径不同，不相加。内核未暴露 `memory.peak`，报告的是采样峰值；读取子进程不足一秒，使用其 OS maxRSS，不能拿较低的周期采样值代替。

运行总计 28.221 秒，15 个资源采样点；主机最低 MemAvailable 27.681 GiB。阶段结束再次复测可用 RAM 28.929 GiB，磁盘剩余 56.160 GiB。OOM、swap-in/out、major page fault 计数增长均为 0；服务器无 swap。

本轮独立 ES 数据目录表观大小 16,595 字节；前后全盘可用空间变化 0.539 MiB，这个系统级差值包含日志等背景写入，不作为精确任务占用。没有安装依赖、下载镜像、扩容或修改系统配置；使用的是既有付费 ECS，本轮新增 GPT 请求为 0。

为保护历史索引，新建 `axcell-formal-p1-es`，只挂载 `.../20261022_formal/stage1/elasticsearch_data`；原 `elasticsearch-single` 未挂载、原容器未启动且元数据不变。新容器、日志和隔离数据保留供复核；所有容器已停止，9200 端口关闭，任务 tmux 已结束，Docker daemon 保持此前状态。

## 证据边界与下一阶段

本轮证明已有产物可复用、固定环境可读取结果以及服务可正常启动停止，**没有重新测量模型推理峰值或批量稳定性**。历史唯一成功推理耗时 65.271 秒、模型子进程 maxRSS 4.813 GiB 是上一轮记录；本轮没有把它计为新运行。此前初始化的 fastprogress 空进度条错误日志仍保留，显示兼容方案未变。

原作者 36 篇的确切成员与 TeX 版本仍未核实。39 篇可用 TeX 对应 283 条 Gold，不能称为作者 36 篇范围。前次确认只授权本阶段，正式评价口径仍须明确；不根据当前两个错误选择或排除论文。

若确认进入阶段 2，将沿用冻结清单，复用本篇转换产物、串行处理其余 38 篇的 TeX 转换与解析，保留失败状态，并停在 P2。阶段 2 不运行 AxCell 模型抽取、不调用 GPT。本报告不授权越过 P1，也不自动启动批量。

## 文件

- `single_paper_verification.json`：结构、配置、哈希与停止状态。
- `single_paper_resource_usage.csv`：逐采样资源明细。
- `stage1_gate.json`：当前 P1 待确认状态；P0 manifest/gate 保持历史快照。
- `stage1/remote_reports/`：实际运行脚本、原始日志、容器 inspect、资源 JSONL、读回检查。
- `stage1/remote_before.json`、`remote_after.json`：前后只读核验。
- 远端：`/root/scilead/axcell/runs/20261022_formal/stage1/`。
