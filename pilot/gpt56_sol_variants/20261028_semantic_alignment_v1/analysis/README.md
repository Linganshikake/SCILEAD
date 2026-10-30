# GPT-5.6 Sol semantic-alignment offline evaluation

All tooling and generated files stay under this `analysis` directory. The baseline `../../20261024` is read-only. No runtime modules, credentials, model calls, network access, subprocesses or installation are used by the Python evaluation tools. The main agent owns runtime/Prompt/usage work outside analysis.

## Run

Use the existing interpreter; no installation is needed:

```powershell
$analysis = 'D:\C++\SCILEAD\pilot\gpt56_sol_variants\20261028_semantic_alignment_v1\analysis'
$python = 'D:\miniconda3\envs\scilead\python.exe'

# One pass: inspect summaries and any previously sealed evaluations.
& $python -B -X utf8 "$analysis\evaluate_ready.py" --inspect

# One pass: evaluate every completed stage; leave unfinished stages pending.
& $python -B -X utf8 "$analysis\evaluate_ready.py"

# Build a new timestamped paired comparison under analysis\comparisons.
& $python -B -X utf8 "$analysis\compare_results.py"

# Recheck tests, baseline parity and immutable reuse.
& $python -B -X utf8 "$analysis\verify_offline.py"
```

Python exit codes: **0 complete, 2 pending/incomplete, 1 error**. A pending result is expected while runtime is unfinished; inspect `$LASTEXITCODE` immediately after a command. `verify_offline.py` returns 0 only when its suite and all baseline checks pass.

Select a stage with repeatable `--case partially_stage2`, `--case cold_default_stage2`, `--case cold_0_stage2`, or `--case cold_42_stage2`; the corresponding `_stage1` cases are supported. `evaluate_offline.py` is an alias for the same completed-stage CLI. `evaluate_ready.py --source baseline` re-evaluates the frozen baseline into `analysis\baseline_evaluations`, or verifies and reuses existing sealed results.

Default behavior never waits. Optional bounded polling is `--wait-seconds 60 --poll-seconds 10`. Run one evaluation process at a time. `--inspect` writes only `readiness.json` (or `baseline_readiness.json`); it does not run scoring. Comparison does not run evaluation itself. `compare_results.py --out <new-directory-below-analysis>` chooses a destination; nonempty destinations are rejected.

## Accepted inputs and completion

- Flat experiment branches: `partially`, `cold_default`, `cold_0`, `cold_42`.
- Stage1: `<branch>/stage1/normalized_output.json`; stage2: `<branch>/stage2/leaderboard_normalized_output.json`.
- Each stage needs `summary.json` declaring `COMPLETE`, 43 papers, 335 records, the matching absolute output path and its SHA-256.
- Each branch's `config.json` must identify `inputs/output.json` with the frozen baseline byte hash. Its paper order must match the same baseline branch and normalized output order.
- Gold paths may identify the official files or this experiment's `inputs/gold.json` and `inputs/leaderboards.json`. Local snapshots must be byte-identical to the official Gold files.
- Full scope is fixed at **43 papers / 335 predictions / 295 Gold annotations / all 27 boards**. Result strings, row counts and source documents must remain unchanged from extraction.
- Missing or non-COMPLETE summaries remain pending, including `PAUSED_FAILED_OR_UNCERTAIN`. Malformed in-progress summary JSON remains pending. Duplicate keys, a COMPLETE summary with missing/changed output, wrong scope, changed extraction, or incompatible config are errors.

An evaluation is sealed only after successful official scoring, full validation and stable input hashes. Reuse verifies the entire artifact inventory, input/source hashes and metric consistency. No completed evaluation is overwritten. A changed input, added/removed/modified artifact, or missing seal fails closed. If evaluation was interrupted, inspect and archive that case's unsealed directory **within analysis** before retrying; do not edit seals or re-pin hashes to hide a mismatch. Source code/audit changes intentionally invalidate existing seals.

## Metrics and outputs

`comparisons/<actual-UTC-timestamp>/` contains:

- `report.md`: stage2 primary comparison, stage1 diagnostic comparison, all metric tables and three-Cold mean/sample SD.
- `comparison.json` and `comparison.csv`: all six tuple metrics (Task/Dataset/Metric/Result IIM, TDM and TDMR exact match), each with P/R/F1; LR, finite-nonempty, PC, RC, RBO and AO. CSV contains baseline, variant and variant-minus-baseline delta for each case/metric.
- `cold_statistics.csv`: all 24 scalar metrics for each stage and baseline/variant/paired-delta group. Mean and sample SD require exactly all three Cold orders. The paired-delta SD is computed from three paired differences; it is not a difference of SDs. These three orders are not independent model replicates.
- `per_paper_differences.json` and `.csv`: 43 papers × six tuple metrics × eight cases, with all P/R/F1 before/after/deltas where available. Unavailable variant and delta values are null/blank.
- `source_hashes.json` and `report_status.json`: report provenance and generated-file hashes.

JSON/CSV retain unrounded fractions. Markdown displays percent and percentage-point deltas. Official tuple F1 is the harmonic mean of macro P/R, not mean paper F1. Official Result IIM/tuple matching, numeric conversion, duplicate handling and RBO behavior are preserved. LR means exact TDM hit before numeric conversion; finite-nonempty is separate. RBO uses official deduplicated numeric-value rankings. AO ranks paper IDs with deterministic ties and counts empty boards as zero in the all27 denominator. Strict numeric Result equality remains auxiliary in each evaluation directory.

`status` covers all eight paired stages; `primary_status` covers the four stage2 pairs; `diagnostic_status` covers the four stage1 pairs. Selection or partial completion never implies the whole rerun finished. DeepSeek's 295-prediction results are excluded from Sol's 335-prediction paired comparisons.

The experiment directory name is an identifier, not an execution date. Readiness and comparison reports use the actual UTC clock, including after midnight. Runtime launch/completion timestamps and Prompt evidence remain the main agent's responsibility.

## Validation delivered

`verification/initial/verification.json` records **22 passing tests**, eight fresh baseline re-evaluations, and exact equality with all historical tuple/per-paper results and all four historical stage2 all27 leaderboard results. Equality uses no rounding or tolerance. Stage1 leaderboard metrics are additional offline diagnostics; the historical Sol evaluator stored leaderboard results only for stage2.

The verification checks 139 pinned source/input files and 383 source/artifact files during parity and reuse, with zero changes. It verifies repeated reuse performs no evaluation-artifact writes. Tests exercise output boundaries, synthetic blocked network/process/model/credential events, summary/hash/scope checks, local Gold byte copies, extraction/Result/order preservation, changed seals and inventories, missing comparisons, delta direction, macro F1 and three-Cold sample SD.

`verification/comparison_selfcheck.json` also confirms 192 scalar comparison rows, 2,064 per-paper metric rows, 144 Cold-statistic rows, preserved blank missing values and zero deltas when self-pairing baseline rows strictly as a diagnostic. No synthetic result is included in the actual experiment comparison.

Scoring is reused byte-for-byte in `audited_helpers/evaluate_offline.py`; both leaderboard helper files are also byte-identical to audited DeepSeek copies. Official repository `tdm_eval.py` and `leaderboard_eval.py` are loaded unchanged with a minimal `utils.read_json` adapter, avoiding runtime/model imports. `offline_support.py` differs from the audited DeepSeek copy only in its ANALYSIS path assignment. The public facade gates the legacy scorer on completed stages; do not invoke files under `audited_helpers` directly.

The initial comparison is `comparisons/initial/report.md`. It records a real pending snapshot, not a result for the unfinished rerun. Run evaluation and comparison again when stages finish.

## Files added

All files were added below analysis; no baseline or runtime files were edited.

- Entry points: `evaluate_ready.py`, `evaluate_offline.py`, `compare_results.py`, `verify_offline.py`.
- Validation and IO: `evaluation_contract.py`, `offline_support.py`, `audit_manifest.json`.
- Audited copies: `audited_helpers/evaluate_offline.py`, `audited_helpers/run_official_leaderboard_eval.py`, `audited_helpers/evaluate_paper_metrics.py`.
- Tests: `test_utilities.py`, `test_sol_contract.py`.
- Instructions/record: `README.md`, `implementation_plan.md`, `delivery_manifest.json`.
- Generated evidence: `baseline_evaluations/` (eight sealed cases), `baseline_readiness.json`, `readiness.json`, `verification/`, `comparisons/initial/`.

`delivery_manifest.json` lists every delivered relative path and SHA-256 except itself; it is a handoff snapshot, not a live-run constraint on future readiness/comparison artifacts.
