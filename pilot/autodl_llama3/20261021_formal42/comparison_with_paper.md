# 原论文参考与本轮结果

[官方论文](https://aclanthology.org/2024.emnlp-main.453.pdf)。原文43篇；本轮42篇；仅并列参考，不计算正式差值。百分制P/R/F1。

|设置|指标|原论文Llama-3（43篇）|本轮Llama-3（42篇）|
|---|---|---|---|
|Fully LLM|Task IIM|87.33 / 92.17 / 89.68|Fully LLM: 83.45 / 87.36 / 85.36|
|Fully LLM|Dataset IIM|92.09 / 87.75 / 89.87|Fully LLM: 82.63 / 77.54 / 80.01|
|Fully LLM|Metric IIM|94.90 / 89.48 / 92.11|Fully LLM: 87.04 / 80.89 / 83.86|
|Fully LLM|Result IIM|39.50 / 49.56 / 43.96|Fully LLM: 37.98 / 47.82 / 42.34|
|Fully LLM|TDM Exact Match|77.13 / 72.56 / 74.77|Fully LLM: 68.49 / 63.43 / 65.86|
|Fully LLM|TDMR Exact Match|27.11 / 35.60 / 30.78|Fully LLM: 23.65 / 32.14 / 27.25|
|Fully CS|TDMR Exact Match|23.22 / 29.54 / 26.00|Fully CS: 21.76 / 28.42 / 24.64|
|Fully CS|TDM Exact Match|62.02 / 58.07 / 59.98|Fully CS: 58.47 / 54.42 / 56.37|
|Partially|TDMR Exact Match|15.70 / 18.75 / 17.09|Partially Stage1: 9.48 / 10.86 / 10.12；Partially Stage2: 19.04 / 26.16 / 22.04|
|Partially|TDM Exact Match|50.75 / 45.30 / 47.87|Partially Stage1: 34.59 / 29.75 / 31.99；Partially Stage2: 62.48 / 53.26 / 57.50|

原文未将Partially元组表明确绑定到具体阶段输出JSON，本报告并列保留Stage1和Stage2，不挑较高值作为原论文对应结果。
原论文表5的AO名称沿用原文；本报告分别列出官方数值RBO与独立论文ID AO，不能未经定义核验直接互换。
Llama-3 Cold Start 是原文另有实验，按本轮限制只列待确认，未执行。
