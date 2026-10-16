# Partially 实际映射与疑似错误

所有结论来自冻结预测的离线分析；未修正答案。Gold相同数值并不保证同一实验，疑似可见实体错误保留此限制。

| 论文/序号 | 字段 | 原始 | 阶段一 | 阶段二 | 同值Gold名称 |
|---|---|---|---|---|---|
| 1905.03197.pdf/7 | Metric | BLEU-4 | BLEU-4 | BLEU-4 | ['METEOR'] |
| 2105.03654.pdf/1 | Metric | Accuracy | Accuracy | Accuracy | ['F1'] |
| 2105.03654.pdf/2 | Metric | Accuracy | Accuracy | Accuracy | ['F1'] |
| 2105.03654.pdf/3 | Metric | Accuracy | Accuracy | Accuracy | ['F1'] |
| 2105.03654.pdf/5 | Metric | Accuracy | Accuracy | Accuracy | ['F1'] |
| 2105.03654.pdf/7 | Metric | Accuracy | Accuracy | Accuracy | ['F1'] |
| 1910.13461.pdf/3 | Task | Natural Language Inference | Natural Language Inference (NLI) | Natural Language Inference (NLI) | ['Question Answering'] |
| 1910.13461.pdf/3 | Metric | Accuracy | Accuracy | Accuracy | ['F1'] |
| 1903.07785.pdf/3 | Task | MRPC (Microsoft Research Paraphrase Corpus) sentence similarity | Text Similarity | Text Similarity | ['Paraphrase Detection'] |
| 1811.09242.pdf/2 | Metric | V-Measure | V-Measure (V-M) | V-Measure (V-M) | ['AVG'] |
| 1812.09471.pdf/3 | Metric | Accuracy | Accuracy | Accuracy | ['Overall-Accuracy'] |
| 1812.09471.pdf/6 | Metric | Accuracy | Accuracy | Accuracy | ['Overall-Accuracy'] |

## 阶段二实际修改

| 论文/序号 | 阶段一 | 阶段二 | 严格Gold命中 |
|---|---|---|---|
| D18-1279.pdf/3 | Named Entity Recognition / CoNLL-2003 English / F1 / 91.64 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.64 | {'stage1': [], 'stage2': [1]} |
| 2020.emnlp-main.523.pdf/3 | Named Entity Recognition / CoNLL-2003 English / F1 / 94.3 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 94.3 | {'stage1': [], 'stage2': [7]} |
| 1702.02098.pdf/1 | Named Entity Recognition / CoNLL-2003 / F1 / 90.65 ± 0.15 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 90.65 ± 0.15 | {'stage1': [], 'stage2': []} |
| 1703.06345.pdf/3 | NER / CoNLL-2003 English / F1 / 91.26 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.26 | {'stage1': [], 'stage2': [1]} |
| 128538.pdf/1 | Named Entity Recognition / WNUT 2016 / F1 / 53.48 | Named Entity Recognition (NER) / WNUT-16 - English / F1 / 53.48 | {'stage1': [], 'stage2': [1]} |
| 1511.08308.pdf/1 | Named Entity Recognition / CoNLL-2003 / F1 / 91.62 | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.62 | {'stage1': [], 'stage2': [1]} |
| 1806.03489.pdf/1 | Named Entity Recognition / CoNLL-2003 / F1 / 91.73 (± 0.10) | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / 91.73 (± 0.10) | {'stage1': [], 'stage2': []} |
| 1908.08345.pdf/5 | Single-document news summarization (abstractive) / CNN/DailyMail / ROGUE-2 / 19.60 | Summarization / CNN/DailyMail / ROGUE-2 / 19.60 | {'stage1': [], 'stage2': []} |
| 1911.09483.pdf/1 | Machine Translation (English-German) / WMT’14 EN-DE / BLEU / 29.9 | Machine Translation / WMT’14 EN-DE / BLEU / 29.9 | {'stage1': [], 'stage2': [2]} |
| 1911.09483.pdf/2 | Machine Translation (English-French) / WMT’14 EN-FR / BLEU / 43.5 | Machine Translation / WMT’14 EN-FR / BLEU / 43.5 | {'stage1': [], 'stage2': [1]} |
| C18-1139.pdf/4 | Part-of-Speech (POS) Tagging / Penn Treebank / Accuracy / 97.85±0.01 | Part-of-Speech (POS) Tagging / Penn Treebank (PTB) / Accuracy / 97.85±0.01 | {'stage1': [], 'stage2': []} |
| D19-1367.pdf/3 | Named Entity Recognition / CoNLL-2003 English / F1 / Best result for I-DARTS (n = 1) (exact value not provided in the excerpt) | Named Entity Recognition (NER) / CoNLL-2003 - English / F1 / Best result for I-DARTS (n = 1) (exact value not provided in the excerpt) | {'stage1': [], 'stage2': []} |
| K19-1036.pdf/1 | Dialogue Act Classification / SWDA / Accuracy / 82.3 | Dialogue Act Classification / Switchboard Dialog Act Corpus (SWDA) / Accuracy / 82.3 | {'stage1': [], 'stage2': [1]} |
| K19-1036.pdf/2 | Dialogue Act Classification / MRDA / Accuracy / 92.2 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 92.2 | {'stage1': [], 'stage2': [2]} |
| N19-1373.pdf/2 | Dialogue Act Classification / MRDA / Accuracy / 89.2 | Dialogue Act Classification / ICSI Meeting Recorder Dialog Act Corpus (MRDA) / Accuracy / 89.2 | {'stage1': [], 'stage2': []} |
