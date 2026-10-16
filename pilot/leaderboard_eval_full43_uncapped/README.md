# 离线复现说明

正式输入为 ../full43_uncapped/merged/normalized_output.json，不写入或重建 Baseline。全部新文件位于本目录。使用 D:\miniconda3\envs\scilead\python.exe -B -X utf8。

1. 首次冻结：freeze_and_check.py。已有 freeze_before.json 时拒绝覆盖。
2. run_official_leaderboard_eval.py：独立 CLI 桥接入口，调用未改动的 leaderboard_eval.main；生成 official/ 原始结果。
3. test_paper_metrics.py：公式、空榜、并列和源码数值规则验证。
4. evaluate_paper_metrics.py：只读构建逐榜论文 ID 排名及 AO、LR 两种口径。数值转换调用原始构建函数。
5. write_reports.py：生成报告并再次核验输入哈希。最终 artifact_sha256.json 记录本目录文件清单；重跑任何汇总后需重新生成清单。

所有评价脚本通过 common.boundary 禁止网络、敏感配置读取和向本目录外写文件；Python 禁写 bytecode，临时文件和缓存定向至本目录。Windows NUL 设备仅用于系统探测，不产生磁盘文件。公开参考 PDF 已保存在 reference/，后续复跑无需网络。

official/eval_results.json 和 eval_values.json 是原始 main 的直接输出。paper_metrics/ 是独立论文公式补充，不能把 RBO 当成 AO。leaderboards/ 保存 27 榜的原值、官方转换值、Gold/预测排名、逐层 AO、并列和缺失原因候选。空榜不删除。

本轮没有 LLM API 调用、模型初始化、权重下载、PDF 预处理、向量检索或标准化调用。原论文 PDF 的文本/页面检查仅用于核对定义，不处理 43 篇实验论文。不要将参考 PDF 的下载计作模型请求。
