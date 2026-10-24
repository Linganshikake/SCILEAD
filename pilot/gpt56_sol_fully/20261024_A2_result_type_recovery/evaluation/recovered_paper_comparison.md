# 两篇恢复后的逐条对照

恢复只解决Result类型，不代表数值、方向或Metric绑定正确。原始预测不修改。


## 1812.09471.pdf

|Gold Task / Dataset / Metric / Result|同TDM预测Result|说明|
|---|---|---|
|Intent Detection and Slot Filling / ATIS / F1 / 0.952|['0.952']|严格数值相等|
|Intent Detection and Slot Filling / ATIS / Accuracy / 0.95|['0.95']|严格数值相等|
|Intent Detection and Slot Filling / ATIS / Overall-Accuracy / 0.834|['0.834']|严格数值相等|
|Intent Detection and Slot Filling / SNIPS / F1 / 0.918|['0.918']|严格数值相等|
|Intent Detection and Slot Filling / SNIPS / Accuracy / 0.977|['0.973']|TDM相同，但原始数值不相等；未换算或修正|
|Intent Detection and Slot Filling / SNIPS / Overall-Accuracy / 0.809|['0.809']|严格数值相等|

## 2002.03184.pdf

|Gold Task / Dataset / Metric / Result|同TDM预测Result|说明|
|---|---|---|
|Machine Translation / WMT’14 EN-FR / BLEU / 43.2|['43.2']|严格数值相等|
|Machine Translation / WMT’14 EN-DE / BLEU / 29.6|['29.6']|严格数值相等|
|Machine Translation / IWSLT’14 EN-DE / BLEU / 35.5|['35.5']|严格数值相等|
|Summarization / CNN/DailyMail / ROGUE-1 / 40.59|['40.59']|严格数值相等|
|Summarization / CNN/DailyMail / ROGUE-2 / 18.97|['18.97']|严格数值相等|
|Summarization / CNN/DailyMail / ROGUE-L / 36.81|['36.81']|严格数值相等|
|Language Modeling / WikiText-103 / Perplexity / 23.3|['23.3']|严格数值相等|