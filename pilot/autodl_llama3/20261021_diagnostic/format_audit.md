# Llama-3 格式诊断（尚未批准正式处理）

结论：不是重复 Prompt 或包装器误切分。历史与新增每次 pipeline 原始文本都严格等于完整请求 Prompt + 作者包装后的响应；四个实例中的三个由模型自行生成说明性前缀。新增三篇均 EOS，未触及 1024 上限。

## 作者依据与边界

[冻结 README 第145行](https://github.com/UKPLab/emnlp2024-leaderboard-generation/blob/8bf74b0a830feb7035c6166dce3394dc344ae532/README.md#L145) 允许标准化前使用格式纠正后的输出，但未规定算法、白名单或人工修改界限。官方 tdm_extraction.py 原样保存模型字符串；tdm_llm_normalization.py 直接 json.loads，然后对 Result 使用 str()。因此数字 Result 不必在适配层手动转换。原 Prompt 的示例使用字符串，但源码能接受有限 JSON 数值。

已有 author_hf_pipeline.py 是作者固定 community 0.0.20 模块的逐字节副本，SHA256 为 6716e012f55d006674dc320b4204015024a5f776fdaefbfe6c55fbbff3136d7c。它只恢复原版对返回输入 Prompt 的移除，不删除生成的说明前缀。已实测完整文本等式，未重复套 chat template。

43 个实际 RetrievalQA Prompt 与独立渲染一致；每篇仅一个 begin_of_text、三段 header。实际 pipeline add_special_tokens=False，Llama-3 tokenizer 的 BOS=128000、EOS=128009；作者加载后添加 pad=128256。生成的 EOS 配置为 [128001,128009]，实际 do_sample=False、max_new_tokens=1024、seed=0。原模型配置中采样默认值被 pipeline 参数覆盖；没有改变原配置。

## 实际输出

| 论文（最后一行为历史 smoke） | 输入 Tokens | 输出 Tokens | 结束 | 原文可直接解析 | 唯一数组内候选条数 | Result 类型 | 重复条数（保留） |
|---|---:|---:|---|---|---:|---|---:|
| D18-1105.pdf | 1460 | 62 | eos | 是 | 2 | str | 0 |
| 2203.16804.pdf | 4038 | 482 | eos | 否 | 13 | float | 0 |
| 1511.08308.pdf | 4661 | 445 | eos | 否 | 12 | float | 1 |
| 2020.findings-emnlp.378.pdf | 4226 | 205 | eos | 否 | 6 | float | 0 |

候选条数只描述数组结构，不代表结果正确或已经通过正式标准化。全部原始输出仍保留，重复记录未删除。

## 提交确认的候选规则 v1

1. 原始完整响应能直接 json.loads 且字段可接受时直接使用原响应，不改写。
2. 否则必须存在唯一完整的最外层 JSON 数组；只允许移除空白、精确前缀 `Here are the extracted tuples in JSON format:` 以及成对的完整 Markdown JSON 代码围栏。
3. 数组内部逐字符保留，不改 Task/Dataset/Metric/Result，不改变数值字面形式、顺序、重复项和条数，不在这里把数字转字符串。Result 的 str() 仅由官方标准化源码完成。
4. 多个数组、截断、未知前后缀、解释性后缀、重复 JSON 键、NaN/Infinity、缺字段、额外字段、非标量 Result 均保留失败。不得选取一个看似较好的片段、补括号、补字段或调用模型修复。
5. 即使语法可解析，非 EOS/异常结束也必须单独标记，不能据此宣称生成完整。本轮三个新增样本均 EOS。

三个带前缀实例都恰好只删除数组外49个字符；候选文件中的数组内部与原响应片段完全相同。所有字段和值保持一致，包括 `89.80` 这样的原始数值文本。候选文件仅在 diagnostics/candidates/，**没有作为正式 output.json、Normalization 或评价输入**。

具体例子（仅展示一个条目，完整候选文件保留全部13条）：原响应为说明前缀后接数组，其中包含 `{"Task": "Abstractive Summarization", "Dataset": "CNNDM", "Metric": "ROUGE-1", "Result": 44.29}`。候选处理只移除数组之前的前缀；这个条目原样保留，不把 CNNDM 改成 Gold 名称，不更换44.29。

13项边界测试通过。该具体规则不是作者定义的算法，按本次用户附件第三节要求，正式使用前仍须确认。
