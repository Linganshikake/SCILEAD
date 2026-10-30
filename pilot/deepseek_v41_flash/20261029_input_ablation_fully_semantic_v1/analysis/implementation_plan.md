# Fully semantic offline evaluator plan

Goal: implement the user's corrected Fully-only evaluation scope.
Architecture: reuse hash-pinned functions from the previous evaluator by AST and
call unchanged official evaluator modules through their JSON-only utils binding.
Python standard library plus the already-installed rbo dependency; no runtime,
model, API, environment-value or credential access.

- [x] Test scope/integrity, frozen candidates, official parity and offline guard.
- [x] Implement evaluate_fully_semantic.py for the three arms' merged files.
- [x] Run prior-completed fixture parity and evaluate the completed real inputs.
- [x] Document commands, report schema, assumptions and test evidence.

Writes: this analysis/ and evaluation/ only. No worktrees, commits, runtime edits,
deletes, stage2, variants, cold summaries or old full43-filtered comparisons.
Missing/unfinished artifacts are incomplete, and receive no new metrics.
Well-formed invalid artifacts fail. Compare verified old Fully with enhanced Fully
only on exactly five selected papers, byte-identical raw extractions, 28 Gold
tuples, 10 original restricted boards, 14 memberships and six singletons.
Keep official legacy Result matching and numeric RBO; strictNumeric and paper-ID
AO remain auxiliary. F1 is harmonic macro P/R; mean per-paper F1 stays separate.
Fixed candidates are exactly the frozen 23/71/26 sets, with original null fallback.
Completeness means stable input artifacts, not a claim about producer job status.

Review focus: no partial-set scoring; fail on raw-copy/candidate/label/Result drift;
recheck input hashes; fixture pointers never replace production report/latest;
old/new full metrics and per-paper deltas retain official formulas.

Execution: real inputs became complete before the evaluator was ready, so used
them directly as requested. All three real arms evaluated COMPLETE, exit 0.
11 regression tests passed, including separate prior-input fixture parity;
fixture execution preserved production and previous report/latest bytes.
Partial inputs are covered by tests rather than modifying live producer files.
