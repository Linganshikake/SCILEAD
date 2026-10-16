# Author Few-shot Normalization Implementation Plan

> Execute inline using executing-plans and verification-before-completion. User explicitly authorized execution after free checks; no additional plan approval is required.

**Goal:** Reuse all 43 Few-shot extractions (293 records) and run the author's complete Few-shot normalization branch, followed by unchanged tuple and leaderboard evaluation.

**Architecture:** Independent experiment directory. Original normalization main is called per paper with is_few_shot=True; only its model factory is adapted to the existing logged ChatOpenAI transport. Frozen request plans check every actual message. No extraction code is executed.

**Tech stack:** Existing scilead Python 3.11.17, LangChain/OpenAI client and official code at 8bf74b0a830feb7035c6166dce3394dc344ae532.

**Spec:** User attachment eeb1ca5a-27b5-497c-9b1a-11ac909d8e0b, read in this conversation.

## Constraints and decisions

- Write only full43_fewshot_both_prompts; do not create a worktree or alter the official repository. The user explicitly requires an isolated experiment directory and unchanged sources.
- GPT-4.1 snapshot, temperature=0, seed=0, stream=False; omit output limits, tools and response_format; SDK retries=0.
- PYTHONHASHSEED=0; 23/71/26 fixed candidates; no semantic cache, context, cleaning or fallback.
- Single sequential worker given approximately 1.5 GiB available memory. Parallel evaluation is unnecessary.
- Existing extraction and source_documents are immutable; source record order keys are paper ID and one-based original record index.
- Errors stop that paper and remain distinct from model-generated null. Continue other papers without retrying unresolved calls.

## Review focus

- Few-shot dispatch flag must actually produce the author's system text, with escaped braces rendered once.
- Static demonstration candidate lists must stay distinct from actual dynamic field candidates.
- Same raw field repeated in different records must issue separate requests; checkpoint replay applies only to identical completed positions.
- Out-of-set/quoted/whitespace answers map to null without cleanup; Result remains untouched.
- Complete coverage and historical-request accounting must not be inferred from a subset.

## Tasks

- [x] Freeze and validate: prepare.py verifies historical hashes and 43 extraction request payloads, records candidate order and computes exact/pass-through and LLM request counts. Save input_manifest.json, input/output.json, config.json and prompt provenance.
- [x] Free validation: test_offline.py invokes original normalization main with mocks; verify in-set/out-of-set/whitespace responses, no duplicate-value cache, unchanged Result and evidence, completed-position replay and ambiguous-failure guard. Save offline_validation.json.
- [x] Execute: normalize.py uses the unmodified official main and durable transport. Save each response before updating checkpoints, continue other papers after failure, never issue extraction requests.
- [x] Evaluate: original tdm_eval and audited leaderboard wrappers; preserve 43-paper macro behavior and verify Result scores remain identical to B. Save A/B/C comparisons and per-record mapping differences.
- [x] Verify and report: offline replay all normalized predictions from saved responses, independently total actual usage, verify all frozen files and request parameters, save report, README and artifact hashes; stop.

## Progress ledger

Plan/spec checked: original normalization main selects few-shot-normalization-system-prompt only when is_few_shot=True. Three author examples are embedded in one System message. Source demonstrations and dynamic lists will not be rewritten.

Progress: free checks passed; 426 exact fields and 453 independent model fields. Paid normalization running; no extraction requests. Scoring block matches prior audited source.
