# DeepSeek-V4.1-Flash SCILEAD reproduction

**Goal:** Repeat Fully LLM, Fully CS, Partially and three Cold Start orders on the frozen 43-paper/295-Gold scope, then compare official tuple and leaderboard metrics.

**Architecture:** Reuse frozen evidence and original official mains. Independent transport changes only the model/provider and supported generation configuration. All new outputs live below this directory; old experiment data and source remain read-only.

**Execution:** Main worker prepares and runs Fully. Parallel independent workers prepare the variant adapters and evaluators; no sub-agent performs paid requests. Review and offline validation precede model execution. Existing user authorization covers this run.

## Frozen requirements
- Official request model `deepseek-flash`, documented serving model DeepSeek-V4.1-Flash-1017 (2026-10-28).
- Official endpoint https://api.deepseek.com/chat/completions. Only designated deepseek.env read in transport; no credentials in artifacts.
- Thinking enabled, reasoning_effort=high (official default), stream=false; omit output caps, temperature, seed, tools and response_format. DeepSeek documents medium as mapping to high. No model fallback.
- 43 frozen RAG inputs, original system/user prompt, exact document order, full canonical sets (23/71/26); no new parsing/retrieval.
- Reuse approved lossless numeric Result-to-string conversion in separate compatible output; raw response immutable. No semantic repair or deduplication.
- Serial per branch; no repeated-name cache. Durable request checkpoint blocks uncertain/failed resend. Preserve malformed outputs and incomplete coverage.
- Partially and Cold Start run official stage1 and stage2 with prior ordering/masking. Cold seeds: null, string "0", string "42".
- CS uses existing original embedding weights/settings; require adequate measured RAM before loading.
- Official macro P/R, F1=2PR/(P+R), 27 Gold leaderboards. Auxiliary strict values and paper-ID AO separately labeled.

## Tasks
- [x] Freeze source/input hashes and document provider compatibility.
- [x] Implement isolated transport and Fully runner; offline no-retry/format tests.
- [x] Run one formal queued paper, validate actual request/response, continue remaining queue.
- [x] Prepare/review/test independent CS/Partially/Cold adapters and run on new Extraction.
- [x] Run unchanged official evaluations; compare original paper/GPT-4.1/Sol.
- [x] Verify protected files, coverage, usage, output indices and report.

## Review focus
Unknown API result must never resend automatically; failed JSON must remain raw; canonical candidate order must match historical protocol; numeric Results must retain meaning; partial runs must not be reported as complete.
