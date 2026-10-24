# AxCell P4准备交付

已完成离线核查及请求准备；实际GPT调用0、标准化0、评价0。停止在P4，未经批准不得收费执行。

- 原始范围：37篇完成，28篇非空，9篇VALID_EMPTY，65条预测；2篇解析失败保留。
- 123次拟新增请求：Task50、Dataset45、Metric28；72字段精确命中，缓存命中0。
- 41,714输入Tokens；历史均值474输出Tokens，参考费用$0.087220；每请求128输出Tokens规划情景$0.209380，不是上限。中转站实际价格UNVERIFIED。预计串行5–15分钟。
- 官方36篇成员仍未核实。当前范围仅能称“本地37篇可解析范围”，并另报39/43覆盖；完整43篇标准名称集合保持不变。
- 保留91.85误绑F1、4696实体数量、300向量维度这三类错误，未修正。
- 候选与Prompt、65条来源与Result、冻结文件通过核验；无模型、Docker、SSH或其他实验启动。

主要交付：normalization_request_manifest.json（123位置清单）、normalization_request_preview.json（全部精确payload）、normalization_input.json（37篇含空输出）、record_provenance.json、paper_scope_comparison.csv、normalization_preflight.md、normalization_cost_estimate.md、verification.json。

D盘目录：`D:\C++\SCILEAD\pilot\axcell_aliyun\20261022_stage4_preparation`。
E盘镜像目标：`E:\SCILEAD\axcell\reports\20261022_stage4_preparation`；镜像实际结果以sync_verification.json为准。文件中的D盘来源索引保留原值，不伪造E盘源文件；本轮不复制模型或重新下载数据。
