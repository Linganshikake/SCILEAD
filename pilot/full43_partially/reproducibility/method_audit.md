# Method and adaptation audit

The user specification is implemented by calling the unchanged official mains at commit `8bf74b0a830feb7035c6166dce3394dc344ae532`.

## Stage 1

- `sample_tdms()` is called directly with integer seed 0 and cold_start False. Its real return value and local sampling outputs were recorded; no alternative masking algorithm is substituted.
- Full Gold is read only where original code builds candidate names. Actual model inputs are the original SystemMessage plus HumanMessage containing one name and the serialized current candidate set.
- Official main iterates frozen JSON keys, each prediction list and each record's keys. No sorting or concurrency is introduced.
- An observer receives original-main line events. It records actual locals after the official field branch, asserts the specified branch and stores exact pre/post candidate order. It never sets frame locals or changes choices.
- Exact names skip calls. Non-exact Task/Dataset use the masked prompt. Metric uses the fully normalization prompt and never expands. Only an answer equal to the original Task/Dataset name is newly inserted. Quoted names, commentary and arbitrary new strings are not cleaned.

## Stage 2

- A fresh original main invocation loads the completed stage1 JSON, preserving the saved stage1 artifact.
- Gold candidate tuples consist solely of the 27 standard TDM names, serialized exactly as original code joins its set. Gold paper IDs, Results and ranks are not transmitted.
- Null fields skip the request; exact tuple membership skips the request; non-exact accepted answers undergo the original string slicing/splitting. Unmatched answers retain the prior record.

## Transport and checkpoint boundary

- The pre-existing ChatOpenAI/OpenAI SDK transport pattern is retained: fixed GPT-4.1 snapshot, temperature 0, seed 0, stream false, max_retries 0, explicit endpoint and timeouts.
- No output-cap field is sent. This is an explicit experimental configuration difference from official defaults 15/100, not claimed to be bit-identical author generation settings.
- `attempt.json` is written before a request can leave the request hook. The raw response is persisted before a COMPLETE state and before official main applies its answer. Interrupted or failed attempted calls cannot automatically re-enter transport.
- Resume begins at the original input and replays COMPLETE responses at identical stage/call/paper/record/field positions. Candidate string and full message equality are checked first. It is not a semantic cache.
- Prompt hashes serialize message objects in role/content order; SDK wire JSON may serialize keys content/role. Message list order and text are identical. Verification normalizes only JSON object key order for this hash, retaining the exact wire JSON file separately.
- Windows PermissionError retries apply only to the same file payload, at most 20 attempts with capped short delays. They cannot trigger an API retry or choose another response. The observed call132 incident is archived separately.

## Evaluation boundaries

- Stage1 and stage2 each call unchanged `tdm_eval.main` on all 43 papers. F1 is extra arithmetic on official macro P/R; Result's official substring rule is not replaced.
- The strict numeric diagnostic uses the prior frozen finite-Decimal equality definition and denominators. Equality to frozen results is checked per paper and in aggregate.
- Leaderboard evaluation uses stage2 and the audited prior entry points. Separate runs change only the Gold path to all27 versus the actual 10 masked boards. All 43 predicted papers remain present.
- Existing official conversion, overwrite, sort, RC and numerical RBO formulas remain unchanged. Supplemental paper-ID AO and both LR definitions are reused. RC is not clamped.
- The paper and README establish a second alignment stage for leaderboard evaluation, but do not identify a concrete stage1/stage2 JSON for every TDMR/IIM table. Both sets of scores are retained with explicit stage labels.
