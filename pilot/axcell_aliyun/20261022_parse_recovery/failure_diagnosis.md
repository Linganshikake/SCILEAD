# 两篇失败的诊断与受控恢复记录

本轮完成只读诊断与一次受控恢复尝试，**未恢复任一论文**。所有结果为 RECOVERY，不改正式阶段 2。

## 1905.03197.pdf

主文件 `unified.tex` 正确，官方优先级 15；其他两份 TeX 优先级 0。原包 7 个文件与正式解压逐文件匹配，包括 `neurips_2019.sty`、`settings.tex`、`math_commands.tex`。没有解压或文件组织修复的依据。

原 `container_stderr.log:167` 首个 Error 为 `Package expl3 Error: Required primitives not found`，位置 `expl3-code.tex:288`。调用链：`unified.tex:22` → `settings.tex:14–15` → TikZ/tikzmark → 镜像中的 `expl3, l3keys2e, xparse`。随后才出现 `\ExplSyntaxOn`、`\cs` 等连锁错误，最终 101 errors/1 fatal。固定 LaTeXML 为 0.8.4，镜像没有独立 expl3/tikzmark binding。

`capt-of.sty`、`scalerel.sty`、`adjustbox.sty` 在镜像内实际存在；缺少 binding 的警告不能等同源文件下载缺失。首个错误已定位，但不保证修复它后不存在其他兼容问题。

没有执行重复转换或宏补丁。具体独立兼容诊断提案见 `1905_compatibility_proposal.md`；不删除宏、表格或正文，不使用猜测定义。静态 TeX 计数为 10 个 table/table* 块、14 个 tabular 起始标记；没有可验证的解析产物。

## 2203.16804.pdf

主文件 `acl.tex` 正确；原包 10 个文件与正式解压一致，`acl.sty` 和 `acl_natbib.bst` 都在。原日志另有 pgfplots `compat=1.17` 不被镜像所含最多 1.16 支持、`\DeclareUnicodeCharacter`、`\aboverulesep`、`\belowrulesep` 未定义；这些错误未在正文消化阶段直接终止转换，不能断言与后处理异常无关。本轮没有修改它们。

原 300 秒运行在约 26 秒完成正文消化、构建、数学处理并进入 Scan。最后可见步骤为 `Scan index.html ... DBStatus: 517/0 objects`。历史容器峰值约 10.70 GiB，无 OOM 或 swap；没有保存 CPU 历史，失败容器/临时目录已经清理，没有残留 HTML，不能补造历史 CPU 数据。

固定 Engrafo 使用 readline 逐行转发 LaTeXML 日志，而部分 NoteBegin/进度没有换行，故日志沉默不能直接证明死锁。源码含 37,517,244 字节 `anthology.bib`，静态标记计数 70,470，是潜在后处理负担。**尚未证实本次持续增长发生在参考文献转换，不能将该假说当作根因。**

在原任务无 OOM/换页且资源余量充分的条件下，仅执行一次获准诊断。恢复版 `latex2html.sh` 相对原文件逐字节唯一差异是 `timeout -s KILL 300 engrafo` 改为 600。原镜像、输入 SHA256、官方补丁、主文件选择、原版 PaperExtractor、6 CPU/20 GiB/禁网配置保持一致。监控器新增只读 CPU/文件位置/中间文件观察，外层 660 秒看门狗只供解析清理，不增加 Engrafo 的 600 秒上限。

实际运行 511.09 秒（含清理），最后采样在 502.65 秒。Perl 持续 CPU 计算，容器累计 CPU 约 501.70 秒；没有观察到网络等待或外部工具阻塞。采样峰值容器 19.726 GiB、Perl RSS 19.644 GiB。最后采样时仍没有 HTML/XML/log 中间文件。触发 95% 容器上限持续 15 秒的保护，原因 `TASK_CONTAINER_NEAR_MEMORY_LIMIT`；SIGTERM 停止包装进程，随后 `docker stop` 返回 0。但是保护未及时阻止容器继续分配内存：内核日志确认 17:33:38（北京时间）清理窗口内达到 **20 GiB**，对同一容器 PID75933 的 Perl 触发 **1 次 CONSTRAINT_MEMCG OOM kill**。它不是全宿主物理内存耗尽。无交换增长。外层退出码 125，包装子进程 -15；这**不是运行足 600 秒后再次超时**。

原始监控最后一条记录的 OOM 标志仍为 false，原因是它随后进入清理且不再采样；结束后的全局 oom_kill 增量与内核日志补足了这个盲区。保留原始记录，不修改成事后数据。本轮早先基于采样作出的“无 OOM”进度判断已经更正。保护阈值的 15 秒持续条件及容器停止延迟对这一快速增长场景不足；后续资源保护需要提前触发并覆盖清理窗口，不能把本次资源使用称为稳定或通过。

可确认：延长超时未在保护范围内恢复；LaTeXML 后处理持续计算并增长内存。未确认：具体函数/循环、是否正在构建大型参考文献、剩余完成时间。没有再次延长、改内存上限、缩减 bibliography 或替换 PDF 文本。原 13 个 table/table* 和 13 个 tabular 源结构完整保留，但没有 HTML 可供表头、行名、数值验收。

## 原版补丁行为与工程记录

实时 Docker stdout 显示 1171.patch 中仓库 `MANIFEST` 文件在安装目录不存在，清单 hunk 被跳过；NeurIPS、Post.pm、MakeBibliography.pm，以及后续 URL/ICML 代码补丁执行。没有新增补丁，也没有修复这个原版安装目录差异。原 1905 日志已成功加载 NeurIPS binding，不是遗漏 NeurIPS 补丁。

只读审计曾产生一份 `guess_main.cpython-310.pyc`；按创建时间/路径核实后保留诊断副本并精确移除，后续禁写字节码，源码文本未改变。初次独立核验误用本地汇总字段 rows，而远端实际字段为 papers，已仅修复审计脚本并重做只读检查；该工程修正没有重跑转换。初次大段 SSH 输出读取不完整，改用 SFTP 读取已保存的同一审计文件并校验，没有重复镜像转换。

## 完整性

本地冻结目录 1152 文件、远端冻结目录 1712 文件的前后内容及大小相同。37 篇成功论文的 643 个产物按原 manifest 全部匹配；91 个源码、模型等既有资产匹配。两篇原失败日志均保留，所有输入归档和解压文件匹配。没有模型抽取、GPT/API 调用或阶段 3 运行。
