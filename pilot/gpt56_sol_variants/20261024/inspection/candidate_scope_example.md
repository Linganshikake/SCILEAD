# Cold Start默认顺序：候选范围与名称匹配案例

本分析仅在模型输出完成后离线读取Gold，不反馈模型，不修正预测。论文：`2020.findings-emnlp.378.pdf`。

|Result|Gold Dataset / Metric|Stage1 Dataset / Metric|Stage2 Dataset / Metric|
|---|---|---|---|
|90.32|Ontonotes v5 - English / F1|ON5E / F1 score|Ontonotes v5 - English / F1|
|55.14|WNUT-16 - English / F1|WN16 / F1 score|WNUT-16 - English / F1|
|50.68|WNUT-17 - English / F1|WN17 / F1 score|WNUT-17 - English / F1|
|81.18|Ontonotes v4 - Chinese / F1|ON4C / F1 score|ON4C / F1 score|
|96.62|Resume - Chinese / F1|RE / F1 score|RE / F1 score|
|69.78|Weibo - Chinese / F1|WE / F1 score|WE / F1 score|

六个数值均已抽取，Task均为Named Entity Recognition (NER)。第一阶段从空集合生长，保留数据集缩写和F1 score，未产生null；这不等于通过Gold名称精确匹配。第二阶段官方候选仅有27个排行榜TDM，其中包含前三条英文NER目标，不包含本例后三条中文数据集目标。模型前三条返回候选中的标准元组，后三条返回集合外名称，官方逻辑保留原字段。

该例体现候选信息条件和两阶段职责的差异，不能将阶段二分数变化解释为重新抽取了数值，也不能把所有集合外返回统称为程序失败。没有人工改名或新增候选。

来源：`cold_default/stage1/normalized_output.json`、`cold_default/stage2/leaderboard_normalized_output.json`、相应events与config.json指向的冻结Gold。结构化对照见本目录同名JSON。
