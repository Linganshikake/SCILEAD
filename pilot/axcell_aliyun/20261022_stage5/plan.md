# P5 execution ledger

User approved P4: local completed37 scope (including9 VALID_EMPTY),65 raw records,123 uncapped GPT-4.1 Fully field calls; provider billing unverified accepted. No model changes, extraction reruns, prompt edits or automatic retries.

1. Freeze P4 and P3 input hashes; prepare independent per-paper working copies.
2. Verify HTTP ledger with offline mock responses: exact frozen payload, once-only attempt marker, replay valid checkpoint, reject HTTP errors/non-stop/wrong model, no retry.
3. Execute123 frozen requests serially, preserve raw responses and null mappings, run unmodified official normalization main via initializer-only adapter.
4. Verify all37 outputs and source/Result invariants before official evaluation. If incomplete, disclose and do not label partial results complete37.
5. Original TDM evaluation plus original leaderboard evaluation on27 boards restricted to37paper IDs (no rethreshold); independent LR/AO and strict one-to-one diagnostics. Frozen GPT-4.1 comparison on same37. No paid calls for comparison.
6. Reports, integrity check and E-drive mirror. Stop after P5; no Partially/Cold Start or other experiment.

Ruling: use new experiment directory instead of modifying frozen repositories/worktrees; only orchestration and reports are new. No git commit or cleanup of experiment artifacts.
Ruling: keep original repeated-field behavior. Cache only exact approved request occurrence at durable completed checkpoint; no cross-record name cache.
