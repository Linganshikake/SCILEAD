# 1912.08777.pdf 抽取结果核验

完整输入 54,504 Tokens；本次返回 801 Tokens、finish_reason=stop。15 条记录均为合法 JSON，Result 为字符串，无重复，未截断。原有 48 条证据与 Prompt 完全不变，未重新解析 PDF。

模型将 ROUGE-1 / ROUGE-2 / ROUGE-L 合并在同一个 Metric 字段，并将三个结果合并为斜杠分隔字符串，例如 XSum `47.60/24.83/39.64`；还输出三条人工评价记录。Gold 要求逐指标记录，XSum 对应值为 47.21、24.56、39.25。本次没有手工拆分、重绑或修正。

31 次官方逐字段标准化调用均正常结束，21 次集合内回答，10 次集合外回答按官方保存 null。该篇官方 Result IIM F1=0、TDM F1=0.2、TDMR F1=0。未截断不等于答案完整或正确。

全部原始预测、标准化记录和 36 条 Gold 对照见 [tdmr_comparison.md](../evaluation/tdmr_comparison.md)。其余十四篇结果未变，历史错误记录见 [上一阶段核验](../../subset15/inspection/manual_findings.md)。
