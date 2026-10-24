# SCILEAD Llama-3 70B 本轮执行报告

**已完成三篇单次诊断，正式实验尚未启动。** 3/3成功生成并EOS，1/3原响应可直接作为JSON输入；另2篇的唯一完整数组可按候选规则保留，但该规则等待用户确认。生成成功、语法有效、完成评价、达到原论文性能分别记录，不能等同。

## 真实输出

| 论文（末行为历史） | 输入 | 输出 | 结束 | 原始JSON有效 | 数组候选条数 | Result类型 | 保留重复条数 |
|---|---:|---:|---|---|---:|---|---:|
| D18-1105.pdf | 1460 | 62 | eos | 是 | 2 | str | 0 |
| 2203.16804.pdf | 4038 | 482 | eos | 否 | 13 | float | 0 |
| 1511.08308.pdf | 4661 | 445 | eos | 否 | 12 | float | 1 |
| 2020.findings-emnlp.378.pdf | 4226 | 205 | eos | 否 | 6 | float | 0 |

| 本轮论文 | 纯生成秒 | 子进程总秒 | GPU allocated峰值GiB | RSS峰值GiB |
|---|---:|---:|---:|---:|
| D18-1105.pdf | 8.03 | 76.61 | 45.65 | 5.73 |
| 2203.16804.pdf | 53.55 | 105.83 | 48.53 | 6.34 |
| 1511.08308.pdf | 51.51 | 117.37 | 49.23 | 5.73 |

本轮合计输入10159、输出989 Tokens；总运行299.90秒；3次本地生成、0次重试、0次付费API。结束GPU状态：0 MiB, 81153 MiB（used/free）。实例未关机或改计费模式。

## 结论与停止点

格式问题已定位为模型生成的49字符外层前缀；未发现Prompt重复、错误chat包装或1024截断。作者README允许格式纠正但没有具体算法；官方Result本来会str()。保守候选已在独立目录测试，数组内部、数值、重复项均未改动，未送入标准化或计分。

当前42篇合规、259条Gold；1912.08777.pdf输入55324，含36条Gold，保持BLOCKED。正式42篇范围、失败评价口径和格式规则均须用户确认；依据来自本次附件第三、五节。所需最小规则、实例与时间预算详见formal_protocol_proposal.md。

Extraction：新增3次完成；Fully LLM/CS/Partially：未执行；Llama IIM/TDM/TDMR与排行榜P/R/F1、LR/PC/RC/RBO/AO：**N/A，尚未评价，不能记为0**。只完成了同范围GPT-4.1的免费离线官方评价，TDMR F1=0.431616，明确不计作Llama结果。

## 工程记录与完整性

复用原环境和30片权重；本轮未下载/安装。69个远端源码/证据哈希一致；本地214个受保护文件哈希未变。CS已有10个模型文件SHA再次通过，没有重复嵌入计算。

仅修正诊断工程问题：历史pipeline日志为嵌套批次列表，按实际结构读取；Windows官方评价子进程启用UTF-8并使用任务内离线缓存路径；初次扩大历史文件扫描耗时，停止本任务扫描后改用明确214个保护文件清单。没有修改模型、Prompt、官方算法或预测。

本地：`D:\C++\SCILEAD\pilot\autodl_llama3\20261021_diagnostic`；远端：`/root/autodl-tmp/scilead/runs/llama3/20261021_diagnostic`。原始输出在extraction/，候选在diagnostics/candidates/，逐条哈希与判据在diagnostics/format_audit.json；execution状态见experiment_manifest.json。正式入口沿用原 adapters/run_llama.py，但确认前不得启动。恢复时先检查request/complete，不能删除失败检查点来重跑。
