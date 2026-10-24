# A1离线验收

仅离线操作，本轮API调用0次。原始A1文件保持不变，报告与评价写入A2独立目录。

对2020.emnlp-main.152.pdf的6条Extraction、13次Normalization逐字段追溯：6个Task、3个Dataset、4个Metric发起请求；其余直接保留。Result字符串原样保留，无缓存合并、修正、删项或重生成。14次历史请求均HTTP200、stop且响应模型标识匹配。

## 官方评价

使用完整43篇Gold，未经修改的tdm_eval.py只遍历该篇预测，评价分母为1篇/6条Gold。P/R由官方生成；F1额外按2PR/(P+R)计算。

|指标|P|R|F1|
|---|---:|---:|---:|
|Task|1.000000|1.000000|1.000000|
|Dataset|1.000000|1.000000|1.000000|
|Metric|1.000000|1.000000|1.000000|
|Result|1.000000|1.000000|1.000000|
|TDM|1.000000|1.000000|1.000000|
|TDMR|1.000000|1.000000|1.000000|

严格Decimal数值相等及TDM一对一匹配为6/6；本篇未发现官方包含关系产生的虚假匹配、重复记录或额外结果。

## 原始缓存证据抽查

6条均来自第5页Table 3。第4页Metrics正文明确Slot用F1、Intent用Accuracy、联合结果用Sentence accuracy。

|Dataset|Metric|Result|Table 3方法行|
|---|---|---|---|
|ATIS|F1|96.24|SlotRefine with GloVe|
|ATIS|Accuracy|97.74|SlotRefine with BERT|
|ATIS|Sent-Accuracy|88.64|SlotRefine with BERT|
|SNIPS|F1|97.05|SlotRefine with BERT|
|SNIPS|Accuracy|99.04|SlotRefine with BERT|
|SNIPS|Sent-Accuracy|92.96|SlotRefine with BERT|

ATIS Slot最佳96.24来自GloVe而非BERT（96.16），抽取保留了逐指标最佳结果。6条均与Gold对应，未确认Baseline混入或字段错误。表格转换文本存在列顺序混排；上述判断基于冻结表格与Metrics正文，未重新渲染PDF，不代表全量解析质量已验证。

原始Task的细分名称经官方候选映射统一为Intent Detection and Slot Filling；Snips→SNIPS、F1-score→F1、Sentence accuracy→Sent-Accuracy均正确。

单篇满分只验证这篇与管线，不用于调整Prompt、参数、排序、抽取规则或推广全量性能结论。
