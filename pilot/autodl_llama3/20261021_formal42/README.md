# SCILEAD Llama-3 70B：经批准的42篇正式实验

本目录与历史 GPT、smoke、20261021_diagnostic 隔离。范围是42篇、259 Gold、27榜131条，不是完整43篇复现。审批原文及批准的格式实现 SHA 见 `approval.json`。

## 范围与方法

- 模型为官方 Meta-Llama-3-70B-Instruct，revision `50fd307e57011801c7833c87efa1984ddf2db42f`。
- 作者4-bit FP4、模型bfloat16、量化计算float32、greedy、seed0。Extraction/名称标准化/排行榜对齐的 `max_new_tokens` 分别为1024/15/100。
- 模型自带的默认generation_config与实际调用参数分别记录；判断greedy应查看pipeline_forward_params及每次request中的`do_sample=False`，不能把未生效的模型默认temperature/top_p当成本轮采样设置。
- 原生8192上下文；`1912.08777.pdf` 的55324输入Tokens无法原样运行。未截断、未改RoPE、未换模型、未重做PDF解析、MPNet证据Embedding或Chroma检索。CS名称标准化所需的独立双语Embedding正常执行。
- 四篇原始响应直接复用；固定其余38篇各生成一次。队列和每篇Prompt哈希在 `config/extraction_queue.json`。
- 只使用批准的格式规则v1；数组内部逐字符不变，重复项与数值保留。Result类型转换由原版标准化完成。
- 候选集合来自完整43篇Gold（23/71/26），Partially掩码也基于完整原始27榜。当前论文Gold对应答案不进入抽取Prompt。
- `PYTHONHASHSEED=0`；使用固定输入键顺序。作者历史论文处理顺序不可确认，不能宣称完全相同。
- 原版规范化 `answer[2:]`、精确候选判断、动态新增条件、null、CS top1及评价公式均未修改。
- GPT此前采用无客户端输出上限；本轮Llama保持作者预算，这一配置差异不会隐藏。

## 文件分层

- `remote_snapshot/extraction/<论文>/extraction/`：新增真实原始生成；`raw/`：四篇历史生成的原样副本。
- `remote_snapshot/extraction/<论文>/prepared_output.json`：仅经过已批准格式协议的标准化输入。
- `remote_snapshot/extraction/raw_output.json`：保留所有生成结果，包括无效JSON。
- `remote_snapshot/extraction/prepared_output.json`：仅可解析的真实输入，没有失败空预测。
- `remote_snapshot/normalization/`：真实官方标准化输出、逐字段候选顺序、原始响应、调用统计。
- `evaluation/*/evaluation_input_fixed42.json`：独立评价副本。失败论文在此记空列表以固定42篇分母，并在coverage中明确列出；不回写原始结果。
- `evaluation/*/eval_results.json`、`eval_values.json`：原版指标；`metrics_with_f1.json` 为官方Macro P/R派生F1。
- `strict_numeric_auxiliary.json`：额外严格数值检查，不能替代官方字符串包含匹配。
- `leaderboard_official.json`：原版PC/RC/数值RBO；`leaderboard_supplementary.json`：精确TDM LR、有效非空榜率、独立论文ID AO。
- `remote_snapshot/reproducibility/`：原始响应离线重放官方main，检查输出一致，没有新模型生成。

旧适配器带有“Result必须已经是字符串”的更严格检查，也会将中性前缀记为解析错误；它的进程退出码不单独决定正式结果。正式判据使用实际生成完成记录、EOS及本轮批准的格式规则。原退出码和原校验JSON仍保留，不为绕过旧校验重复生成。

## 远程任务和断点

远程根目录：`/root/autodl-tmp/scilead/runs/llama3/20261021_formal42`。
使用已有独立环境 `/root/autodl-tmp/scilead/envs/llama/bin/python`，不使用Base环境。

本轮所有推理阶段已经结束；**不要重复执行启动命令**。42篇均取得原始响应，40篇格式有效，两个失败状态保留。`launch.json` 与 `partial_launch.json` 记录实际进程；`.batch.lock`、`.followup.lock`、`.partial.lock` 避免重叠任务。

状态读取：本地使用已有SSH客户端环境运行 `scripts/session.py status`；详细只读检查为 `scripts/session.py script --file scripts/inspect_progress.py`（传绝对路径）。连接沿用已核验主机指纹，不输出凭据。

每次生成先保存 `request.json`；随后保留完整pipeline返回、`response.txt`，最后写入 `complete.json`。只有complete存在且输入、响应SHA完全匹配，才允许在恢复时读取已有结果。存在请求但无完成标记时阻止重复生成，必须先检查实际状态；失败或低分不构成重新生成理由。

若进程中断，先确认原进程不在运行，再检查所有不完整请求。不得删除检查点来绕过保护。Extraction编排可以在确认后恢复：已完成生成仅重新读取；未完成请求保留BLOCKED。正式标准化恢复时会按原顺序重放已完成响应以重建动态集合，不重新调用这些字段；遇到不完整请求会再次停止。

CS采用已验证的固定本地权重副本、CPU FP32。先比较三类历史相似度和top1结果；正式执行调用未修改的 `tdm_embedding_normalization.main`。保存逐篇完成标记，成功论文不重复计算。没有发现旧实验持久化embedding缓存，旧GPT名称映射不能冒充Llama预测。

`scripts/remote_followup.py` 只等待依赖阶段，不重试模型。Fully失败、CS验证失败或Partially异常均停止后续依赖步骤。运行完成不自动关机或调整AutoDL计费。

## 评价与最终报告

本地原环境运行 `scripts/evaluate_scope.py`，随后 `scripts/finalize.py`；均不生成模型响应。评价保留全部42篇分母并另报有效覆盖，27榜空榜记0。F1取官方Macro P/R的调和平均。

GPT参考来自冻结输出在相同42篇评价范围的离线筛选；特别是Partially的历史43篇动态更新过程未重新执行，不能视为完全相同的状态轨迹。

原论文43篇/295 Gold/140榜内条目仅作并列参考。Partially原文元组表未唯一绑定到具体阶段JSON，因此保留两个阶段，不选择较高值来对应原文。

本轮只执行批准的A/B/C/D/E；Cold Start、threshold=2及其他模型不在范围内。

本地最终报告入口为 `run_report.md`，最终索引为 `experiment_manifest.json`。远程交付副本位于上述远程根目录的 `delivery/`，由 `DELIVERY.md` 指向最终报告；远程原始执行目录及初始manifest保留。`delivery_transfer_verified.json` 记录交付文件逐项SHA256核验结果。
