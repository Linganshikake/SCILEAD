# AxCell Extraction + GPT-4.1 Fully Normalization：P4预检查

**P3已由用户验收；P4请求准备完成，未执行标准化和评价，等待明确费用授权。**

输入来自20261022_stage3_resume的原始records.json及既有SCILEAD兼容output.json，不读取历史GPT预测替代AxCell。37篇包含28篇非空、9篇有效空；65条全部保留。37篇对应248条Gold仅用于覆盖计数，不是结果命中数。两篇解析失败原样保留。

候选集合由完整43篇/295条Gold构建：23 Task、71 Dataset、26 Metric。使用原str(set)、PYTHONHASHSEED=0，保存候选实际顺序与序列，字节级匹配冻结Fully候选文件。只将名称集合及当前AxCell单个字段值放入请求；不放入paper_id、Result、原表/单元格、其他字段或Gold答案绑定。

Prompt来自未修改的prompts.json中的normalization-system-prompt；调用未修改的NormalizationPrompt GPT分支生成system/user消息。gpt4-turbo-128k仅是官方模板分支标识，计划wire payload固定gpt-4.1-2025-04-14，temperature=0、seed=0、stream=false。不设置任何客户端输出Token上限、工具或response_format。未实例化API客户端；真正发送参数须在P5执行时再次核验，不能把本阶段计划当作已发送证据。

名称已精确命中时原样保留；不命中时逐字段调用，官方回答精确属于候选集合才接受，否则保存null，不strip、不去引号、不改缩写。Result保持P3字符串：AxCell已有float分数仅沿用P3的str(score)，不补单位、不缩放百分数、不纠正错误含义。来源表格文本另存record_provenance.json，不成为GPT上下文。

123个待调用位置（Task50/Dataset45/Metric28），72字段直接保留，0缓存命中，83个重复位置不去重。2020.emnlp-main.523.pdf虽非空但六个字段精确命中，0请求；9篇空输出也为0请求。未来只可复用同一实验位置、输入、Prompt、候选顺序、模型及完整参数均一致的成功检查点。

输入估算41,714 Tokens，输出历史均值估算474 Tokens；OpenAI公开参考约$0.087220，保守规划情景约$0.209380，但服务商价格未知且不设置输出上限，不能把这些数当报价或费用封顶。细节见normalization_cost_estimate.md。

以下已知错误全部保留，不做人工修复、不剔除：

| 记录ID | 原指标 | Result字符串 | 来源 | 错误类型 |
|---|---|---|---|---|
| 1511.08308.pdf#001 | F1 | 91.85 | 1511.08308v5/table_06.csv/6.2 | METRIC_CELL_BINDING_RECALL_AS_F1 |
| 1511.08308.pdf#002 | F1 | 4696.0 | 1511.08308v5/table_11.csv/2.4 | ENTITY_COUNT_AS_SCORE |
| 1603.01354.pdf#002 | F1 | 300.0 | 1603.01354v5/table_06.csv/3.1 | EMBEDDING_DIMENSION_AS_SCORE |

来源核验：65条均保留paper_id、原模型名、record_index、原始JSON哈希、cell_ext_id、表格路径/哈希/原单元格。1511.08308v5的源表位于原单篇parsed_paper目录，其余位于正式stage2目录；这是索引路径差异，无重解析、无输入修改。

完整性：本轮3809个既有受保护文件哈希不变；7个E盘模型/词表文件匹配冻结模型manifest；固定Git提交的21个跟踪文件与官方Git blob一致（允许检出CRLF）。历史542个已完成请求仅用于Token/耗时统计，1626个相关文件只读核验。

生成器禁止socket连接、DNS及监听，并拒绝读取.env/私钥。依赖导入期间urllib3尝试探测本机IPv6监听(::1,0)，被拒绝并记录；没有外网连接尝试，更没有GPT请求。未读取或检查任何凭据的内容，后续授权执行才安全复用指定认证。

当前未验证项：作者36篇成员、9527.codes实际价目及当前服务可用性。没有用收费请求探测服务。已完成技术请求准备，但付费执行就绪状态仍为false，必须由用户批准范围和调用。

待P4确认：是否按“本地已完成37篇（保留9篇空输出）”独立口径，对65条预测执行123次标准化请求，并接受服务商账单与OpenAI参考价可能不同。即使获批，失败仍保存并停止该请求，不自动重试或换模型。
