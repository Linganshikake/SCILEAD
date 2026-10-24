# 1905.03197.pdf：兼容性诊断方案（未实施）

状态：`RECOVERY_BLOCKED_COMPATIBILITY`。没有对这篇论文执行新的完整转换，也没有修改其 TeX。

## 已确认的失败链

- 正确主文件为 `unified.tex`（官方选择器优先级 15）；`settings.tex` 和 `math_commands.tex` 均为 0。
- 原包 7 个普通文件与正式解压副本逐文件 SHA256 一致，包含 `neurips_2019.sty`，不是解压遗漏。
- `unified.tex:22` 加载 `settings.tex`；后者第 14、15 行加载 TikZ 和 `tikzmark`。
- 固定镜像的 `tikzlibrarytikzmark.code.tex` 第 14 行要求 `expl3, l3keys2e, xparse`。
- 首个真正的 Error 是原 stderr 第 167 行：`Package expl3 Error: Required primitives not found`，定位 `expl3-code.tex:288`。
- expl3 提前终止后才出现 `\ExplSyntaxOn`、`\cs` 等未定义与下划线错误；达到 101 errors 后终止。
- 镜像含 `capt-of.sty`、`scalerel.sty`、`adjustbox.sty` 的 TeX 文件；日志中的 “No LaTeXML binding / missing files” 不能理解为源包缺文件。
- 作者的 1171/1173/1177 补丁分别处理 NeurIPS/参考文献预加载、URL、ICML algorithmic；不提供 expl3/tikzmark 支持。原日志已加载 NeurIPS binding，不能用“漏打 NeurIPS 补丁”解释本错误。

## 最小的后续诊断范围

若另行批准兼容变体，先针对上述依赖链建立小型隔离诊断，不先重跑整篇：使用相同固定镜像、原三个补丁，仅增加**有权威来源、版本固定且语义明确的 tikzmark/LaTeXML binding**。当前未找到并验证这样的候选，因此此处不提供猜测性宏定义或可执行补丁。

待候选有来源后，先验证纯文本及 TikZ 标记用例，再允许一次完整论文恢复；整篇恢复最多两次，每次只引入一个有记录的兼容变更。新增文件、来源版本、许可证、哈希和 diff 必须先固定。此方案未获执行批准，当前不启动。

影响范围包括 TikZ 位置标记、行内图形、其余 expl3/xparse 调用及可能的表格单元格内容；不能只验证文档能退出。源文件还定义 `\mybox`、`\bg`、`\rg`，须核查引用与作用域，不能直接设为空操作。

不采用以下做法：删除 `\usetikzlibrary{tikzmark}`；定义假的 `\ExplSyntaxOn` 或引擎版本；删表格；注释正文；升级整套转换器。即使后来得到 HTML，也只能先标记独立 RECOVERY 变体，不能覆盖原版失败或直接计入正式 37 篇。

## 内容验收基准

原始 TeX 的静态扫描记录 10 个 table/table* 块、14 个 tabular 起始标记；这是源码结构计数，不是 AxCell 解析数。各块原文、行号及数值保存在 `diagnosis/1905.03197.pdf/source_structure.json`。后续须检查原表头、行名、数值和正文末尾，使用原版 `PaperCollection` 读取产物。没有 HTML 的本轮结果不能声称表格保留或解析成功。
