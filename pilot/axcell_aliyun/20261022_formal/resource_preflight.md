# 阶段 0：资源预检查

测量时间 UTC：2026-10-22T08:13:46.864092+00:00；上海时间：2026-10-22T16:13:46.864092+08:00。

| 项目 | 当前实测 |
|---|---|
| 主机 | Ubuntu 22.04.5 LTS，8 vCPU，nproc=8 |
| 物理内存 | 30.689 GiB |
| 三次采样最低 MemAvailable | 28.948 GiB |
| Swap | 0；本阶段未启用或调整 |
| Committed_AS / CommitLimit | 2.129 / 15.345 GiB，Linux 指标，不套用 Windows 提交限额语义 |
| 数据路径挂载 | `/root/scilead/axcell` 和 `/var/lib/docker` 均在 `/dev/nvme0n1p3`，ext4，挂载 `/` |
| df 可见文件系统容量 / 余量 | 78.373 / 56.160 GiB；云盘标称 80 GiB，无独立数据盘 |
| inode | 总 5,224,464；余 4,774,718（本次 df -i） |
| Docker / 任务容器 | Engine active；运行容器 0 |
| Elasticsearch | 停止；没有因 P0 检查启动 |

| cgroup | memory.max | memory.high | cpu.max |
| --- | --- | --- | --- |
| /sys/fs/cgroup/user.slice/user-0.slice/session-186.scope | max | max | None |
| /sys/fs/cgroup/user.slice/user-0.slice | max | max | None |
| /sys/fs/cgroup/user.slice | max | max | max 100000 |
| /sys/fs/cgroup | None | None | None |

`max` 表示相应 cgroup 没有该硬限额；根级文件不存在不代表主机内存无限。有效主机 RAM 仍为约 30.69 GiB。停止的 ES 容器限制为 3 GiB、CPU 2、无额外容器 swap；转换容器计划限制保持 20 GiB/6 CPU。当前零模型负载，**没有新的运行峰值测量**。

此前单篇模型子进程 maxRSS 约 4.813 GiB，ES 采样峰值约 1.304 GiB，CPU 推理约 65.3 秒；仅作为已有基线，不当作本轮批量实测。P0 证明当前满足 ≥6 GiB 可用内存及 ≥20 GiB 磁盘余量的启动门槛，不能保证所有长论文/复杂表格的峰值。

39 个本地 TeX 合计 59,188,214 bytes（56.45 MiB）；远端目前只存一篇既有输入，其余 38 篇尚未传送，待后续授权。现有 56 GiB 余量足以容纳这些输入；批量转换临时文件和日志峰值未知，后续仍逐篇测量并保持 20 GiB 工作余量。

冻结保护条件：串行一次一篇、单份模型；阶段/每篇开始前重测资源；RAM 连续 15 秒低于 2 GiB、容器连续 15 秒达到 95% 限额、OOM 或磁盘工作余量不足时保存日志并停止任务所属进程/容器。转换容器退出后才进入模型服务阶段，不同时预加载多个模型。未来批量磁盘监测需在 P2 前验证；本轮未创建或启动批量程序。

无需修改 WSL、swap、分页文件、Docker 全局设置或云实例规格。原有云实例正常计费，不新增云资源或付费 GPT 调用。服务器未关机，Docker daemon 保持原状态。
