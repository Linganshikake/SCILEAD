# GPT-5.6 Sol：Fully + CS、Partially、Cold Start

本目录只复用已冻结的43篇、335条Extraction记录；Gold为295条、27个排行榜。没有重新解析PDF、检索证据或生成Extraction。正式配置见`experiment_manifest.json`和`generation_config.json`。

## 结果位置

- `实验结果汇总.md`：中文总报告，仅以最终verification状态判断是否全部完成。
- `report.md`：两阶段完整P/R/F1、all27与masked10排行榜指标和历史对照。
- `fully_cs/`：CPU执行的原版CS名称标准化及评价。
- `partially/`：原版部分预定义名称标准化；第一阶段名称映射，第二阶段排行榜TDM映射。
- `cold_default/`、`cold_0/`、`cold_42/`：默认顺序及字符串种子`"0"`、`"42"`的独立Cold Start运行。
- 每个LLM分支的`stage1/`、`stage2/`保留请求、响应、候选顺序、官方逐字段决策和检查点；`evaluation/`保存相应阶段评价。
- `request_audit.csv`与`api_usage_summary.json`：实际请求审计；包括失败及经批准的额外尝试。
- `verification.json`：最终范围、输入、原版代码、冻结历史文件完整性检查。

## 设置与方法边界

真实请求使用`gpt-5.6-sol`、`reasoning_effort=medium`、`max_completion_tokens=32768`、`stream=false`，与已成功的GPT56 Fully配置一致。不发送temperature、seed、tools或response_format。代码内部方法seed与PYTHONHASHSEED均为0。

原版代码中的`gpt4-turbo-128k`仅用于选择原版消息角色和处理分支；独立传输层实际发送GPT56。官方源码、Prompt、接受规则和候选生成方式不变。每个独立字段按原版逻辑请求，未引入语义缓存；断点恢复只重放同一次已保存的响应，不合并重复字段。

## 断点恢复

必须先核对进程是否已退出。相同分支具有操作系统文件锁，禁止同时启动两份。命令格式：

```powershell
$env:PYTHONHASHSEED='0'
& 'D:\miniconda3\envs\scilead\python.exe' -X utf8 -B '.\variant_runtime.py' --branch partially
```

在本目录运行，branch可选partially、cold_default、cold_0、cold_42。完整阶段校验后跳过；阶段内从头按原顺序重放已落盘响应，验证请求、响应哈希和动态候选状态，再继续未执行字段。该命令具有真实请求能力，不能当成离线状态检查。

失败或未知状态默认阻止重发。本轮用户明确批准的例外单独保存于对应请求的`retry_authorization.json`，额外尝试仅在`retry_1/`中保存。再次失败不发第三次。原失败状态和响应不会覆盖。恢复后的`accepted.json`引用实际成功响应路径，不意味着最初的失败尝试成功。

Windows临时文件占用仅对相同内容的文件写入做有限重试；不改变HTTP自动重试次数（始终为0）。日志、审批和测试证据保存在`engineering/`。

## 离线评价

所有分支完成后，使用同一Python与PYTHONHASHSEED：

```powershell
python -X utf8 -B evaluate_variants.py --branch all
python -X utf8 -B summarize_variants.py
python -X utf8 -B finalize_experiment.py
```

评价保持43篇分母，不把未完成阶段视为零分或忽略后称全量完成。官方Macro P/R之后计算F1。名称标准化和排行榜TDM映射的结果分别报告；all27与masked10不可混用。官方数值列表RBO、论文ID AO和严格数值辅助诊断分别标注。

本目录不自动启动Mixtral、其他模型或新实验，也不自动发布到GitHub。
