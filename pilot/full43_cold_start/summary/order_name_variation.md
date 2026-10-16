# 同一记录位置在三个顺序下的名称变化

按相同 paper_id + record_index + field 比较，输入抽取不变；不把所有名称差异判为语义错误。模型服务也可能有随机性，不能只归因于排序。

| 论文/记录 | 字段 | 原始名称 | 阶段 | default | 种子字符串 0 | 种子字符串 42 |
| --- | --- | --- | --- | --- | --- | --- |
| 1709.04109.pdf/1 | Metric | F1 score | stage1 | F1 score | F1 score | F1 Score |
| 1709.04109.pdf/1 | Metric | F1 score | stage2 | F1 score | F1 score | F1 Score |
| D18-1279.pdf/1 | Dataset | CoNLL-2002 Spanish | stage1 | CoNLL-2002 Spanish | CoNLL 2002 Spanish | CoNLL 2002 Spanish |
| D18-1279.pdf/1 | Dataset | CoNLL-2002 Spanish | stage2 | CoNLL-2002 Spanish | CoNLL 2002 Spanish | CoNLL 2002 Spanish |
| D18-1279.pdf/2 | Dataset | CoNLL-2002 Dutch | stage1 | CoNLL-2002 Dutch | CoNLL 2002 Dutch | CoNLL 2002 Dutch |
| D18-1279.pdf/2 | Dataset | CoNLL-2002 Dutch | stage2 | CoNLL-2002 Dutch | CoNLL 2002 Dutch | CoNLL 2002 Dutch |
| D18-1279.pdf/5 | Dataset | CoNLL-2000 | stage1 | CoNLL-2000 | CoNLL-2000 | None |
| D18-1279.pdf/5 | Dataset | CoNLL-2000 | stage2 | CoNLL-2000 | CoNLL-2000 | None |
| D18-1279.pdf/6 | Dataset | Penn Treebank WSJ | stage1 | WSJ | Penn Treebank WSJ | Penn Treebank (WSJ) |
| D18-1279.pdf/6 | Dataset | Penn Treebank WSJ | stage2 | WSJ | Penn Treebank WSJ | Penn Treebank (WSJ) |
| 2020.emnlp-main.523.pdf/3 | Task | Named Entity Recognition | stage2 | Named Entity Recognition | Named Entity Recognition (NER) | Named Entity Recognition (NER) |
| 2020.emnlp-main.523.pdf/3 | Dataset | CoNLL-2003 | stage1 | CoNLL-2003 English | CoNLL-2003 | CoNLL-2003 |
| 2020.emnlp-main.523.pdf/3 | Dataset | CoNLL-2003 | stage2 | CoNLL-2003 English | CoNLL-2003 - English | CoNLL-2003 - English |
| 2105.03654.pdf/8 | Dataset | CoNLL-03 (train) → CBS SciTech News (test) | stage1 | CoNLL-03 | CoNLL-03 (train) → CBS SciTech News (test) | CoNLL-03 (train) → CBS SciTech News (test) |
| 2105.03654.pdf/8 | Dataset | CoNLL-03 (train) → CBS SciTech News (test) | stage2 | CoNLL-03 | CoNLL-03 (train) → CBS SciTech News (test) | CoNLL-03 (train) → CBS SciTech News (test) |
| 1910.13461.pdf/4 | Metric | ROUGE-1 | stage1 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 1910.13461.pdf/4 | Metric | ROUGE-1 | stage2 | ROGUE-1 | Rouge-1 | ROGUE-1 |
| 1910.13461.pdf/5 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 1910.13461.pdf/7 | Metric | ROUGE-1 | stage1 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 1910.13461.pdf/7 | Metric | ROUGE-1 | stage2 | ROGUE-1 | Rouge-1 | ROGUE-1 |
| 1910.13461.pdf/8 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 1910.13461.pdf/8 | Metric | ROUGE-2 | stage2 | ROGUE-2 | Rouge-2 | ROGUE-2 |
| 1910.13461.pdf/12 | Metric | ROUGE-1 | stage1 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 1910.13461.pdf/12 | Metric | ROUGE-1 | stage2 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 1910.13461.pdf/13 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 1910.13461.pdf/13 | Metric | ROUGE-2 | stage2 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| D18-1105.pdf/1 | Task | Dialog Act Classification | stage1 | Dialog Act Classification | Dialog Act Classification | Dialogue Act Classification |
| D18-1105.pdf/1 | Task | Dialog Act Classification | stage2 | Dialog Act Classification | Dialog Act Classification | Dialogue Act Classification |
| D18-1105.pdf/2 | Task | Dialog Act Classification | stage1 | Dialog Act Classification | Dialog Act Classification | Dialogue Act Classification |
| D18-1105.pdf/2 | Task | Dialog Act Classification | stage2 | Dialog Act Classification | Dialog Act Classification | Dialogue Act Classification |
| D18-1105.pdf/2 | Dataset | MRDA | stage2 | MRDA | MRDA | ICSI Meeting Recorder Dialog Act Corpus (MRDA) |
| 1703.06345.pdf/2 | Dataset | CoNLL 2000 | stage1 | CoNLL-2000 | CoNLL 2000 | CONLL2000 |
| 1703.06345.pdf/2 | Dataset | CoNLL 2000 | stage2 | CoNLL-2000 | CoNLL 2000 | CONLL2000 |
| 1703.06345.pdf/3 | Task | NER | stage2 | Named Entity Recognition (NER) | Named Entity Recognition (NER) | NER |
| 1703.06345.pdf/3 | Dataset | CoNLL 2003 English | stage1 | CoNLL-2003 English | CoNLL-2003 English | CoNLL 2003 English |
| 1703.06345.pdf/3 | Dataset | CoNLL 2003 English | stage2 | CoNLL-2003 - English | CoNLL-2003 - English | CoNLL 2003 English |
| 1703.06345.pdf/4 | Dataset | CoNLL 2002 Spanish | stage1 | CoNLL-2002 Spanish | CoNLL 2002 Spanish | CoNLL 2002 Spanish |
| 1703.06345.pdf/4 | Dataset | CoNLL 2002 Spanish | stage2 | CoNLL-2002 Spanish | CoNLL 2002 Spanish | CoNLL 2002 Spanish |
| 1703.06345.pdf/5 | Dataset | CoNLL 2002 Dutch | stage1 | CoNLL-2002 Dutch | CoNLL 2002 Dutch | CoNLL 2002 Dutch |
| 1703.06345.pdf/5 | Dataset | CoNLL 2002 Dutch | stage2 | CoNLL-2002 Dutch | CoNLL 2002 Dutch | CoNLL 2002 Dutch |
| 1903.07785.pdf/6 | Task | MNLI-m (Multi-Genre Natural Language Inference - matched) | stage1 | MNLI-m (Multi-Genre Natural Language Inference - matched) | MNLI-m (Multi-Genre Natural Language Inference - matched) | Natural Language Inference |
| 1903.07785.pdf/6 | Task | MNLI-m (Multi-Genre Natural Language Inference - matched) | stage2 | MNLI-m (Multi-Genre Natural Language Inference - matched) | MNLI-m (Multi-Genre Natural Language Inference - matched) | Natural Language Inference |
| 1912.08777.pdf/1 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 | stage1 | ROUGE-1 | ROUGE-1/ROUGE-2/ROUGE-L F1 | ROUGE-1/ROUGE-2/ROUGE-L F1 |
| 1912.08777.pdf/1 | Metric | ROUGE-1/ROUGE-2/ROUGE-L F1 | stage2 | ROUGE-1 | ROUGE-1/ROUGE-2/ROUGE-L F1 | ROUGE-1/ROUGE-2/ROUGE-L F1 |
| 1912.08777.pdf/13 | Task | Abstractive Summarization (Human Evaluation) | stage1 | Abstractive Summarization | Abstractive Summarization (Human Evaluation) | Abstractive Summarization (Human Evaluation) |
| 1912.08777.pdf/13 | Task | Abstractive Summarization (Human Evaluation) | stage2 | Abstractive Summarization | Abstractive Summarization (Human Evaluation) | Abstractive Summarization (Human Evaluation) |
| 1912.08777.pdf/14 | Task | Abstractive Summarization (Human Evaluation) | stage1 | Abstractive Summarization | Abstractive Summarization (Human Evaluation) | Abstractive Summarization (Human Evaluation) |
| 1912.08777.pdf/14 | Task | Abstractive Summarization (Human Evaluation) | stage2 | Abstractive Summarization | Abstractive Summarization (Human Evaluation) | Abstractive Summarization (Human Evaluation) |
| 1912.08777.pdf/15 | Task | Abstractive Summarization (Human Evaluation) | stage1 | Abstractive Summarization | Abstractive Summarization (Human Evaluation) | Abstractive Summarization (Human Evaluation) |
| 1912.08777.pdf/15 | Task | Abstractive Summarization (Human Evaluation) | stage2 | Abstractive Summarization | Abstractive Summarization (Human Evaluation) | Abstractive Summarization (Human Evaluation) |
| wang19f.pdf/1 | Dataset | Penn Treebank (PTB) | stage1 | PTB | Penn Treebank (PTB) | Penn Treebank (PTB) |
| wang19f.pdf/1 | Dataset | Penn Treebank (PTB) | stage2 | PTB | Penn Treebank (PTB) | Penn Treebank (PTB) |
| wang19f.pdf/4 | Dataset | WMT2014 English→German | stage1 | WMT2014 English→German | WMT2014 English→German | WMT'14 En→De |
| wang19f.pdf/4 | Dataset | WMT2014 English→German | stage2 | WMT2014 English→German | WMT2014 English→German | WMT'14 En→De |
| wang19f.pdf/5 | Dataset | IWSLT2014 German→English | stage1 | IWSLT2014 German→English | IWSLT 2014 De-En | IWSLT2014 German→English |
| wang19f.pdf/5 | Dataset | IWSLT2014 German→English | stage2 | IWSLT2014 German→English | IWSLT 2014 De-En | IWSLT2014 German→English |
| 128538.pdf/1 | Task | Named Entity Recognition | stage2 | Named Entity Recognition | Named Entity Recognition | Named Entity Recognition (NER) |
| 128538.pdf/1 | Dataset | WNUT 2016 | stage1 | WNUT 2016 | WNUT 2016 | WNUT-16 |
| 128538.pdf/1 | Dataset | WNUT 2016 | stage2 | WNUT 2016 | WNUT 2016 | WNUT-16 - English |
| 128538.pdf/1 | Metric | F1 score | stage2 | F1 score | F1 score | F1 |
| 128538.pdf/2 | Task | Named Entity Recognition | stage2 | Named Entity Recognition | Named Entity Recognition | Named Entity Recognition (NER) |
| 128538.pdf/2 | Dataset | WNUT 2017 | stage1 | WNUT 2017 | WNUT 2017 | WNUT-17 |
| 128538.pdf/2 | Dataset | WNUT 2017 | stage2 | WNUT 2017 | WNUT 2017 | WNUT-17 - English |
| 128538.pdf/2 | Metric | F1 score | stage2 | F1 score | F1 score | F1 |
| 1511.08308.pdf/1 | Task | Named Entity Recognition | stage2 | Named Entity Recognition (NER) | Named Entity Recognition | Named Entity Recognition (NER) |
| 1511.08308.pdf/1 | Dataset | CoNLL-2003 | stage2 | CoNLL-2003 - English | CoNLL-2003 | CoNLL-2003 - English |
| 1603.01354.pdf/1 | Dataset | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) | stage1 | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) | Penn Treebank (WSJ) | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) |
| 1603.01354.pdf/1 | Dataset | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) | stage2 | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) | Penn Treebank (WSJ) | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) |
| 1603.01354.pdf/2 | Dataset | CoNLL 2003 English | stage1 | CoNLL-2003 English | CoNLL-2003 English | CoNLL 2003 English |
| 1603.01354.pdf/2 | Dataset | CoNLL 2003 English | stage2 | CoNLL-2003 English | CoNLL-2003 English | CoNLL 2003 English |
| 1806.03489.pdf/1 | Dataset | CONLL-2003 | stage1 | CONLL-2003 | CoNLL-2003 | CoNLL-2003 |
| 1806.03489.pdf/1 | Dataset | CONLL-2003 | stage2 | CONLL-2003 | CoNLL-2003 | CoNLL-2003 |
| 1806.03489.pdf/2 | Dataset | ONTONOTES 5.0 | stage1 | ONTONOTES 5.0 | OntoNotes 5.0 | ONTONOTES 5.0 |
| 1806.03489.pdf/2 | Dataset | ONTONOTES 5.0 | stage2 | ONTONOTES 5.0 | OntoNotes 5.0 | ONTONOTES 5.0 |
| 1806.03489.pdf/3 | Dataset | ONTONOTES 5.0 (Broadcast Conversation genre) | stage1 | ONTONOTES 5.0 | ONTONOTES 5.0 (Broadcast Conversation genre) | ONTONOTES 5.0 |
| 1806.03489.pdf/3 | Dataset | ONTONOTES 5.0 (Broadcast Conversation genre) | stage2 | ONTONOTES 5.0 | ONTONOTES 5.0 (Broadcast Conversation genre) | ONTONOTES 5.0 |
| 1809.08370.pdf/2 | Task | Text Chunking | stage1 | Text Chunking | Text Chunking | Chunking |
| 1809.08370.pdf/2 | Task | Text Chunking | stage2 | Text Chunking | Text Chunking | Chunking |
| 1809.08370.pdf/2 | Dataset | CoNLL-2000 | stage1 | CoNLL-2000 | CoNLL-2000 | CONLL2000 |
| 1809.08370.pdf/2 | Dataset | CoNLL-2000 | stage2 | CoNLL-2000 | CoNLL-2000 | CONLL2000 |
| 1809.08370.pdf/3 | Dataset | CoNLL-2003 | stage2 | CoNLL-2003 | CoNLL-2003 - English | CoNLL-2003 |
| 1809.08370.pdf/5 | Dataset | Penn Treebank (WSJ) | stage1 | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) | Penn Treebank (WSJ) | Penn Treebank (WSJ) |
| 1809.08370.pdf/5 | Dataset | Penn Treebank (WSJ) | stage2 | Wall Street Journal (WSJ) portion of Penn Treebank (PTB) | Penn Treebank (WSJ) | Penn Treebank (WSJ) |
| 1811.09242.pdf/1 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/1 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/2 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/2 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/3 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/3 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/4 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/4 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/5 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/5 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/6 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/6 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/7 | Task | Word Sense Induction | stage1 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1811.09242.pdf/7 | Task | Word Sense Induction | stage2 | Word Sense Induction | Word Sense Induction | Word Sense Induction (WSI) |
| 1901.10430.pdf/1 | Dataset | WMT English-German (newstest2014) | stage1 | WMT2014 English→German | WMT2014 English→German | None |
| 1901.10430.pdf/1 | Dataset | WMT English-German (newstest2014) | stage2 | WMT2014 English→German | WMT2014 English→German | None |
| 1901.10430.pdf/2 | Dataset | WMT English-French (newstest2014) | stage1 | WMT English-French (newstest2014) | WMT English-French (newstest2014) | None |
| 1901.10430.pdf/2 | Dataset | WMT English-French (newstest2014) | stage2 | WMT English-French (newstest2014) | WMT English-French (newstest2014) | None |
| 1901.10430.pdf/3 | Dataset | IWSLT'14 German-English | stage1 | IWSLT'14 German-English | IWSLT 2014 De-En | IWSLT'14 German-English |
| 1901.10430.pdf/3 | Dataset | IWSLT'14 German-English | stage2 | IWSLT'14 German-English | IWSLT 2014 De-En | IWSLT'14 German-English |
| 1901.10430.pdf/6 | Dataset | CNN-DailyMail | stage1 | CNN/DailyMail | CNN-DailyMail | CNN/DailyMail |
| 1901.10430.pdf/6 | Dataset | CNN-DailyMail | stage2 | CNN/DailyMail | CNN-DailyMail | CNN/DailyMail |
| 1901.10430.pdf/6 | Metric | Rouge-1 | stage2 | Rouge-1 | Rouge-1 | ROGUE-1 |
| 1901.10430.pdf/7 | Dataset | CNN-DailyMail | stage1 | CNN/DailyMail | CNN-DailyMail | CNN/DailyMail |
| 1901.10430.pdf/7 | Dataset | CNN-DailyMail | stage2 | CNN/DailyMail | CNN-DailyMail | CNN/DailyMail |
| 1901.10430.pdf/7 | Metric | Rouge-2 | stage2 | ROGUE-2 | Rouge-2 | ROGUE-2 |
| 1901.10430.pdf/8 | Dataset | CNN-DailyMail | stage1 | CNN/DailyMail | CNN-DailyMail | CNN/DailyMail |
| 1901.10430.pdf/8 | Dataset | CNN-DailyMail | stage2 | CNN/DailyMail | CNN-DailyMail | CNN/DailyMail |
| 1901.10430.pdf/8 | Metric | Rouge-L | stage1 | Rouge-L | ROUGE-L | ROUGE-L |
| 1901.10430.pdf/8 | Metric | Rouge-L | stage2 | ROGUE-L | ROUGE-L | ROGUE-L |
| 1906.05012.pdf/1 | Metric | ROUGE-1 | stage1 | ROUGE-1 | ROUGE-L | ROUGE-1 |
| 1906.05012.pdf/1 | Metric | ROUGE-1 | stage2 | ROUGE-1 | ROUGE-L | ROUGE-1 |
| 1906.05012.pdf/2 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 1906.05012.pdf/2 | Metric | ROUGE-2 | stage2 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 1909.02188.pdf/1 | Dataset | SNIPS | stage1 | Snips | SNIPS | Snips |
| 1909.02188.pdf/1 | Dataset | SNIPS | stage2 | Snips | SNIPS | Snips |
| 1909.02188.pdf/2 | Dataset | SNIPS | stage1 | Snips | SNIPS | Snips |
| 1909.02188.pdf/2 | Dataset | SNIPS | stage2 | Snips | SNIPS | Snips |
| 1909.02188.pdf/3 | Dataset | SNIPS | stage1 | Snips | SNIPS | Snips |
| 1909.02188.pdf/3 | Dataset | SNIPS | stage2 | Snips | SNIPS | Snips |
| 1911.09483.pdf/1 | Task | Machine Translation (English-German) | stage1 | Machine Translation (English-German) | Machine Translation | Machine Translation (English-German) |
| 1911.09483.pdf/1 | Task | Machine Translation (English-German) | stage2 | Machine Translation (English-German) | Machine Translation | Machine Translation (English-German) |
| 1911.09483.pdf/1 | Dataset | WMT14 En-De | stage1 | WMT14 En-De | WMT14 En-De | WMT'14 En→De |
| 1911.09483.pdf/1 | Dataset | WMT14 En-De | stage2 | WMT14 En-De | WMT14 En-De | WMT'14 En→De |
| 1911.09483.pdf/2 | Task | Machine Translation (English-French) | stage1 | Neural Machine Translation (English to French) | Machine Translation (English-French) | Machine Translation (English-French) |
| 1911.09483.pdf/2 | Task | Machine Translation (English-French) | stage2 | Neural Machine Translation (English to French) | Machine Translation (English-French) | Machine Translation (English-French) |
| 1911.09483.pdf/2 | Dataset | WMT14 En-Fr | stage1 | WMT14 En-Fr | WMT14 En-Fr | WMT'14 En→Fr |
| 1911.09483.pdf/2 | Dataset | WMT14 En-Fr | stage2 | WMT14 En-Fr | WMT14 En-Fr | WMT'14 En→Fr |
| 1911.10390.pdf/1 | Metric | ROUGE-1 | stage1 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 1911.10390.pdf/1 | Metric | ROUGE-1 | stage2 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 1911.10390.pdf/2 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 1911.10390.pdf/2 | Metric | ROUGE-2 | stage2 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 2001.04063.pdf/1 | Metric | ROUGE-1 | stage1 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 2001.04063.pdf/1 | Metric | ROUGE-1 | stage2 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 2001.04063.pdf/2 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 2001.04063.pdf/2 | Metric | ROUGE-2 | stage2 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 2001.04063.pdf/4 | Metric | ROUGE-1 | stage1 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 2001.04063.pdf/4 | Metric | ROUGE-1 | stage2 | ROUGE-1 | Rouge-1 | ROUGE-1 |
| 2001.04063.pdf/5 | Metric | ROUGE-2 | stage1 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 2001.04063.pdf/5 | Metric | ROUGE-2 | stage2 | ROUGE-2 | Rouge-2 | ROUGE-2 |
| 2002.03184.pdf/5 | Dataset | CNN-DailyMail | stage1 | CNN/DailyMail | CNN-DailyMail | CNN-DailyMail |
| 2002.03184.pdf/5 | Dataset | CNN-DailyMail | stage2 | CNN/DailyMail | CNN-DailyMail | CNN-DailyMail |
| 2002.03184.pdf/6 | Dataset | CNN-DailyMail | stage1 | CNN/DailyMail | CNN-DailyMail | CNN-DailyMail |
| 2002.03184.pdf/6 | Dataset | CNN-DailyMail | stage2 | CNN/DailyMail | CNN-DailyMail | CNN-DailyMail |
| 2002.03184.pdf/6 | Metric | Rouge-L | stage1 | Rouge-L | ROUGE-L | Rouge-L |
| 2002.03184.pdf/6 | Metric | Rouge-L | stage2 | Rouge-L | ROUGE-L | Rouge-L |
| 2002.03184.pdf/7 | Dataset | WikiText-103 | stage1 | Wikitext-103 (WT103) | WikiText-103 | Wikitext-103 (WT103) |
| 2002.03184.pdf/7 | Dataset | WikiText-103 | stage2 | Wikitext-103 (WT103) | WikiText-103 | Wikitext-103 (WT103) |
| 2008.07772.pdf/1 | Dataset | WMT'14 English-French | stage1 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/1 | Dataset | WMT'14 English-French | stage2 | WMT’14 EN-FR | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/2 | Dataset | WMT'14 English-French | stage1 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/2 | Dataset | WMT'14 English-French | stage2 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/3 | Dataset | WMT'14 English-French | stage1 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/3 | Dataset | WMT'14 English-French | stage2 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/4 | Dataset | WMT'14 English-German | stage1 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/4 | Dataset | WMT'14 English-German | stage2 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/5 | Dataset | WMT'14 English-German | stage1 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/5 | Dataset | WMT'14 English-German | stage2 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/6 | Dataset | WMT'14 English-German | stage1 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/6 | Dataset | WMT'14 English-German | stage2 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/7 | Dataset | WMT'14 English-French | stage1 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/7 | Dataset | WMT'14 English-French | stage2 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/7 | Metric | BLEU (sacreBLEU.py) | stage1 | BLEU (sacreBLEU.py) | BLEU | BLEU (sacreBLEU.py) |
| 2008.07772.pdf/7 | Metric | BLEU (sacreBLEU.py) | stage2 | BLEU (sacreBLEU.py) | BLEU | BLEU (sacreBLEU.py) |
| 2008.07772.pdf/8 | Dataset | WMT'14 English-German | stage1 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/8 | Dataset | WMT'14 English-German | stage2 | WMT'14 English-German | WMT14 En-De | WMT'14 English-German |
| 2008.07772.pdf/8 | Metric | BLEU (sacreBLEU.py) | stage1 | BLEU (sacreBLEU.py) | BLEU | BLEU (sacreBLEU.py) |
| 2008.07772.pdf/8 | Metric | BLEU (sacreBLEU.py) | stage2 | BLEU (sacreBLEU.py) | BLEU | BLEU (sacreBLEU.py) |
| 2008.07772.pdf/9 | Dataset | WMT'14 English-French | stage1 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/9 | Dataset | WMT'14 English-French | stage2 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/9 | Metric | BLEU (multi-bleu.perl) | stage1 | BLEU (multi-bleu.perl) | BLEU | BLEU (multi-bleu.perl) |
| 2008.07772.pdf/9 | Metric | BLEU (multi-bleu.perl) | stage2 | BLEU (multi-bleu.perl) | BLEU | BLEU (multi-bleu.perl) |
| 2008.07772.pdf/10 | Dataset | WMT'14 English-French | stage1 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/10 | Dataset | WMT'14 English-French | stage2 | WMT'14 English-French | WMT14 En-Fr | WMT'14 English-French |
| 2008.07772.pdf/10 | Metric | BLEU (sacreBLEU.py) | stage1 | BLEU (sacreBLEU.py) | BLEU | BLEU (sacreBLEU.py) |
| 2008.07772.pdf/10 | Metric | BLEU (sacreBLEU.py) | stage2 | BLEU (sacreBLEU.py) | BLEU | BLEU (sacreBLEU.py) |
| C18-1139.pdf/1 | Task | Named Entity Recognition (English) | stage1 | Named Entity Recognition (English) | Named Entity Recognition | Named Entity Recognition (English) |
| C18-1139.pdf/1 | Task | Named Entity Recognition (English) | stage2 | Named Entity Recognition (English) | Named Entity Recognition | Named Entity Recognition (English) |
| D19-1367.pdf/1 | Dataset | PTB (Penn Treebank) | stage1 | PTB (Penn Treebank) | Penn Treebank | PTB (Penn Treebank) |
| D19-1367.pdf/1 | Dataset | PTB (Penn Treebank) | stage2 | PTB (Penn Treebank) | Penn Treebank | PTB (Penn Treebank) |
| D19-1367.pdf/2 | Dataset | PTB (Penn Treebank) | stage1 | PTB (Penn Treebank) | Penn Treebank | PTB (Penn Treebank) |
| D19-1367.pdf/2 | Dataset | PTB (Penn Treebank) | stage2 | PTB (Penn Treebank) | Penn Treebank | PTB (Penn Treebank) |
| K19-1036.pdf/1 | Dataset | SWDA | stage1 | SwDA | SwDA | SWDA |
| K19-1036.pdf/1 | Dataset | SWDA | stage2 | SwDA | SwDA | Switchboard Dialog Act Corpus (SWDA) |
