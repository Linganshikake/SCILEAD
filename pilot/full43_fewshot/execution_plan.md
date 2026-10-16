# SCILEAD Few-shot Implementation Plan

**Goal:** Run 43 author-demo extractions and Fully Pre-defined LLM normalization, preserving frozen evidence and evaluation.

**Architecture:** Independent adapter and durable per-paper request ledgers. Original TDMPrompt/NormalizationPrompt, RetrievalQA stuff, original normalization main (model factory and configuration only adapted), original evaluation main functions. No parsing/indexing or changes to official files.

**Tech stack:** Existing scilead Python 3.11 environment, LangChain 0.1.17 / langchain-openai 0.1.2, GPT-4.1-2025-04-14.

**Spec:** User's Few-shot experiment request in this conversation.

## Constraints and review focus

- All new requests omit client output limits, tools and response_format; temperature=0, seed=0, stream=False, no retries.
- Example is embedded once in official System template; user message and evidence match frozen requests exactly.
- Extraction cannot read Gold. Normalization uses full 23/71/26 label sets in the same order as frozen Fully baseline.
- Official is_few_shot also changes normalization prompt: use a separate normalization input configuration with is_few_shot=False, keeping extraction configuration honest and immutable.
- Invalid JSON, non-stop responses and ambiguous failures block that paper; successful positions replay locally without extra requests.
- Preserve author example anomalies, every raw prediction and all nulls; no score-based regeneration.

## Execution

- [x] Prepare `common.py`, `prepare.py`: hash all frozen roots, official sources, Gold, dependencies; save author example and per-paper evidence-only inputs and request plans. Confirm 43 bundles / 284 historical predictions.
- [x] Prepare `transport.py`, `run.py`, `test_offline.py`: test identical rendered user messages, official normalization behavior, durable same-position replay and no retry after uncertain failure.
- [x] Run 43 extractions, then eligible normalizations. Save requests/responses/usage and per-paper checkpoints.
- [x] Run original `tdm_eval.py` and `leaderboard_eval.py`, reusing audited supplementary LR/AO definitions on 27 boards. Save per-paper metrics, strict numeric diagnostics and Zero-shot comparisons.
- [x] Verify wire parameters, response status, evidence hashes, official normalization replay, source/dependency/frozen-root hashes; write final report and resume instructions. Stop.
