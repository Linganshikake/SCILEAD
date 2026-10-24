# P4 论文范围核查

已核实：完整Gold43篇/295条；既有TeX39篇/283条；当前流程完成37篇/248条Gold覆盖，其中28篇非空65条原始预测，9篇VALID_EMPTY。所有paper_id均与Gold完全对应；无缺Gold、无无法匹配ID。

作者36篇的确切成员与TeX版本仍**UNVERIFIED**。能确认“属于作者36篇且完成”的论文为0篇，是缺少成员证据，不表示与作者集合不相交。37篇成功论文全部标为“已完成、作者子集身份未核实”。禁止按抽取得分从39/37篇中挑36篇。

[原论文Appendix C](https://aclanthology.org/2024.emnlp-main.453.pdf)（PDF第12页，印刷页7974）说明取得36份TeX，针对这些论文的Gold评价，并用GPT-4 Turbo做Fully标准化，但检查文本未见成员名单。旧报告定位为Appendix B，此处纠正引用位置，旧文件保留。

本次成功读取固定GitHub树（21个文件）、Release列表（空），核验固定版源码与本地官方数据README/Gold结构；未见独立AxCell36成员清单。ACL页面列出的software.zip/data.zip URL本次直接GET均404，无法检查其内容，不能据此声称作者从未公开名单。证据与访问结果见source_evidence.json、public_sources/。

建议待确认的评价口径：后续主要报告“本地可解析37篇AxCell范围”，保留9篇有效空预测；另外报告39篇可用TeX的失败覆盖和43篇全数据集覆盖，不能把37篇分数当作作者36篇严格复现。39篇中的1905.03197.pdf（26 Gold）和2203.16804.pdf（9 Gold）继续FAILED，未纳入模型/标准化队列。4篇无已核实TeX：128538.pdf、D19-1367.pdf、C18-1139.pdf、D18-1105.pdf。P4不执行任何分数计算。

后续公平比较需要在同一论文范围复算已有模型；Llama-3缺1912.08777.pdf，若做三模型共同范围，则37篇与Llama的交集为36篇，但**这36篇只是本地比较交集，不等于作者AxCell36篇**。正式范围需P4审批，不能静默删除零预测或失败记录后声称全范围。

| paper_id | Gold数量 | 当前状态 | 原始预测数 | 作者36篇成员 |
|---|---:|---|---:|---|
| 1911.10390.pdf | 8 | EXTRACTION_COMPLETE | 6 | UNVERIFIED |
| 2001.04063.pdf | 9 | EXTRACTION_COMPLETE | 3 | UNVERIFIED |
| 1905.03197.pdf | 26 | FAILED | — | UNVERIFIED |
| 1912.08777.pdf | 36 | VALID_EMPTY | 0 | UNVERIFIED |
| 1906.05012.pdf | 3 | VALID_EMPTY | 0 | UNVERIFIED |
| 2203.16804.pdf | 9 | FAILED | — | UNVERIFIED |
| 1910.13461.pdf | 25 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 1908.08345.pdf | 9 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 1808.08745.pdf | 3 | VALID_EMPTY | 0 | UNVERIFIED |
| 2020.findings-emnlp.378.pdf | 6 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| 1809.08370.pdf | 8 | EXTRACTION_COMPLETE | 5 | UNVERIFIED |
| 1806.03489.pdf | 2 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 1702.02098.pdf | 2 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| 1511.08308.pdf | 2 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 2020.emnlp-main.523.pdf | 11 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 2105.03654.pdf | 7 | EXTRACTION_COMPLETE | 4 | UNVERIFIED |
| 128538.pdf | 4 | TEX_UNAVAILABLE | — | UNVERIFIED |
| 1903.07785.pdf | 11 | EXTRACTION_COMPLETE | 4 | UNVERIFIED |
| D19-1367.pdf | 2 | TEX_UNAVAILABLE | — | UNVERIFIED |
| C18-1139.pdf | 4 | TEX_UNAVAILABLE | — | UNVERIFIED |
| D18-1279.pdf | 6 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 1703.06345.pdf | 5 | EXTRACTION_COMPLETE | 3 | UNVERIFIED |
| 1603.01354.pdf | 4 | EXTRACTION_COMPLETE | 3 | UNVERIFIED |
| 1709.04109.pdf | 3 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| 2008.07772.pdf | 6 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| 1911.09483.pdf | 4 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| 1901.10430.pdf | 8 | EXTRACTION_COMPLETE | 3 | UNVERIFIED |
| 2002.03184.pdf | 7 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| wang19f.pdf | 5 | VALID_EMPTY | 0 | UNVERIFIED |
| 1804.09849.pdf | 2 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| D18-1523.pdf | 3 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 1905.12598.pdf | 6 | VALID_EMPTY | 0 | UNVERIFIED |
| 1811.09242.pdf | 6 | VALID_EMPTY | 0 | UNVERIFIED |
| 1812.10235.pdf | 8 | EXTRACTION_COMPLETE | 2 | UNVERIFIED |
| 2020.emnlp-main.152.pdf | 6 | VALID_EMPTY | 0 | UNVERIFIED |
| 1909.02188.pdf | 6 | EXTRACTION_COMPLETE | 4 | UNVERIFIED |
| 1907.00390.pdf | 6 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| 1812.09471.pdf | 6 | EXTRACTION_COMPLETE | 4 | UNVERIFIED |
| D18-1105.pdf | 2 | TEX_UNAVAILABLE | — | UNVERIFIED |
| N19-1373.pdf | 2 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
| K19-1036.pdf | 3 | VALID_EMPTY | 0 | UNVERIFIED |
| 1811.05021.pdf | 2 | VALID_EMPTY | 0 | UNVERIFIED |
| 1711.05568.pdf | 2 | EXTRACTION_COMPLETE | 1 | UNVERIFIED |
