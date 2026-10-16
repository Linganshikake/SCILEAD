# 离线审计文件说明

当前为 BLOCKED，不是 threshold=2 复现成功。

- report.md：结论、数据范围、来源与缺失材料。
- source_manifest.json：原始路径、正式下载 URL、哈希、归档成员与获取失败。
- data_audit.json / data_differences.md：精确字符串/不同论文计数、差异和结构检查。
- verified_inputs/：仅核验过的冻结参考副本及 README，不包含已验证作者 threshold=2 文件。
- diagnostics/：只做数量/差异检查，禁止正式评分。
- reuse_manifest.json：Fully/Cold 复用文件索引、哈希和验证。
- threshold3_frozen_reference.json / comparison_threshold3_vs_threshold2.md：旧分数参考，不是新实验结果。
- next_stage_configs.json / next_stage_plan.md：禁用的未来配置及依赖关系。
- freeze_before.json / verification.json：运行前后 42,610 个历史文件及源码/Gold/依赖完整性。
- artifact_sha256.json：本轮文件清单（不含该清单自身）。

复核已有离线审计可依次执行 audit_data.py、prepare_reuse.py、verify.py、write_reports.py，解释器 D:\miniconda3\envs\scilead\python.exe，参数 -B -X utf8。脚本仅写本目录，不调用模型。freeze.py 是首次快照，不可覆盖运行。fetch_official.py 是单独公共来源下载器，不需在离线复核时运行。
如果未来获得另一官方数据版本，先另存并单独审核，不能直接让本轮诊断输出变成实验输入。本轮不提供会自动启动 API 的执行命令。
