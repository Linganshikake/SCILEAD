# Partially execution ledger

User specification: attachment 0c71d664-1a58-4ce5-b30c-d9616b5d2c56.

1. Freeze three existing experiment directories and official source/Gold; validate counts and paper order; call unchanged sample_tdms(seed=0).
2. Create minimal ChatOpenAI transport and original-main tracing adapters. Mock original code branches, response replay and dynamic state consistency before live requests.
3. Execute original stage1 main sequentially; persist request before sending and raw response before applying updates. Replay same-position responses only; block uncertain/failed attempts.
4. Preserve stage1 output; execute original stage2 main on a fresh load; preserve both stages.
5. Run original tdm_eval for both stages; reuse audited leaderboard evaluator for all27 and masked subset; retain all denominators and definitions.
6. Validate Result invariance, requests, dynamic events, frozen files; report both stages and Fully comparisons.

Ruling: independent user-specified experiment directory is the isolation boundary; no worktree or edits inside official repo, no git commits needed.
Ruling: user specifies algorithm and approval to execute; no additional design/fee approval is needed. API failures pause dependent normalization, not converted to null.
Ruling: no new global file I/O guard; scoped paths, exact hashes, redaction and request-target validation suffice. Only designated existing API credential configuration may be read by live adapter, never printed.

Task 1 complete: original sample_tdms produced 3 masked tasks, 8 datasets, 10 boards; initial counts 20/63/26. Current frozen output order retained; author historical execution order unconfirmed.
Task 2 complete: 13 original-main branch/replay checks passed; synthetic timeout/truncation each attempted once, no state applied and retry blocked. All standalone scripts parse successfully.
Task 3 running: real sequential stage1 API calls; original prompt and wire payload verified, no output-cap parameter. Stage2 begins only after stage1 complete.
Tasks 4–6 prepared: separate evaluation, original-main response replay validation, reports and freeze checks; pending real outputs.

Engineering incident: after successful API call132 (HTTP200/stop, response digest verified), Windows refused state.json atomic replacement. Old durable state was already COMPLETE; pending temporary file differed only by elapsed seconds. Archived both and paused summary, completed same-payload filesystem write, added bounded PermissionError write retries (no HTTP retry). Regression test failed before fix and passed after two simulated locks. Resume replays first132 responses without remote calls; original algorithm/Prompt unaffected.

Tasks 3–4 complete: stage1 340 API calls, stage2 204, all HTTP200/stop at fixed snapshot; 284 rows retained. Stage1 added50 Task/56 Dataset names; stage2 changed15 tuples, preserved189 unmatched input echoes, skipped68 null records and12 exact tuples.
Task 5 complete: both original TDMR evaluations and all27/masked10 leaderboard evaluations passed. Stage1 TDMR F1 .08902523496021629; stage2 .16938419651363157. Both Result metrics equal frozen baseline.
Task 6 complete: every saved successful response replayed through unchanged original mains offline; full output/event/candidate serialization equality, no model calls. All1420 frozen files and filename sets preserved; source/Prompt/Gold/dependencies unchanged. Final report records low scores, formatting/method differences and the filesystem incident without changing predictions.
