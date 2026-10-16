# ExSciLead: Exhaustive Scientific Leaderboard Dataset 

This dataset is proposed in manuscript named "Efficient Scientific Progress Tracking: Leveraging Large Language Models for Automated Generation of Scientific Leaderboards". The dataset consist of Task, Dataset, Metric and Result (TDMR) information from scientific papers along with a leaderboard dataset constructed based on TDMR information.

## Content

```tdm_annotations.tsv```: TSV file containing Task, Dataset, Metric and Result values from selected scientific papers. This file also contains URLs of papers. 

```tdm_annotations.json```: JSON version of ```tdm_annotations.tsv```.

```leaderboards.json```: JSON file containing leaderboards constructed by grouping the papers with the same Task, Dataset, Metric tuples. The corresponding result values of the grouped papers are added to the leaderboards. Threshold for minimum number of values for a leaderboard is 3. Therefore, not every data e instance of ```tdm_annotations.tsv``` has to belong to a leaderboard. Similarly, a paper can belong to different leaderboards with different results obtained for different tasks.

## Dataset Statistics

| Dataset item              | Counts |
|---------------------------|--------|
| Papers                    | 43     |
| Leaderboards              | 27     |
| Avg. papers / leaderboard | 5.19   |
| TDMRs                     | 295    |
| Unique tasks              | 23     |
| Unique datasets           | 71     |
| Unique metrics            | 26     |