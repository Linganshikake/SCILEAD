# Few-shot 与 Zero-shot 对照

抽取条数：284 → 293。所有论文使用相同冻结证据；唯一预设变化为 Extraction Prompt。
模型重新请求可能带来变化，不能仅由此对 Prompt 效果作因果判断。
以下 IIM/ETM 仅比较共同完成的 40 篇；43 篇抽取条数与标准化完成覆盖范围分开报告。

| 指标 | Zero P/R/F1 | Few P/R/F1 |
| --- | --- | --- |
| Task IIM | 0.957500 / 0.971429 / 0.964414 | 0.952500 / 0.961508 / 0.956983 |
| Dataset IIM | 0.806607 / 0.765890 / 0.785722 | 0.758720 / 0.732576 / 0.745419 |
| Metric IIM | 0.861429 / 0.823775 / 0.842181 | 0.790625 / 0.711465 / 0.748959 |
| Result IIM | 0.708589 / 0.734431 / 0.721278 | 0.741400 / 0.745283 / 0.743336 |
| TDM Exact Match | 0.612585 / 0.555987 / 0.582916 | 0.500329 / 0.458441 / 0.478470 |
| TDMR Exact Match | 0.409397 / 0.426670 / 0.417855 | 0.316033 / 0.321163 / 0.318577 |

## 逐篇变化（按 TDMR F1 差排序）

| 论文 | 原条数→新条数 | 原null→新null | Result F1旧→新 | TDM F1旧→新 | TDMR F1旧→新 | ΔTDMR |
| --- | --- | --- | --- | --- | --- | --- |
| C18-1139.pdf | 4→4 | 2→0 | 1.000000 → 1.000000 | 0.571429 → 1.000000 | 0.500000 → 1.000000 | +0.500000 |
| 1811.09242.pdf | 7→6 | 3→2 | 0.307692 → 0.666667 | 0.500000 → 0.500000 | 0.153846 → 0.500000 | +0.346154 |
| 1806.03489.pdf | 8→2 | 1→1 | 0.400000 → 1.000000 | 0.500000 → 0.500000 | 0.200000 → 0.500000 | +0.300000 |
| 128538.pdf | 4→4 | 3→2 | 1.000000 → 1.000000 | 0.285714 → 0.500000 | 0.250000 → 0.500000 | +0.250000 |
| 2020.findings-emnlp.378.pdf | 6→6 | 6→6 | 1.000000 → 1.000000 | 0.000000 → 0.000000 | 0.000000 → 0.000000 | +0.000000 |
| 1709.04109.pdf | 3→3 | 2→2 | 0.333333 → 0.000000 | 0.333333 → 0.333333 | 0.000000 → 0.000000 | +0.000000 |
| D18-1279.pdf | 6→6 | 1→1 | 1.000000 → 1.000000 | 0.833333 → 0.833333 | 0.833333 → 0.833333 | +0.000000 |
| 2020.emnlp-main.523.pdf | 7→7 | 1→1 | 0.333333 → 0.333333 | 0.666667 → 0.666667 | 0.222222 → 0.222222 | +0.000000 |
| 1702.02098.pdf | 2→2 | 2→2 | 0.500000 → 0.500000 | 0.000000 → 0.000000 | 0.000000 → 0.000000 | +0.000000 |
| 2105.03654.pdf | 11→8 | 4→2 | 0.555556 → 0.533333 | 0.000000 → 0.000000 | 0.000000 → 0.000000 | +0.000000 |
| 1912.08777.pdf | 15→36 | 8→13 | 0.000000 → 0.000000 | 0.285714 → 0.686567 | 0.000000 → 0.000000 | +0.000000 |
| 1511.08308.pdf | 2→2 | 2→2 | 1.000000 → 1.000000 | 0.000000 → 0.000000 | 0.000000 → 0.000000 | +0.000000 |
| 1804.09849.pdf | 2→2 | 0→0 | 0.000000 → 0.000000 | 1.000000 → 1.000000 | 0.000000 → 0.000000 | +0.000000 |
| 1809.08370.pdf | 8→8 | 5→5 | 0.625000 → 0.625000 | 0.400000 → 0.400000 | 0.000000 → 0.000000 | +0.000000 |
| 1812.10235.pdf | 8→8 | 0→0 | 1.000000 → 1.000000 | 1.000000 → 1.000000 | 0.500000 → 0.500000 | +0.000000 |
| 1905.12598.pdf | 6→6 | 0→0 | 1.000000 → 1.000000 | 1.000000 → 1.000000 | 1.000000 → 1.000000 | +0.000000 |
| 1906.05012.pdf | 3→3 | 3→3 | 1.000000 → 1.000000 | 0.000000 → 0.000000 | 0.000000 → 0.000000 | +0.000000 |
| 1907.00390.pdf | 6→6 | 2→2 | 1.000000 → 1.000000 | 0.666667 → 0.666667 | 0.666667 → 0.666667 | +0.000000 |
| 1909.02188.pdf | 6→6 | 2→2 | 0.000000 → 0.000000 | 0.666667 → 0.666667 | 0.000000 → 0.000000 | +0.000000 |
| 1911.09483.pdf | 4→4 | 1→1 | 1.000000 → 1.000000 | 0.750000 → 0.750000 | 0.750000 → 0.750000 | +0.000000 |
| 2001.04063.pdf | 9→9 | 7→7 | 1.000000 → 1.000000 | 0.285714 → 0.285714 | 0.222222 → 0.222222 | +0.000000 |
| D18-1523.pdf | 2→2 | 1→1 | 0.400000 → 0.400000 | 0.400000 → 0.400000 | 0.400000 → 0.400000 | +0.000000 |
| 1910.13461.pdf | 15→17 | 10→10 | 0.650000 → 0.619048 | 0.176471 → 0.277778 | 0.050000 → 0.047619 | -0.002381 |
| 1905.03197.pdf | 18→26 | 17→23 | 0.454545 → 0.461538 | 0.102564 → 0.127660 | 0.090909 → 0.076923 | -0.013986 |
| 2008.07772.pdf | 10→10 | 0→0 | 0.750000 → 0.625000 | 1.000000 → 1.000000 | 0.750000 → 0.625000 | -0.125000 |
| 1911.10390.pdf | 7→7 | 6→7 | 0.533333 → 0.533333 | 0.200000 → 0.000000 | 0.133333 → 0.000000 | -0.133333 |
| 1812.09471.pdf | 6→6 | 3→3 | 0.833333 → 0.833333 | 0.400000 → 0.400000 | 0.166667 → 0.000000 | -0.166667 |
| 1903.07785.pdf | 10→10 | 1→1 | 0.761905 → 0.761905 | 0.761905 → 0.571429 | 0.571429 → 0.380952 | -0.190476 |
| wang19f.pdf | 5→5 | 0→1 | 1.000000 → 1.000000 | 1.000000 → 0.800000 | 1.000000 → 0.800000 | -0.200000 |
| 2020.emnlp-main.152.pdf | 6→12 | 0→0 | 0.666667 → 0.444444 | 1.000000 → 1.000000 | 0.666667 → 0.444444 | -0.222222 |
| 1901.10430.pdf | 8→8 | 2→5 | 1.000000 → 1.000000 | 0.750000 → 0.533333 | 0.750000 → 0.500000 | -0.250000 |
| 2203.16804.pdf | 22→9 | 14→12 | 0.387097 → 1.000000 | 0.608696 → 0.000000 | 0.258065 → 0.000000 | -0.258065 |
| 2002.03184.pdf | 7→7 | 2→4 | 1.000000 → 1.000000 | 0.714286 → 0.500000 | 0.714286 → 0.428571 | -0.285714 |
| 1603.01354.pdf | 2→2 | 0→1 | 0.666667 → 0.666667 | 0.666667 → 0.333333 | 0.666667 → 0.333333 | -0.333333 |
| 1703.06345.pdf | 5→7 | 0→3 | 0.800000 → 0.666667 | 1.000000 → 0.727273 | 0.800000 → 0.333333 | -0.466667 |
| D18-1105.pdf | 2→2 | 0→1 | 1.000000 → 1.000000 | 1.000000 → 0.500000 | 1.000000 → 0.500000 | -0.500000 |
| 1711.05568.pdf | 2→2 | 0→1 | 1.000000 → 1.000000 | 1.000000 → 0.500000 | 1.000000 → 0.500000 | -0.500000 |
| 1808.08745.pdf | 5→5 | 2→4 | 0.750000 → 0.750000 | 0.571429 → 0.000000 | 0.500000 → 0.000000 | -0.500000 |
| 1811.05021.pdf | 2→2 | 0→1 | 1.000000 → 1.000000 | 1.000000 → 0.500000 | 1.000000 → 0.500000 | -0.500000 |
| 1908.08345.pdf | 15→9 | 6→9 | 0.500000 → 1.000000 | 0.777778 → 0.000000 | 0.500000 → 0.000000 | -0.500000 |

## 最大变化案例
以下仅列真实新增/消失的模型记录，详细归因需与冻结 source_documents 对照。

### C18-1139.pdf
ΔTDMR F1=+0.500000
```json
{
  "added_raw_records": [
    {
      "Task": "Named Entity Recognition",
      "Dataset": "CONLL03 English",
      "Metric": "F1-score",
      "Result": "93.09±0.12"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "CONLL03 German",
      "Metric": "F1-score",
      "Result": "88.32±0.20"
    }
  ],
  "removed_raw_records": [
    {
      "Task": "Named Entity Recognition (English)",
      "Dataset": "CONLL03",
      "Metric": "F1-score",
      "Result": "93.09±0.12"
    },
    {
      "Task": "Named Entity Recognition (German)",
      "Dataset": "CONLL03",
      "Metric": "F1-score",
      "Result": "88.32±0.20"
    }
  ]
}
```

### 1811.09242.pdf
ΔTDMR F1=+0.346154
```json
{
  "added_raw_records": [
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2010 Task 14",
      "Metric": "F-S",
      "Result": "62.9"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2010 Task 14",
      "Metric": "V-M AVG",
      "Result": "25.20"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2013 Task 13",
      "Metric": "F-BC",
      "Result": "62.2"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2013 Task 13",
      "Metric": "AVG",
      "Result": "24.37"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "Arnet",
      "Metric": "AVG",
      "Result": "58.8"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "PubMed",
      "Metric": "AVG",
      "Result": "46.6"
    }
  ],
  "removed_raw_records": [
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2010 Task 14",
      "Metric": "F-Score",
      "Result": "62.9"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2010 Task 14",
      "Metric": "V-Measure",
      "Result": "25.20"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2013 Task 13",
      "Metric": "F-BC",
      "Result": "61.7"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2013 Task 13",
      "Metric": "F-NMI",
      "Result": "7.97"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "SemEval 2013 Task 13",
      "Metric": "AVG",
      "Result": "22.17"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "Arnet",
      "Metric": "F-Score",
      "Result": "58.8"
    },
    {
      "Task": "Word Sense Induction",
      "Dataset": "PubMed",
      "Metric": "F-Score",
      "Result": "46.6"
    }
  ]
}
```

### 1806.03489.pdf
ΔTDMR F1=+0.300000
```json
{
  "added_raw_records": [
    {
      "Task": "Named Entity Recognition",
      "Dataset": "CONLL-2003",
      "Metric": "F1",
      "Result": "91.73"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0",
      "Metric": "F1",
      "Result": "87.95"
    }
  ],
  "removed_raw_records": [
    {
      "Task": "Named Entity Recognition",
      "Dataset": "CONLL-2003",
      "Metric": "Mention-level F1 score",
      "Result": "91.73 (± 0.10)"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0",
      "Metric": "Mention-level F1 score",
      "Result": "87.95 (± 0.13)"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0 (Broadcast Conversation genre)",
      "Metric": "Mention-level F1 score",
      "Result": "86.33"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0 (Broadcast News genre)",
      "Metric": "Mention-level F1 score",
      "Result": "90.46"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0 (Magazine genre)",
      "Metric": "Mention-level F1 score",
      "Result": "85.91"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0 (Newswire genre)",
      "Metric": "Mention-level F1 score",
      "Result": "89.75"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0 (Telephone Conversation genre)",
      "Metric": "Mention-level F1 score",
      "Result": "76.17"
    },
    {
      "Task": "Named Entity Recognition",
      "Dataset": "ONTONOTES 5.0 (Blogs and Newsgroups genre)",
      "Metric": "Mention-level F1 score",
      "Result": "80.39"
    }
  ]
}
```

### 1808.08745.pdf
ΔTDMR F1=-0.500000
```json
{
  "added_raw_records": [
    {
      "Task": "Extreme Summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-1",
      "Result": "31.89"
    },
    {
      "Task": "Extreme Summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-2",
      "Result": "11.54"
    },
    {
      "Task": "Extreme Summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-L",
      "Result": "25.75"
    },
    {
      "Task": "Extreme Summarization",
      "Dataset": "XSum",
      "Metric": "Human QA Accuracy",
      "Result": "46.05"
    },
    {
      "Task": "Extreme Summarization",
      "Dataset": "XSum",
      "Metric": "Human Ranking Score",
      "Result": "0.037"
    }
  ],
  "removed_raw_records": [
    {
      "Task": "Extreme summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-1 F1",
      "Result": "31.89"
    },
    {
      "Task": "Extreme summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-2 F1",
      "Result": "11.54"
    },
    {
      "Task": "Extreme summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-L F1",
      "Result": "25.75"
    },
    {
      "Task": "Extreme summarization",
      "Dataset": "XSum",
      "Metric": "Human QA-based evaluation (percentage of questions answered correctly)",
      "Result": "46.05"
    },
    {
      "Task": "Extreme summarization",
      "Dataset": "XSum",
      "Metric": "Human ranking score",
      "Result": "0.037"
    }
  ]
}
```

### 1811.05021.pdf
ΔTDMR F1=-0.500000
```json
{
  "added_raw_records": [],
  "removed_raw_records": []
}
```

### 1908.08345.pdf
ΔTDMR F1=-0.500000
```json
{
  "added_raw_records": [
    {
      "Task": "Summarization",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-1",
      "Result": "43.85"
    },
    {
      "Task": "Summarization",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-2",
      "Result": "20.34"
    },
    {
      "Task": "Summarization",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-L",
      "Result": "39.90"
    },
    {
      "Task": "Summarization",
      "Dataset": "NYT",
      "Metric": "ROUGE-1",
      "Result": "49.02"
    },
    {
      "Task": "Summarization",
      "Dataset": "NYT",
      "Metric": "ROUGE-2",
      "Result": "31.02"
    },
    {
      "Task": "Summarization",
      "Dataset": "NYT",
      "Metric": "ROUGE-L",
      "Result": "45.55"
    },
    {
      "Task": "Summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-1",
      "Result": "38.81"
    },
    {
      "Task": "Summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-2",
      "Result": "16.50"
    },
    {
      "Task": "Summarization",
      "Dataset": "XSum",
      "Metric": "ROUGE-L",
      "Result": "31.27"
    }
  ],
  "removed_raw_records": [
    {
      "Task": "Single-document news summarization (extractive)",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-1 F1",
      "Result": "43.85"
    },
    {
      "Task": "Single-document news summarization (extractive)",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-2 F1",
      "Result": "20.34"
    },
    {
      "Task": "Single-document news summarization (extractive)",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-L F1",
      "Result": "39.90"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-1 F1",
      "Result": "42.13"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-2 F1",
      "Result": "19.60"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "CNN/DailyMail",
      "Metric": "ROUGE-L F1",
      "Result": "39.18"
    },
    {
      "Task": "Single-document news summarization (extractive)",
      "Dataset": "NYT",
      "Metric": "ROUGE-1 Recall",
      "Result": "46.66"
    },
    {
      "Task": "Single-document news summarization (extractive)",
      "Dataset": "NYT",
      "Metric": "ROUGE-2 Recall",
      "Result": "26.35"
    },
    {
      "Task": "Single-document news summarization (extractive)",
      "Dataset": "NYT",
      "Metric": "ROUGE-L Recall",
      "Result": "42.62"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "NYT",
      "Metric": "ROUGE-1 Recall",
      "Result": "48.92"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "NYT",
      "Metric": "ROUGE-2 Recall",
      "Result": "30.84"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "NYT",
      "Metric": "ROUGE-L Recall",
      "Result": "45.41"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "XSum",
      "Metric": "ROUGE-1 F1",
      "Result": "38.81"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "XSum",
      "Metric": "ROUGE-2 F1",
      "Result": "16.50"
    },
    {
      "Task": "Single-document news summarization (abstractive)",
      "Dataset": "XSum",
      "Metric": "ROUGE-L F1",
      "Result": "31.27"
    }
  ]
}
```

## 与原论文观察对照
原论文 Section 6.3 报告 ETM 略降、Task/Metric IIM 提升。本轮方向按上表实际值记录；使用 GPT-4.1、固定证据与本轮只切换抽取 Prompt 的设定，不预设相同趋势。
标准化仍可能将不在集合内的回答变为 null；这类错误与抽取数值遗漏分别记录，未手工纠正。