# Sol offline semantic-alignment evaluation adaptation

**Goal:** Prepare offline, same-branch Sol baseline/rerun evaluation and comparison.
**Spec:** User handoff in this task; no new Prompt design or runtime work.
**Architecture:** Reuse DeepSeek's audited evaluator and both leaderboard helpers byte-for-byte. Adapt readiness, paths, 335-prediction scope and historical Sol result loading. Baseline re-evaluations live under this analysis directory and must match historical numerical results exactly.
**Tech stack:** Existing scilead Python environment; standard library and already-installed rbo.

## Constraints and decisions

- All writes, logs, temporary files and outputs stay strictly below this analysis directory. No worktree, commits, installation, child processes, runtime imports, credentials, network or models.
- Flat branch layout: partially, cold_default, cold_0, cold_42; stage1 diagnostic, stage2 primary. 43 papers / 335 predictions / 295 Gold / 27 boards.
- COMPLETE summary, hash, counts, config, identical raw input bytes, paper order and preserved Result/source_documents are required before evaluation.
- Completed evaluations are sealed; changed sources, artifacts or inventory fail reuse. Incomplete stages stay missing, never zero-filled.
- Reuse the approved method without brainstorming or requesting approval. Main agent owns runtime, Prompt and usage audit outside analysis.

## Work and verification

- [x] Adapt existing behavior tests first; observe missing implementation failures.
- [x] Copy scoring/helpers unchanged; adapt readiness, environment and immutable audit checks.
- [x] Re-evaluate all eight baseline stages locally; compare all historical tuple outputs exactly and all four historical all27 leaderboard outputs exactly. Stage1 leaderboard diagnostics have no historical counterpart.
- [x] Adapt paired comparison, all tuple P/R/F1, LR/PC/RC/RBO/AO, three-Cold mean/sample SD and paired-delta SD, per-paper deltas.
- [x] Run offline tests and baseline parity; confirm guards and read-only reuse. Generate a pending comparison if rerun is not ready; do not wait.
- [x] Deliver commands, exact validation results and changed-file inventory.

Review focus: COMPLETE-but-missing/corrupt output; config/raw/order mismatch; modified completed evaluation; unequal or missing three-Cold runs; partial primary results clearly distinguished from stage1 diagnostics.

Execution record: 22 tests passed; all eight baseline stages freshly evaluated with exact numerical identity. No baseline writes. Initial verification timestamp is recorded in verification/initial/verification.json. Config inspection after runtime launch showed local Gold snapshots; readiness now accepts only their byte-identical copies and freezes their hashes. Reports use actual UTC times instead of inferring dates from the experiment folder. Initial comparison has eight baseline rows and zero completed variant pairs. Main agent owns the observed PAUSED_FAILED_OR_UNCERTAIN runtime status.
