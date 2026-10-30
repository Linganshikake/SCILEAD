# Offline Fully semantic evaluation

From the experiment root:

```powershell
& 'D:\miniconda3\envs\scilead\python.exe' -E -s -B -X utf8 .\evaluate_fully_semantic.py
& 'D:\miniconda3\envs\scilead\python.exe' -E -s -B -X utf8 .\analysis\test_evaluate_fully_semantic.py
```

The real three-arm evaluation completed successfully. The 11 regression tests
passed. The tests include a separately labelled prior-completed fixture that
exactly reproduces the previous aggregate, per-paper and per-board metrics.
Its output is under evaluation/fixtures/; production pointers are unchanged.
Optional explicit fixture CLI: append `--fixture-prior-completed`.
Optional arm restriction: `--arms baseline_rag parsed_full`.

Exit codes: 0 complete (or successful explicit fixture), 2 incomplete, 1 failed.
No generation code is imported. No API calls, model loads, downloads or subprocess
launches occur in the evaluator. Its audit hook blocks network activity, known
credential paths, generation/model imports and writes outside this root's
evaluation/ and analysis/. Dependencies see an empty Python environment mapping;
inherited values are neither read nor logged. Use the existing interpreter and
flags above; this is a local guard for this evaluator, not an OS sandbox for
arbitrary hostile Python code.

## Inputs and report contract

Required new inputs: root/selection_frozen.json, root/candidate_sets.json and,
for each of baseline_rag, parsed_full and page_images:

- `{arm}/merged/output.json`: exact byte copy of the verified old arm extraction.
- `{arm}/previous_normalized_output.json`: exact byte copy of old Fully output.
- `{arm}/merged/normalized_output.json`: enhanced Fully output.

The first two are compared with the hashes in the pinned previous evaluation.
Candidate strings and selection are also byte-pinned. Candidate membership is
exactly 23 tasks / 71 datasets / 26 metrics, from the frozen full43 setup.
Raw labels already in the candidate set must remain unchanged. Other labels may
map to a candidate or JSON null, preserving the original None fallback.
Results retain exact string values (lossless Decimal equality for a raw JSON
number), positional row counts and Result sequence, and source_documents.

`evaluation/report.json` and `evaluation/comparison.json` contain the same schema;
`evaluation/latest.json` points to the immutable run directory. Read top-level
`status`, each arm's `status`, and `protected_files_unchanged` before using scores.
`arm_results[arm]` contains:

- `old_fully` and `enhanced_fully`: `aggregate` (all six official tuple metrics,
  each P/R/F1, plus strict numeric auxiliary), `per_paper`, and `leaderboard`
  (`aggregate` plus `per_board` values/rankings).
- `comparison.delta`: enhanced minus old tuple, leaderboard and per-paper values.
- `field_binding_changes`: counts by field/paper and each changed row's old/new
  TDM, Result, and individual raw/old/new field bindings. Indices are zero-based.
- `coverage` and `input_paths` for the enhanced output.

All metrics are raw fractions. `all_three_arms_complete` is false for fixtures or
restricted arm runs. Old results come from the hash-pinned COMPLETE previous
report/latest, not from any filtered full43 comparison. The report identifies
this as original zero-shot Fully versus enhanced Fully on the same extraction.
Prompt/transport equivalence is the main orchestrator's audit responsibility;
this evaluator verifies candidates, extraction and output integrity. It does
not read request logs or infer semantic correctness from the new prompt.

## Official semantics and completeness

The helper AST-loads existing evaluator functions without running its module
top level. It calls the unchanged official tdm_eval.py and leaderboard_eval.py,
with utils replaced only by a JSON reader. Source SHA256s are checked against
the previous verified evaluation before and after use. No evaluator formulas
are rewritten. Existing scilead dependencies include rbo; no installation occurs.

Tuple denominator: exactly the five frozen papers, 28 Gold records. Official
full43/295 Gold is passed unchanged to the evaluator, which scores only the
provided five predictions. Board denominator: original 27 boards intersected
with selected IDs, dropping empty boards and retaining all singletons; exactly
10 boards / 14 memberships / 6 singleton boards. Full27 candidate boards do
not become the evaluation denominator. No second normalization stage exists.

Official Result IIM and TDMR use the original bidirectional substring rule.
TDM uses unique exact tuples. Aggregate F1 is harmonic macro P/R, with mean
per-paper F1 separately reported. Strict numeric equality is auxiliary only,
without percent stripping, scaling, tolerance or tuple conditioning.
LR exact and LR nonempty are distinct. PC/RC and numeric-value RBO preserve all
official conventions, including numeric scaling and last-row overwrites.
AO uses paper IDs, official metric direction and ID tie-breaking; it averages
prefix overlap through the shorter ranking length. Empty prediction scores 0;
all 10 retained boards, including singletons, stay in the macro denominator.

Missing files, unfinished JSON or missing selected papers do not receive new
metrics or deltas. Extra IDs, duplicate JSON keys, invalid labels, changed
Results/source documents or a wrong raw copy fail. Input hashes are checked
again after scoring; drift invalidates the run. Completeness means stable
artifact coverage, not proof that the producer job has terminated. Raw per-run
official files are subordinate to the final run report if a run is invalidated.

## Abandoned scratch from the corrected request

The earlier 20261029_input_ablation_semantic_alignment_v1 root received only
analysis/implementation_plan.md and analysis/test_evaluate_variants.py before
the correction. No evaluator or evaluation outputs were created there. Both
scratch files were left untouched; no old-root files were deleted.
