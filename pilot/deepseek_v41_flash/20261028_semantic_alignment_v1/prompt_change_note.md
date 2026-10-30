# 本轮补充要求（Semantic alignment v1）

用户已授权补充需求并重跑 Partially 与 Cold Start。本轮固定这一版，不根据结果追加修改。

## 修改范围

- 第一阶段动态实体匹配：按语义和实体身份比较，识别明确缩写、别名、同义表达及表面拼写差异。
- 第二阶段排行榜匹配：联合比较 Task、Dataset、Metric，不要求字符串相等；匹配后逐字返回候选 tuple。
- 保留数据集、语言、版本、split和指标定义差异；候选不唯一或无法确认时保留输入。
- 不添加任何论文示例、Gold答案或新上下文；原版接受规则和未匹配处理保持不变。
- 第一阶段 Partially 的 Metric 继续使用原 normalization-system-prompt。
- 复用295条原始DeepSeek预测；四个分支都从各自原始初始集合重跑两阶段，不复用旧标准化响应。

## 固定追加文本

### masked-normalization-system-prompt

```text
Semantic matching requirements:
Match by meaning and entity identity, not by literal string equality. Recognize unambiguous abbreviations, acronyms, aliases, paraphrases, capitalization, punctuation and superficial spelling differences. Different wording alone is not a reason to reject a match. Compare the input against the supplied candidates before deciding that it is a new entity.
For task names, a more specific wording may match an existing standard task when both denote the same underlying task. Preserve meaningful differences in dataset identity, language, version, split and metric definition; do not merge distinct entities merely because their names are similar. Do not guess an ambiguous abbreviation or missing experimental condition.
If one candidate is a clear semantic match, output that candidate exactly as written in the item list. If the list is empty, no candidate matches, or the match remains ambiguous, output the original input entity exactly unchanged. Do not invent a new canonical name. Output only the selected item or unchanged input, without quotes, explanation or extra formatting.
```

### leaderboard-normalization-system-prompt

```text
Semantic matching requirements:
Here, a tuple matches a listed tuple when its Task, Dataset and Metric denote the same underlying benchmark, even if their strings differ. This is semantic alignment, not an exact-string membership test. Compare all three fields jointly. Recognize unambiguous abbreviations, acronyms, aliases, paraphrases, capitalization, punctuation and superficial spelling differences, using the information in the input tuple and candidate tuples to disambiguate.
A more specific task wording may match a broader standard task label when they describe the same underlying benchmark and the Dataset and Metric remain compatible. Do not merge different dataset identities, languages, versions, splits or metric definitions. Missing details must not be guessed when multiple candidates remain plausible. Similar names alone do not establish equivalence.
If one listed tuple is a clear semantic match, return the entire listed tuple verbatim, with its exact spelling, punctuation and spacing. Never mix fields from different candidates. If no candidate matches or the match remains ambiguous, return the original input tuple verbatim. Output only that one tuple, without quotes, explanation, code fences or extra formatting.
```
