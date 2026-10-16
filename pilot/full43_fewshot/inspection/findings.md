# Few-shot 错误与变化核查

此文件只提供预测变化及冻结证据定位，不修正输出。Gold 对照见 evaluation/error_analysis.json。单凭数值未在 Gold 中出现不能认定为 Baseline；单凭字面字符串未命中证据也不能认定幻觉。

## C18-1139.pdf

TDMR F1 变化 +0.500000；条数 4 → 4；null 字段 2 → 0。

### 新预测 #1
```json
{"Task": "Named Entity Recognition", "Dataset": "CONLL03 English", "Metric": "F1-score", "Result": "93.09±0.12"}
```
证据 #6；metadata={"filename": "C18-1139.pdf", "page_number": 3, "type": "Table"}
```text
t conﬁguration of proposed architecture, and current best published results. The proposed approach signiﬁcantly outperforms previous work on the CONLL03 NER task for German and English and slightly outperforms previous works on CONLL2000 chunking and Penn treebank PoS tagging.
Task PROPOSED Previous best NER English NER German Chunking PoS tagging 93.09±0.12 88.32±0.2 96.72±0.05 97.85±0.01 92.22±0.1 (Peters et al., 2018) 78.76 (Lample et al., 2016) 96.37±0.05 (Peters et al., 2017) 97.64 (Choi, 2016)
```
证据 #7；metadata={"filename": "C18-1139.pdf", "page_number": 7, "type": "Table"}
```text
 task for reference. We signiﬁcantly outperform all previous works on NER, and slightly outperform the previous state-of-the-art in PoS tagging and chunking.
Approach NER-English F1-score NER-German F1-score Chunking F1-score POS Accuracy proposed PROPOSED PROPOSED+WORD PROPOSED+CHAR PROPOSED+WORD+CHAR PROPOSED+ALL 91.97±0.04 93.07±0.10 91.92±0.03 93.09±0.12 92.72±0.09 85.78 ± 0.18 88.20 ± 0.21 85.88 ± 0.20 88.32 ± 0.20 n/a 96.68±0.03 96.70±0.04 96.72±0.05 96.71±0.07 96.65±0.05 97.73±0.02 97.82±0.02 97.8±0.01 97.76±0.01 97.85±0.01 baselines HUANG LAMPLE PETERS 88.54±0.08 89.3±0.23 92.34±0.09 82.32 ± 0.35 83.78 ± 0.39 n/a 95.4±0.08 95.34±0.06 96.69±0.05 96.94±0.02 97.02±0.03 97.81± 0.02 best published 
```
### 新预测 #2
```json
{"Task": "Named Entity Recognition", "Dataset": "CONLL03 German", "Metric": "F1-score", "Result": "88.32±0.20"}
```
结果字面值未在证据中找到，需结合格式/比例进行人工判断。
## 1811.09242.pdf

TDMR F1 变化 +0.346154；条数 7 → 6；null 字段 3 → 2。

### 新预测 #1
```json
{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "F-S", "Result": "62.9"}
```
证据 #5；metadata={"filename": "1811.09242.pdf", "page_number": 5, "type": "Table"}
```text
(a) SemEval 2010 WSI dataset
Model LVMs NBEs LDA Spectral HC HC+Zipf BNP-HC CRP-PPMI SE-WSI-ﬁx AutoSense−wp AutoSense−sw AutoSense AutoSenses=5 AutoSenses=100 F-S 60.7 61.5 44.4 35.1 23.1 57.7 55.1 59.3 61.1 61.7 62.9 61.2 V-M AVG 16.34 4.4 16.64 4.5 22.62 11.5 23.10 15.2 21.4 22.23 12.94 2.9 23.24 9.8 23.36 9.2 22.92 8.6 24.59 9.8 25.20 10.1 24.23 9.6 δ(#S) 1.40 1.98 1.15 3.81 11.77 2.09 1.35 2.16 1.42 0.33 0.32 0.78
```
### 新预测 #2
```json
{"Task": "Word Sense Induction", "Dataset": "SemEval 2010 Task 14", "Metric": "V-M AVG", "Result": "25.20"}
```
证据 #5；metadata={"filename": "1811.09242.pdf", "page_number": 5, "type": "Table"}
```text
(a) SemEval 2010 WSI dataset
Model LVMs NBEs LDA Spectral HC HC+Zipf BNP-HC CRP-PPMI SE-WSI-ﬁx AutoSense−wp AutoSense−sw AutoSense AutoSenses=5 AutoSenses=100 F-S 60.7 61.5 44.4 35.1 23.1 57.7 55.1 59.3 61.1 61.7 62.9 61.2 V-M AVG 16.34 4.4 16.64 4.5 22.62 11.5 23.10 15.2 21.4 22.23 12.94 2.9 23.24 9.8 23.36 9.2 22.92 8.6 24.59 9.8 25.20 10.1 24.23 9.6 δ(#S) 1.40 1.98 1.15 3.81 11.77 2.09 1.35 2.16 1.42 0.33 0.32 0.78
```
### 新预测 #3
```json
{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "F-BC", "Result": "62.2"}
```
证据 #6；metadata={"filename": "1811.09242.pdf", "page_number": 5, "type": "Table"}
```text
w2v MCC AutoSense−wp AutoSense−sw AutoSense AutoSenses=7 AutoSenses=100 F-BC F-NMI 39.0 48.3 53.5 58.1 49.9 55.4 55.6 55.7 61.4 61.7 61.7 61.0 6.50 6.00 6.96 1.60 3.50 7.14 7.62 7.69 7.36 7.96 7.97 7.25 AVG 15.92 17.02 19.30 9.64 13.22 19.89 20.58 20.69 21.26 22.16 22.17 21.03 with additional contexts STM AutoSense +actual +ukWac +actual 59.1 54.5 62.2 9.39 9.74 9.55 23.56 23.04 24.37
```
### 新预测 #4
```json
{"Task": "Word Sense Induction", "Dataset": "SemEval 2013 Task 13", "Metric": "AVG", "Result": "24.37"}
```
证据 #6；metadata={"filename": "1811.09242.pdf", "page_number": 5, "type": "Table"}
```text
w AutoSense AutoSenses=7 AutoSenses=100 F-BC F-NMI 39.0 48.3 53.5 58.1 49.9 55.4 55.6 55.7 61.4 61.7 61.7 61.0 6.50 6.00 6.96 1.60 3.50 7.14 7.62 7.69 7.36 7.96 7.97 7.25 AVG 15.92 17.02 19.30 9.64 13.22 19.89 20.58 20.69 21.26 22.16 22.17 21.03 with additional contexts STM AutoSense +actual +ukWac +actual 59.1 54.5 62.2 9.39 9.74 9.55 23.56 23.04 24.37
```
### 新预测 #5
```json
{"Task": "Word Sense Induction", "Dataset": "Arnet", "Metric": "AVG", "Result": "58.8"}
```
证据 #9；metadata={"filename": "1811.09242.pdf", "page_number": 7, "type": "Table"}
```text
(a) Arnet Dataset
Model LDA HC STM AutoSense S = 5 S = 25 S = 50 S = 100 31.5 46.3 52.8 56.2 13.4 46.3 55.0 56.4 9.8 44.4 55.5 57.9 8.2 41.7 55.0 58.8
```
### 新预测 #6
```json
{"Task": "Word Sense Induction", "Dataset": "PubMed", "Metric": "AVG", "Result": "46.6"}
```
证据 #10；metadata={"filename": "1811.09242.pdf", "page_number": 7, "type": "Table"}
```text
(b) PubMed Dataset
Model LDA HC STM AutoSense S = 5 S = 25 S = 50 S = 100 41.4 42.5 44.9 44.4 13.3 44.1 44.4 45.5 8.9 41.6 44.9 46.6 9.0 41.3 41.9 46.5
```
## 1806.03489.pdf

TDMR F1 变化 +0.300000；条数 8 → 2；null 字段 1 → 1。

### 新预测 #1
```json
{"Task": "Named Entity Recognition", "Dataset": "CONLL-2003", "Metric": "F1", "Result": "91.73"}
```
证据 #12；metadata={"filename": "1806.03489.pdf", "page_number": 9, "type": "Table"}
```text
Table 7: F1 scores of differently trained systems on CONLL and ONTONOTES 5.0 datasets. Capitaliza- tion (Section 4.2.3) and character features (Section 4.2.2) are used by default by all models.
Model CONLL SSKIP LS all 90.52 (± 0.18) 89.94 (± 0.16) 91.73 (± 0.10) ONTONOTES 86.57 (± 0.10) 85.92 (± 0.12) 87.95 (± 0.13)
```
### 新预测 #2
```json
{"Task": "Named Entity Recognition", "Dataset": "ONTONOTES 5.0", "Metric": "F1", "Result": "87.95"}
```
证据 #10；metadata={"filename": "1806.03489.pdf", "page_number": 8, "type": "Table"}
```text
anning, 2009) + + (Ratinov and Roth, 2009) + (Passos et al., 2014) + (Durrett and Klein, 2014) • (Chiu and Nichols, 2016) • (Shen et al., 2017) • (Strubell et al., 2017) • This work LEX GAZ CAP EMB CHE LME LS F1 + + + + + • • + + + + + + + + + • • • • + + + + • • • • + + + + • • • • • • • • • 82.42 • 84.88 • 82.24 • 84.04 • 86.28 • 86.52 • 86.99 + 87.95
```
证据 #12；metadata={"filename": "1806.03489.pdf", "page_number": 9, "type": "Table"}
```text
Table 7: F1 scores of differently trained systems on CONLL and ONTONOTES 5.0 datasets. Capitaliza- tion (Section 4.2.3) and character features (Section 4.2.2) are used by default by all models.
Model CONLL SSKIP LS all 90.52 (± 0.18) 89.94 (± 0.16) 91.73 (± 0.10) ONTONOTES 86.57 (± 0.10) 85.92 (± 0.12) 87.95 (± 0.13)
```
## 128538.pdf

TDMR F1 变化 +0.250000；条数 4 → 4；null 字段 3 → 2。

### 新预测 #1
```json
{"Task": "Named Entity Recognition", "Dataset": "WNUT 2016", "Metric": "F1", "Result": "53.48"}
```
证据 #4；metadata={"filename": "128538.pdf", "page_number": 5, "start_index": 0, "type": "Text"}
```text
to, causing a considerable overlap with the geo-loc en- tity type. By contrast to earlier mentioned approaches, our system goes beyond the current state-of-the-art with 53.48% F1 score on WNUT 2016 without the need for external re- sources and additional data. Our benchmark with current systems is shown in Table 1. WNUT 2017 results. The challenge that WNUT 2017 data (Derczynski et al. 2017) poses is the more frequent use of punctuation (Derczynski et al. 2014). Often, part of the name is also a common word (e.g., Andr
```
证据 #5；metadata={"filename": "128538.pdf", "page_number": 4, "type": "Table"}
```text
 over 4 datasets and comparison with the current state-of-the-art.
Approaches (Partalas et al. 2016) (Limsopatham and Collier 2016) (von D¨aniken and Cieliebak 2017) (Zhang et al. 2018) (Aguilar et al. 2019) (Akbik, Bergmann, and Vollgraf 2019) (Baevski et al. 2019) (Wang et al. 2019) (Zhou et al. 2019) Ours WNUT 2016 46.16 52.41 - - - - - - 53.43 53.48 WNUT 2017 - - 40.78 - 45.55 49.59 - 50.03% - 50.52 CoNLL 2003 (Eng) - - - - 89.01 93.09 93.5 93.47 - 93.76 Multimodal - - - 70.69 - - - - - 74.17
```
### 新预测 #2
```json
{"Task": "Named Entity Recognition", "Dataset": "WNUT 2017", "Metric": "F1", "Result": "50.52"}
```
证据 #5；metadata={"filename": "128538.pdf", "page_number": 4, "type": "Table"}
```text
ate-of-the-art.
Approaches (Partalas et al. 2016) (Limsopatham and Collier 2016) (von D¨aniken and Cieliebak 2017) (Zhang et al. 2018) (Aguilar et al. 2019) (Akbik, Bergmann, and Vollgraf 2019) (Baevski et al. 2019) (Wang et al. 2019) (Zhou et al. 2019) Ours WNUT 2016 46.16 52.41 - - - - - - 53.43 53.48 WNUT 2017 - - 40.78 - 45.55 49.59 - 50.03% - 50.52 CoNLL 2003 (Eng) - - - - 89.01 93.09 93.5 93.47 - 93.76 Multimodal - - - 70.69 - - - - - 74.17
```
证据 #6；metadata={"filename": "128538.pdf", "page_number": 4, "type": "Table"}
```text
Table 2: This table describe the importance of each type of feature in combination to the other.
Combinations 2-Stacked Word BiLSTM 2-Stacked Word BiLSTM + Character 2-Stacked Word BiLSTM + Sentence All features WNUT 2016 47.64 (Baseline) 49.81 52.79 53.48 WNUT 2017 47.27 (Baseline) 48.13 49.87 50.52
```
### 新预测 #3
```json
{"Task": "Named Entity Recognition", "Dataset": "CoNLL 2003 (English)", "Metric": "F1", "Result": "93.76"}
```
证据 #5；metadata={"filename": "128538.pdf", "page_number": 4, "type": "Table"}
```text
patham and Collier 2016) (von D¨aniken and Cieliebak 2017) (Zhang et al. 2018) (Aguilar et al. 2019) (Akbik, Bergmann, and Vollgraf 2019) (Baevski et al. 2019) (Wang et al. 2019) (Zhou et al. 2019) Ours WNUT 2016 46.16 52.41 - - - - - - 53.43 53.48 WNUT 2017 - - 40.78 - 45.55 49.59 - 50.03% - 50.52 CoNLL 2003 (Eng) - - - - 89.01 93.09 93.5 93.47 - 93.76 Multimodal - - - 70.69 - - - - - 74.17
```
### 新预测 #4
```json
{"Task": "Named Entity Recognition (Multimodal)", "Dataset": "Multimodal", "Metric": "F1", "Result": "74.17"}
```
证据 #4；metadata={"filename": "128538.pdf", "page_number": 5, "start_index": 0, "type": "Text"}
```text
 predict entities such as creative-work and product compared to the current state-of-the-art. Multimodal results. So far, we only consider the tex- tual context. In this experiment, we evaluate our multi- modal approach that considers the auxiliary context from the text’s images. With segregated attention network, our model achieved an F1 score of 74.17% on this data which is a considerable improvement over the state-of-the-art model of (Zhang et al. 2018). In one of our experiments, we merged the textual and visual representation and observed
```
证据 #5；metadata={"filename": "128538.pdf", "page_number": 4, "type": "Table"}
```text
and Cieliebak 2017) (Zhang et al. 2018) (Aguilar et al. 2019) (Akbik, Bergmann, and Vollgraf 2019) (Baevski et al. 2019) (Wang et al. 2019) (Zhou et al. 2019) Ours WNUT 2016 46.16 52.41 - - - - - - 53.43 53.48 WNUT 2017 - - 40.78 - 45.55 49.59 - 50.03% - 50.52 CoNLL 2003 (Eng) - - - - 89.01 93.09 93.5 93.47 - 93.76 Multimodal - - - 70.69 - - - - - 74.17
```
## 1711.05568.pdf

TDMR F1 变化 -0.500000；条数 2 → 2；null 字段 0 → 1。

### 新预测 #1
```json
{"Task": "Dialogue Act Recognition", "Dataset": "SwDA", "Metric": "Accuracy", "Result": "81.3"}
```
证据 #9；metadata={"filename": "1711.05568.pdf", "page_number": 7, "type": "Table"}
```text
Table 5: Comparing Accuracy of our method (CRF-ASN) with other methods in the literature on SwDA dataset.
Model Human annotator Accuracy(%) 84.0 Ours (CRF-ASN) Bi-LSTM-CRF DRLM-Conditional LSTM-Softmax RCNN CNN CRF HMM SVM 81.3 79.2 77.0 75.8 73.9 73.1 71.7 71.0 70.6
```
证据 #11；metadata={"filename": "1711.05568.pdf", "page_number": 8, "type": "Table"}
```text
Table 7: Component ablations on SwDA dataset
Model Full CRF-ASN Simple CRF Simple SVM Simple Word Embedding Simple Context state Simple Memory Network Simple Utterance Embedding Accuracy(%) 81.3 79.5 77.8 78.7 79.1 78.3 79.0
```
### 新预测 #2
```json
{"Task": "Dialogue Act Recognition", "Dataset": "MRDA", "Metric": "Accuracy", "Result": "91.7"}
```
证据 #10；metadata={"filename": "1711.05568.pdf", "page_number": 7, "type": "Table"}
```text
Table 6: Comparing Accuracy of our method (CRF-ASN) with other methods in the literature on the MRDA dataset.
Model Ours (CRF-ASN) Bi-LSTM-CRF LSTM-Softmax CNN CRF SVM Accuracy(%) 91.7 90.9 86.8 84.6 83.9 82.0
```
## 1808.08745.pdf

TDMR F1 变化 -0.500000；条数 5 → 5；null 字段 2 → 4。

### 新预测 #1
```json
{"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "ROUGE-1", "Result": "31.89"}
```
证据 #7；metadata={"filename": "1808.08745.pdf", "page_number": 7, "type": "Table"}
```text
Table 4: ROUGE results on XSum test set. We re- port ROUGE-1 (R1), ROUGE-2 (R2), and ROUGE-L (RL) F1 scores. Extractive systems are in the upper block, RNN-based abstractive systems are in the mid- dle block, and convolutional abstractive systems are in the bottom block.
R1 15.16 16.30 29.79 28.42 29.70 28.10 31.27 31.71 31.71 31.61 31.89 R2 1.78 1.60 8.81 8.77 9.21 8.02 11.07 11.38 11.34 11.30 11.54 RL 11.27 11.95 22.66 22.48 23.24 21.72 25.23 25.56 25.61 25.51 25.75 Models Random LEAD EXT-ORACLE SEQ2SEQ PTGEN PTGEN-COVG CONVS2S T-CONVS2S (enct′ ) T-CONVS2S (enct′ , dectD ) T-CONVS2S (enc(t′,tD)) T-CONVS2S (enc(t′,tD), dectD )
```
### 新预测 #2
```json
{"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "ROUGE-2", "Result": "11.54"}
```
证据 #7；metadata={"filename": "1808.08745.pdf", "page_number": 7, "type": "Table"}
```text
port ROUGE-1 (R1), ROUGE-2 (R2), and ROUGE-L (RL) F1 scores. Extractive systems are in the upper block, RNN-based abstractive systems are in the mid- dle block, and convolutional abstractive systems are in the bottom block.
R1 15.16 16.30 29.79 28.42 29.70 28.10 31.27 31.71 31.71 31.61 31.89 R2 1.78 1.60 8.81 8.77 9.21 8.02 11.07 11.38 11.34 11.30 11.54 RL 11.27 11.95 22.66 22.48 23.24 21.72 25.23 25.56 25.61 25.51 25.75 Models Random LEAD EXT-ORACLE SEQ2SEQ PTGEN PTGEN-COVG CONVS2S T-CONVS2S (enct′ ) T-CONVS2S (enct′ , dectD ) T-CONVS2S (enc(t′,tD)) T-CONVS2S (enc(t′,tD), dectD )
```
### 新预测 #3
```json
{"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "ROUGE-L", "Result": "25.75"}
```
证据 #7；metadata={"filename": "1808.08745.pdf", "page_number": 7, "type": "Table"}
```text
ve systems are in the upper block, RNN-based abstractive systems are in the mid- dle block, and convolutional abstractive systems are in the bottom block.
R1 15.16 16.30 29.79 28.42 29.70 28.10 31.27 31.71 31.71 31.61 31.89 R2 1.78 1.60 8.81 8.77 9.21 8.02 11.07 11.38 11.34 11.30 11.54 RL 11.27 11.95 22.66 22.48 23.24 21.72 25.23 25.56 25.61 25.51 25.75 Models Random LEAD EXT-ORACLE SEQ2SEQ PTGEN PTGEN-COVG CONVS2S T-CONVS2S (enct′ ) T-CONVS2S (enct′ , dectD ) T-CONVS2S (enc(t′,tD)) T-CONVS2S (enc(t′,tD), dectD )
```
### 新预测 #4
```json
{"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "Human QA Accuracy", "Result": "46.05"}
```
证据 #1；metadata={"filename": "1808.08745.pdf", "page_number": 9, "start_index": 1802, "type": "Text"}
```text
cited using Amazon’s Mechanical Turk crowdsourcing platform. We uploaded the data in batches (one system at a time) to ensure that the same partic- ipant does not evaluate summaries from different systems on the same set of questions. Table 7 shows the results of the QA evaluation. Based on summaries generated by T-CONVS2S, participants can answer 46.05% of the questions correctly. Summaries generated by CONVS2S, PTGEN and EXT-ORACLE provide answers to 30.90%, 21.40%, and 15.70% of the questions, re- spectively. Pairwise differences between systems are all statistically signiﬁcant (p < 0.01) with the exception of PTGEN and EXT-ORACLE. EXT- ORACLE performs poorly on both QA and rating evaluations.
```
证据 #10；metadata={"filename": "1808.08745.pdf", "page_number": 9, "type": "Table"}
```text
Table 7: System ranking according to human judg- ments and QA-based evaluation.
Models EXT-ORACLE PTGEN CONVS2S T-CONVS2S GOLD Score -0.121 -0.218 -0.130 0.037 0.431 QA 15.70 21.40 30.90 46.05 97.23
```
### 新预测 #5
```json
{"Task": "Extreme Summarization", "Dataset": "XSum", "Metric": "Human Ranking Score", "Result": "0.037"}
```
证据 #10；metadata={"filename": "1808.08745.pdf", "page_number": 9, "type": "Table"}
```text
Table 7: System ranking according to human judg- ments and QA-based evaluation.
Models EXT-ORACLE PTGEN CONVS2S T-CONVS2S GOLD Score -0.121 -0.218 -0.130 0.037 0.431 QA 15.70 21.40 30.90 46.05 97.23
```
## 1811.05021.pdf

TDMR F1 变化 -0.500000；条数 2 → 2；null 字段 0 → 1。

## 1908.08345.pdf

TDMR F1 变化 -0.500000；条数 15 → 9；null 字段 6 → 9。

### 新预测 #1
```json
{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-1", "Result": "43.85"}
```
证据 #6；metadata={"filename": "1908.08345.pdf", "page_number": 6, "type": "Table"}
```text
 et al., 2017) PTGEN+COV (See et al., 2017) DRM (Paulus et al., 2018) BOTTOMUP (Gehrmann et al., 2018) DCA (Celikyilmaz et al., 2018) TransformerABS 36.44 15.66 33.42 39.53 17.28 36.38 39.87 15.82 36.90 41.22 18.68 38.34 41.69 19.47 37.92 40.21 17.76 37.09 BERT-based BERTSUMEXT 43.25 20.24 39.63 BERTSUMEXT w/o interval embeddings 43.20 20.22 39.59 43.85 20.34 39.90 BERTSUMEXT (large) 41.72 19.39 38.76 BERTSUMABS 42.13 19.60 39.18 BERTSUMEXTABS
```
### 新预测 #2
```json
{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-2", "Result": "20.34"}
```
证据 #6；metadata={"filename": "1908.08345.pdf", "page_number": 6, "type": "Table"}
```text
., 2017) PTGEN+COV (See et al., 2017) DRM (Paulus et al., 2018) BOTTOMUP (Gehrmann et al., 2018) DCA (Celikyilmaz et al., 2018) TransformerABS 36.44 15.66 33.42 39.53 17.28 36.38 39.87 15.82 36.90 41.22 18.68 38.34 41.69 19.47 37.92 40.21 17.76 37.09 BERT-based BERTSUMEXT 43.25 20.24 39.63 BERTSUMEXT w/o interval embeddings 43.20 20.22 39.59 43.85 20.34 39.90 BERTSUMEXT (large) 41.72 19.39 38.76 BERTSUMABS 42.13 19.60 39.18 BERTSUMEXTABS
```
### 新预测 #3
```json
{"Task": "Summarization", "Dataset": "CNN/DailyMail", "Metric": "ROUGE-L", "Result": "39.90"}
```
证据 #6；metadata={"filename": "1908.08345.pdf", "page_number": 6, "type": "Table"}
```text
7) PTGEN+COV (See et al., 2017) DRM (Paulus et al., 2018) BOTTOMUP (Gehrmann et al., 2018) DCA (Celikyilmaz et al., 2018) TransformerABS 36.44 15.66 33.42 39.53 17.28 36.38 39.87 15.82 36.90 41.22 18.68 38.34 41.69 19.47 37.92 40.21 17.76 37.09 BERT-based BERTSUMEXT 43.25 20.24 39.63 BERTSUMEXT w/o interval embeddings 43.20 20.22 39.59 43.85 20.34 39.90 BERTSUMEXT (large) 41.72 19.39 38.76 BERTSUMABS 42.13 19.60 39.18 BERTSUMEXTABS
```
### 新预测 #4
```json
{"Task": "Summarization", "Dataset": "NYT", "Metric": "ROUGE-1", "Result": "49.02"}
```
证据 #7；metadata={"filename": "1908.08345.pdf", "page_number": 7, "type": "Table"}
```text
 COMPRESS (Durrett et al., 2016) SUMO (Liu et al., 2019) TransformerEXT 42.20 42.30 41.95 24.90 — 22.70 22.68 38.60 38.51 Abstractive PTGEN (See et al., 2017) PTGEN + COV (See et al., 2017) DRM (Paulus et al., 2018) TransformerABS 42.47 43.71 42.94 35.75 25.61 — 26.40 — 26.02 — 17.23 31.41 BERT-based BERTSUMEXT BERTSUMABS BERTSUMEXTABS 46.66 48.92 49.02 26.35 30.84 31.02 42.62 45.41 45.55
```
### 新预测 #5
```json
{"Task": "Summarization", "Dataset": "NYT", "Metric": "ROUGE-2", "Result": "31.02"}
```
证据 #7；metadata={"filename": "1908.08345.pdf", "page_number": 7, "type": "Table"}
```text
 et al., 2016) SUMO (Liu et al., 2019) TransformerEXT 42.20 42.30 41.95 24.90 — 22.70 22.68 38.60 38.51 Abstractive PTGEN (See et al., 2017) PTGEN + COV (See et al., 2017) DRM (Paulus et al., 2018) TransformerABS 42.47 43.71 42.94 35.75 25.61 — 26.40 — 26.02 — 17.23 31.41 BERT-based BERTSUMEXT BERTSUMABS BERTSUMEXTABS 46.66 48.92 49.02 26.35 30.84 31.02 42.62 45.41 45.55
```
### 新预测 #6
```json
{"Task": "Summarization", "Dataset": "NYT", "Metric": "ROUGE-L", "Result": "45.55"}
```
证据 #7；metadata={"filename": "1908.08345.pdf", "page_number": 7, "type": "Table"}
```text
O (Liu et al., 2019) TransformerEXT 42.20 42.30 41.95 24.90 — 22.70 22.68 38.60 38.51 Abstractive PTGEN (See et al., 2017) PTGEN + COV (See et al., 2017) DRM (Paulus et al., 2018) TransformerABS 42.47 43.71 42.94 35.75 25.61 — 26.40 — 26.02 — 17.23 31.41 BERT-based BERTSUMEXT BERTSUMABS BERTSUMEXTABS 46.66 48.92 49.02 26.35 30.84 31.02 42.62 45.41 45.55
```
### 新预测 #7
```json
{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-1", "Result": "38.81"}
```
证据 #8；metadata={"filename": "1908.08345.pdf", "page_number": 7, "type": "Table"}
```text
n our data by run- ning publicly released software.
Model ORACLE LEAD R1 29.79 16.30 R2 RL 8.81 22.66 1.60 11.95 Abstractive PTGEN (See et al., 2017) PTGEN+COV (See et al., 2017) TCONVS2S (Narayan et al., 2018a) TransformerABS 9.21 23.24 29.70 28.10 8.02 21.72 31.89 11.54 25.75 9.77 23.01 29.41 BERT-based BERTSUMABS BERTSUMEXTABS 38.76 16.33 31.15 38.81 16.50 31.27
```
### 新预测 #8
```json
{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-2", "Result": "16.50"}
```
证据 #8；metadata={"filename": "1908.08345.pdf", "page_number": 7, "type": "Table"}
```text
data by run- ning publicly released software.
Model ORACLE LEAD R1 29.79 16.30 R2 RL 8.81 22.66 1.60 11.95 Abstractive PTGEN (See et al., 2017) PTGEN+COV (See et al., 2017) TCONVS2S (Narayan et al., 2018a) TransformerABS 9.21 23.24 29.70 28.10 8.02 21.72 31.89 11.54 25.75 9.77 23.01 29.41 BERT-based BERTSUMABS BERTSUMEXTABS 38.76 16.33 31.15 38.81 16.50 31.27
```
### 新预测 #9
```json
{"Task": "Summarization", "Dataset": "XSum", "Metric": "ROUGE-L", "Result": "31.27"}
```
证据 #8；metadata={"filename": "1908.08345.pdf", "page_number": 7, "type": "Table"}
```text
y run- ning publicly released software.
Model ORACLE LEAD R1 29.79 16.30 R2 RL 8.81 22.66 1.60 11.95 Abstractive PTGEN (See et al., 2017) PTGEN+COV (See et al., 2017) TCONVS2S (Narayan et al., 2018a) TransformerABS 9.21 23.24 29.70 28.10 8.02 21.72 31.89 11.54 25.75 9.77 23.01 29.41 BERT-based BERTSUMABS BERTSUMEXTABS 38.76 16.33 31.15 38.81 16.50 31.27
```

## 归因限制
Result 粒度、不同实验变体、Baseline 或 Dev/Test 混入仅在冻结证据有直接支持时作出判断。自动分析把无严格数值匹配、标准化 null、数值匹配但标签/绑定不同分别记录；不把这些类别互相等同。
原始 PDF 表格解析完全复用，因此本轮观察到的不同预测不意味着表格重新解析发生了变化。