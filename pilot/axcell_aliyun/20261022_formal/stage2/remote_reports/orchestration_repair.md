# 阶段 2 编排保护修复记录

独立只读审查指出四项重要边界问题；未涉及原版解析方法。

1. 旧 monitor 在 Popen 后、进入 try/finally 前写 owner，写失败时子进程可能失管。
2. 旧清理顺序先扫描容器再终止生产进程，存在晚启动容器遗漏窗口。
3. 原 stop_reason 已是 TIMEOUT 时，清理失败会被掩盖，可能进入下一篇。
4. 未尝试的资源 BLOCKED 以及子进程已完成的 RUNNING 不能完整恢复。

处理：暂停本任务控制器，当前 2203.16804.pdf 转换自然返回 processing-error 后，控制器保存该失败并在下一篇之前退出。没有因修复中断或重跑论文转换。

在独立 revision2 中：将启动/owner 写入纳入 finally；先终止生产进程组后停止任务容器；清理不完整优先停止队列；只恢复未尝试阻塞项或校验完整的已完成子进程，不重试 FAILED 或状态不明的尝试。

验证：

- `test_policy.py` 4/4；`test_resume_cleanup.py` 新增3项先失败后通过。
- Linux `test_monitor_integration.py`：旧版 owner 写失败留下测试子进程、旧版清理顺序错误，两项均 RED；测试自身清理了所创建子进程。
- revision2 两项均 GREEN，没有残留测试进程。结果见 `monitor_regression_tests.json`。
- 已完成4篇和失败2篇原样保留；恢复只处理尚未尝试的队列。

`orchestration_v1/` 保留旧脚本/检查点。`configuration.json` 是初始科学配置与脚本版本快照，保持不变；实际后续调度版本另见 `orchestration_revision2.json`，不能把初始 monitor 哈希当成全部38篇的实际调度哈希。`parse_one.py` 与原版 PaperExtractor 调用没有改变。输入、镜像、模型、阈值、Gold 和解析内容均不调整。

Ruling: 修复仅涉及已授权的独立编排及资源保护，继续既有阶段2任务无需新增方法批准；不以修复为由重跑失败输入，不越过P2。
