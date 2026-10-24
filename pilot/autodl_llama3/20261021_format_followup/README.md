# SCILEAD Llama-3 format follow-up

本轮授权来源为用户附件c55aad55-df3e-4ab2-8068-e5519c5c334b。正式42篇V1目录保持不变。

## 结果入口

- `reports/run_report.md`：总报告，先区分两篇恢复情况。
- `format_v2/comparison_v1_v2.md`：固定42篇/259 Gold、27榜/131条的完整P/R/F1及排行榜配对比较。
- `token2048_diagnostic/diagnostic_report.md`：唯一新增Extraction及独立单篇评价。
- `reports/verification.json`：受保护文件、请求复用、范围、传输及脱敏核验。
- `remote_snapshot/`：远程原始执行文件的逐项哈希校验副本，包含每次新生成和全部复用事件。

## 输入与协议

V2规则及19项边界测试在`parser_v2/`，先冻结哈希再评分。只恢复已有内容：10条完整多数组记录按原序合并；原40篇保持完整文本及记录不变。截断在记录内部的2105.03654.pdf不被V2修复。

2048诊断使用相同Prompt、证据、模型、4-bit量化、dtype、greedy和seed，唯一生成变更为max_new_tokens1024→2048。不得将它混入V2主结果。

Partially按原顺序离线重建候选状态，复用匹配键包含论文/行/字段位置、原始行、部分规范化行、完整候选序列及其序列化、实际Prompt、模型与所有请求参数；不是名称缓存。原本相同名称的不同位置仍分别处理。

## 断点与执行边界

远程根目录：`/root/autodl-tmp/scilead/runs/llama3/20261021_format_followup`。脱离终端的独立会话、`.workflow.lock`、launch标记和逐调用request/complete检查点共同避免重复请求。

不要再次执行`transfer.py start`，它会拒绝已有launch。完成状态以逐阶段done/complete及最终verification为准，失败日志不删除。存在request但没有complete时，先人工核查；不删除检查点绕过保护。

若确需恢复，必须先核对输入、冻结解析器与配置哈希，并确认原进程已结束。官方阶段从头重放以重建动态集合；历史精确匹配响应及本轮已完成new_calls都由检查点读取，不重新生成。用户若改变输入或协议，应创建新目录，而不是沿用done标记。

CS首次缺少离线自定义代码缓存，错误发生在新增映射前。`cs_repair_runner.py`只将同revision的两份代码加入本轮缓存；旧日志及两次完成状态分别保存，不修改原流程失败记录。没有下载模型、升级依赖或修改方法。

本地原环境运行`evaluate_followup.py`及`finalize_followup.py`只作离线评价和报告。复制、冻结文件哈希及真实调用记录才是复核依据，不凭脚本退出码或正常EOS推断结构有效。

远程最终交付报告位于`delivery/`；原始推理和日志仍在远程根目录。没有自动关机或更改计费。
