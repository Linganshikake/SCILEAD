# 逐条 Gold 与原始 / 标准化输出对照

候选索引按数值命中列出，不强行假设一对一关系；`±`、单位等非纯数值文本不满足 Decimal 严格相等。官方字符串包含匹配单独列出。

## 1912.08777.pdf

| Gold 序号及 T/D/M/R | 严格数值候选：原始 → 标准化 | 官方包含匹配候选 | 严格完整匹配 | 分类 |
|---|---|---|---|---|
| 1: Summarization / XSum / ROGUE-1 / 47.21 | — | [] | [] | numeric_result_missing_or_changed |
| 2: Summarization / XSum / ROGUE-2 / 24.56 | — | [] | [] | numeric_result_missing_or_changed |
| 3: Summarization / XSum / ROGUE-L / 39.25 | — | [] | [] | numeric_result_missing_or_changed |
| 4: Summarization / CNN/DailyMail / ROGUE-1 / 44.17 | — | [] | [] | numeric_result_missing_or_changed |
| 5: Summarization / CNN/DailyMail / ROGUE-2 / 21.47 | — | [] | [] | numeric_result_missing_or_changed |
| 6: Summarization / CNN/DailyMail / ROGUE-L / 41.11 | — | [] | [] | numeric_result_missing_or_changed |
| 7: Summarization / Newsroom / ROGUE-1 / 45.15 | — | [] | [] | numeric_result_missing_or_changed |
| 8: Summarization / Newsroom / ROGUE-2 / 33.51 | — | [] | [] | numeric_result_missing_or_changed |
| 9: Summarization / Newsroom / ROGUE-L / 41.33 | — | [] | [] | numeric_result_missing_or_changed |
| 10: Summarization / Multi-News / ROGUE-1 / 47.52 | — | [] | [] | numeric_result_missing_or_changed |
| 11: Summarization / Multi-News / ROGUE-2 / 18.72 | — | [] | [] | numeric_result_missing_or_changed |
| 12: Summarization / Multi-News / ROGUE-L / 24.91 | — | [] | [] | numeric_result_missing_or_changed |
| 13: Summarization / Gigaword / ROGUE-1 / 39.12 | — | [] | [] | numeric_result_missing_or_changed |
| 14: Summarization / Gigaword / ROGUE-2 / 19.86 | — | [] | [] | numeric_result_missing_or_changed |
| 15: Summarization / Gigaword / ROGUE-L / 36.24 | — | [] | [] | numeric_result_missing_or_changed |
| 16: Summarization / WikiHow / ROGUE-1 / 43.06 | — | [] | [] | numeric_result_missing_or_changed |
| 17: Summarization / WikiHow / ROGUE-2 / 19.71 | — | [] | [] | numeric_result_missing_or_changed |
| 18: Summarization / WikiHow / ROGUE-L / 34.8 | — | [] | [] | numeric_result_missing_or_changed |
| 19: Summarization / Reddit TIFU / ROGUE-1 / 26.63 | — | [] | [] | numeric_result_missing_or_changed |
| 20: Summarization / Reddit TIFU / ROGUE-2 / 9.01 | — | [] | [] | numeric_result_missing_or_changed |
| 21: Summarization / Reddit TIFU / ROGUE-L / 21.64 | — | [] | [] | numeric_result_missing_or_changed |
| 22: Summarization / BIGPATENT / ROGUE-1 / 53.63 | — | [] | [] | numeric_result_missing_or_changed |
| 23: Summarization / BIGPATENT / ROGUE-2 / 33.16 | — | [] | [] | numeric_result_missing_or_changed |
| 24: Summarization / BIGPATENT / ROGUE-L / 42.25 | — | [] | [] | numeric_result_missing_or_changed |
| 25: Summarization / arXiv / ROGUE-1 / 44.7 | — | [] | [] | numeric_result_missing_or_changed |
| 26: Summarization / arXiv / ROGUE-2 / 17.27 | — | [] | [] | numeric_result_missing_or_changed |
| 27: Summarization / arXiv / ROGUE-L / 25.8 | — | [] | [] | numeric_result_missing_or_changed |
| 28: Summarization / PubMed / ROGUE-1 / 45.49 | — | [] | [] | numeric_result_missing_or_changed |
| 29: Summarization / PubMed / ROGUE-2 / 19.9 | — | [] | [] | numeric_result_missing_or_changed |
| 30: Summarization / PubMed / ROGUE-L / 27.69 | — | [] | [] | numeric_result_missing_or_changed |
| 31: Summarization / AESLC / ROGUE-1 / 37.69 | — | [] | [] | numeric_result_missing_or_changed |
| 32: Summarization / AESLC / ROGUE-2 / 21.85 | — | [] | [] | numeric_result_missing_or_changed |
| 33: Summarization / AESLC / ROGUE-L / 36.84 | — | [] | [] | numeric_result_missing_or_changed |
| 34: Summarization / BillSum / ROGUE-1 / 57.31 | — | [] | [] | numeric_result_missing_or_changed |
| 35: Summarization / BillSum / ROGUE-2 / 40.19 | — | [] | [] | numeric_result_missing_or_changed |
| 36: Summarization / BillSum / ROGUE-L / 45.82 | — | [] | [] | numeric_result_missing_or_changed |

### 全部原始预测与标准化结果

| 序号 | 原始 Task / Dataset / Metric / Result | 标准化后 |
|---|---|---|
| 1 | Abstractive Summarization / XSum / ROUGE-1/ROUGE-2/ROUGE-L F1 / 47.60/24.83/39.64 | Summarization / XSum / ROGUE-1 / 47.60/24.83/39.64 |
| 2 | Abstractive Summarization / CNN/DailyMail / ROUGE-1/ROUGE-2/ROUGE-L F1 / 44.16/21.56/41.30 | Summarization / CNN/DailyMail / ROGUE-1 / 44.16/21.56/41.30 |
| 3 | Abstractive Summarization / NEWSROOM / ROUGE-1/ROUGE-2/ROUGE-L F1 / 45.98/34.20/42.18 | Summarization / Newsroom / ROGUE-1 / 45.98/34.20/42.18 |
| 4 | Abstractive Summarization / Multi-News / ROUGE-1/ROUGE-2/ROUGE-L F1 / 47.65/18.75/24.95 | Summarization / Multi-News / None / 47.65/18.75/24.95 |
| 5 | Abstractive Summarization / Gigaword / ROUGE-1/ROUGE-2/ROUGE-L F1 / 39.65/20.47/36.76 | Summarization / Gigaword / ROGUE-1 / 39.65/20.47/36.76 |
| 6 | Abstractive Summarization / WikiHow / ROUGE-1/ROUGE-2/ROUGE-L F1 / 46.39/22.12/38.41 | Summarization / WikiHow / None / 46.39/22.12/38.41 |
| 7 | Abstractive Summarization / Reddit TIFU / ROUGE-1/ROUGE-2/ROUGE-L F1 / 27.99/9.81/22.94 | Summarization / Reddit TIFU / None / 27.99/9.81/22.94 |
| 8 | Abstractive Summarization / BIGPATENT / ROUGE-1/ROUGE-2/ROUGE-L F1 / 52.29/33.08/41.66 | Summarization / BIGPATENT / None / 52.29/33.08/41.66 |
| 9 | Abstractive Summarization / arXiv / ROUGE-1/ROUGE-2/ROUGE-L F1 / 44.21/16.95/25.67 | Summarization / arXiv / ROGUE-1 / 44.21/16.95/25.67 |
| 10 | Abstractive Summarization / PubMed / ROUGE-1/ROUGE-2/ROUGE-L F1 / 45.97/20.15/28.25 | Summarization / PubMed / None / 45.97/20.15/28.25 |
| 11 | Abstractive Summarization / AESLC / ROUGE-1/ROUGE-2/ROUGE-L F1 / 37.68/21.25/36.51 | Summarization / AESLC / None / 37.68/21.25/36.51 |
| 12 | Abstractive Summarization / BillSum / ROUGE-1/ROUGE-2/ROUGE-L F1 / 59.67/41.58/47.59 | Summarization / BillSum / None / 59.67/41.58/47.59 |
| 13 | Abstractive Summarization (Human Evaluation) / XSum / Likert Scale (1-5) / 3.2 | Summarization / XSum / None / 3.2 |
| 14 | Abstractive Summarization (Human Evaluation) / CNN/DailyMail / Likert Scale (1-5) / 3.4 | Summarization / CNN/DailyMail / None / 3.4 |
| 15 | Abstractive Summarization (Human Evaluation) / Reddit TIFU / Likert Scale (1-5) / 2.8 | Summarization / Reddit TIFU / None / 2.8 |