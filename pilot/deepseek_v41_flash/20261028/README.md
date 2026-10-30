# DeepSeek-V4.1-Flash SCILEAD — COMPLETE

入口：[中文报告](report.md)、[机器可读汇总](results_summary.json)、[完整性核验](verification.json)。

全部43篇完成；Extraction仅运行一次，六个最终分支完整保留。原始请求在fully/papers和variants各stage/api_calls中。
已完成任务不应重新执行。status.py仅检查状态，final_audit.py仅离线核验请求与输入。
evaluate_ready.py只补齐缺失的已完成阶段评价；已完成评价跳过，正式输出不覆盖。
analysis/README.md提供独立离线评价命令，variants/README.md记录适配和原版方法的对应关系。

主要结果路径见report.md。Partially及Cold Start主指标取第二阶段，第一阶段另列。
generation_config.json是实际请求公共参数；transport.py是唯一网络发送层。
凭据仅在执行时从指定deepseek.env读取，不复制到此目录。
本轮未提交GitHub，也未修改历史PPT或其他冻结实验。
