# Offline DeepSeek evaluation utilities

Goal: implement the evaluation task in ../execution_plan.md, with every write below this analysis directory and no network, credentials, model runtime, or changes to frozen sources.

Architecture: standalone Python CLI calls unchanged official mains through a minimal JSON-only utils binding; byte-identical audited leaderboard helpers receive an isolated common.py. Tuple metrics use observed papers only; leaderboard metrics keep the supplied Gold board denominator. Partial input is explicitly incomplete.

Spec: ../execution_plan.md and the user's evaluator handoff. Execution: inline under the already authorized analysis-only scope; no worktree or commits outside that scope.

- [x] Implement evaluator and focused regression tests: historical equality, variable prediction counts, partial/empty coverage, numeric Result compatibility, malformed input, and filesystem/network boundary.
- [x] Implement branch inspection and source-backed comparison: all six tuple metrics, strict Result, all27 versus masked10, original-paper values separate from local code metrics; Sol Fully CS LR reads 24/27. Latest user instruction: Partially stage2 is primary; both stages remain available. Original repo HEAD and outer/archive commit are distinct.
- [x] Offline-test historical GPT-4.1/Sol data, hash checked sources before/after, and deliver commands and inspection guidance in README.md. All generated test outputs go under offline_test. Current full-suite result and artifact directory are in offline_test/verification_latest.json.

Review focus: missing normalized papers are not silently counted as 43; nonfinite converted values stop supplementary rankings; raw Result strings stay exact and numeric conversion is lossless; duplicate JSON keys and unknown paper IDs fail; missing stages/scopes cannot produce a complete report. Official Result substring semantics and TDM precision's misspelled per-paper key stay unchanged.

Review ledger: independent read-only reviewer found unguarded process-launch events in the offline audit boundary. A synthetic audit-event test reproduced the gap without launching any process; the boundary now rejects subprocess.Popen, os.system, os.exec, os.posix_spawn, and _winapi.CreateProcess. No other concrete evaluator correctness issue was reported. Local review added an explicit nonfinite-conversion failure message and a scope-mismatch reader test. Main worker retains final narrative/usage reporting.
