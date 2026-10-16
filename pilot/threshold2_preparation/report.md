# SCILEAD threshold=2 数据审计与复用准备

**结论：BLOCKED。安全审计与复用准备已完成；正式 threshold=2 评价和 masking preview 未运行。新增 LLM/API 推理调用：0。**

## 数据来源

从 [ACL 论文页面](https://aclanthology.org/2024.emnlp-main.453/) 解析出目前有效的 `/attachments/` 下载路径，成功下载 Data 和 Software 附件。两份 ZIP 均与本地原始 ZIP SHA256 一致；本轮新记录因此补充了独立的官方来源验证，未修改历史来源记录。

| 官方来源 | 结果 |
|---|---|
| [acl_article.html](https://aclanthology.org/2024.emnlp-main.453/) | HTTP 200，47,279 bytes |
| [github_readme.md](https://raw.githubusercontent.com/UKPLab/emnlp2024-leaderboard-generation/8bf74b0a830feb7035c6166dce3394dc344ae532/README.md) | HTTP 200，15,554 bytes |
| [acl_data_attachment.zip](https://aclanthology.org/attachments/2024.emnlp-main.453.data.zip) | HTTP 200，11,211 bytes |
| [acl_software_attachment.zip](https://aclanthology.org/attachments/2024.emnlp-main.453.software.zip) | HTTP 200，18,539 bytes |

原请求给出的不带 `/attachments/` 的两个 ZIP 地址均返回 HTTP 404。作者 [TUdatalib 入口](https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/4345) 在本会话正常证书验证下出现证书链错误或连接超时，未取得其文件列表；不能据此声称作者库不存在 threshold=2 文件。

Data ZIP 只有 README.md、27 榜 leaderboards.json、tdm_annotations.json 和 TSV；Software ZIP 为代码文件，没有 threshold=2 榜单。Data README 明确写最低三篇/27 榜。固定 commit 的 GitHub README 指向同一 TUdatalib 入口，没有另外的 threshold=2 下载链接。

官方 Data ZIP SHA256：`37db7fed3abec7b472ab3de408575bf428b5281adc8b78d39436df0c2c1318c2`。
各文件来源、大小、SHA256、归档成员、结构及版本比较完整保存在 source_manifest.json 和 data_audit.json。没有执行下载归档内的脚本。

## 实际计数与差异

| 范围 | 唯一 TDM / 榜数 | 原始记录数 | 不同论文数 | 性质 |
|---|---:|---:|---:|---|
| 完整冻结 Gold | 141 | 295 | 43 | 官方附件中的原始标注 |
| 作者独立提供的榜单 | 27 | 140 | 43 | 当前正式 threshold=3 评价输入 |
| 完整 Gold 按至少 3 个不同 paper_id 分组 | 33 | 158 | 43 | 数量/差异诊断 |
| 完整 Gold 按至少 2 个不同 paper_id 分组 | 62 | 216 | 43 | 数量/差异诊断，禁止正式评分 |
| 独立作者 threshold=2 文件 | 未找到 | 未核验 | 未核验 | BLOCKED |

按原始 TDM 字符串 tuple、不同 paper_id 计数，未修正名称或缩放 Result。名称集合为 23 Task /71 Dataset /26 Metric。
共有 27 榜的成员和 Result 完全一致；未发现重复 JSON 键、重复榜、未知论文 ID、重复 Gold 行或同 paper/TDM 冲突。官方附件标注、冻结 JSON、TSV 结构化记录一致。

141/138 差异仍未解释。33/27 差额已定位为 CoLA、SST-2、MNLI-m、MNLI-mm、QNLI、RTE 的六组三篇 TDM，但作者为什么未将其纳入独立 27 榜尚无依据。精确任务/指标、三篇 ID 和原值见 [data_differences.md](data_differences.md)。

诊断得到 62 组/216 条，且包含全部旧 27 榜，只证明当前标注可生成这些分组。按本轮要求，它不能代替作者历史 threshold=2 文件，不能用于正式评分。

## 已完成的结果复用核验

从 manifest、已审计评价 invocation 和逐篇索引交叉定位 Fully LLM/CS 输出，确认二者共用同一份 Zero-shot Extraction：43 篇、284 条。逐篇标准化结果与各自合并文件一致；Result 字符串、记录顺序和 source_documents 保持不变。
三种 Cold Start 的 stage1 初始集合为空，顺序及种子类型复算一致，43 篇/284 条输出可复用；新目标 stage2 仍需后续执行。Partially 必须在已核验新榜单上重新生成 mask，再运行两个阶段。
详细文件索引和哈希：reuse_manifest.json；后续禁用配置：next_stage_configs.json；依赖说明：[next_stage_plan.md](next_stage_plan.md)。

## 评价状态

Fully LLM /Fully CS 的 threshold=2 正式指标：**未生成**。未创建 fully_llm_evaluation/、fully_cs_evaluation/、masking_preview/。
[comparison_threshold3_vs_threshold2.md](comparison_threshold3_vs_threshold2.md) 仅保留旧 27 榜分数及口径说明，threshold=2 一列标为未运行。共有 27 榜原始成员/数值检查通过，但新旧逐榜得分比较未运行，不宣称已验证其得分相同。
本轮没有改变 43 篇 TDMR/IIM 的输入，也没有将排行榜范围变化写成抽取指标变化。未来对照 Table 15 须注明本地 GPT-4.1 与论文 GPT-4 Turbo 不同，并保留 LR/RBO/AO 边界。

## 完整性与执行边界

最终 SHA256 核验通过：7 个冻结实验/参考目录共 42,610 个文件，文件集合及内容均未变；另核验 25 个源码/Prompt/Gold/归档文件，依赖版本不变，Git 工作区干净。
Commit：`8bf74b0a830feb7035c6166dce3394dc344ae532`。全部新增文件仅写入本目录。未读取 API Key、未请求任何推理接口、未初始化模型、未重跑解析/Embedding/检索/抽取/标准化、未安装包。
来源核验使用的是公开页面/小型附件 HTTP GET，不是模型推理。独立审计脚本启用网络/敏感配置读取保护；结果见 verification.json。

## 缺失材料与停止点

继续正式评价需要具有作者来源和版本记录的 threshold=2 榜单原文件，并通过与冻结标注及共有 27 榜的兼容性核验。当前已完成所有不依赖该材料的安全步骤，按要求在此停止；不使用诊断 62 组绕过门槛，也不启动 Partially/Cold Start API。
