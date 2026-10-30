# Offline evaluation and comparison utilities

All tools are local-only and write strictly below this `analysis` directory. They never import a generation runtime, read credentials, initialize a model, or make API calls. Use the existing interpreter with `rbo==0.1.3`; no installation or network is needed:

```powershell
$py = 'D:\miniconda3\envs\scilead\python.exe'
$a = 'D:\C++\SCILEAD\pilot\deepseek_v41_flash\20261028\analysis'
$run = 'D:\C++\SCILEAD\pilot\deepseek_v41_flash\20261028'
```

## Evaluate any raw/normalized pair

```powershell
& $py -B -X utf8 "$a\evaluate_offline.py" `
  --raw "$run\fully\merged\output.json" `
  --normalized "$run\fully\merged\normalized_output.json" `
  --out "$a\evaluations\fully"
```

Use a **new or empty** output directory for each evaluation. A rerun against a nonempty directory fails instead of mixing old and new artifacts. Output paths outside `analysis` fail before writing. Exit codes: **0** = this input covers all 43 Gold papers and evaluation succeeded; **2** = missing files, empty input, or partial coverage; **1** = invalid input/evaluation failure. A complete evaluation is not proof of API-generation, replay, usage, or normalization-method completion.

Defaults are the frozen official 43-paper/295-annotation Gold and 27 leaderboards. `--gold` must contain the same Gold annotations. `--boards` can select an unchanged subset of the official 27 boards:

```powershell
& $py -B -X utf8 "$a\evaluate_offline.py" `
  --raw "$run\fully\merged\output.json" `
  --normalized "$run\variants\partially\stage2\leaderboard_normalized_output.json" `
  --boards 'D:\C++\SCILEAD\pilot\full43_partially\masking\partially_masked_leaderboards.json' `
  --out "$a\evaluations\partially_stage2\masked10"
```

Primary outputs:

- `status.json`, `coverage.json`, `source_hashes.json`: completion scope, actual paper/Gold/prediction counts, missing IDs, input/source integrity.
- `metrics_with_f1.json`: Task, Dataset, Metric, Result IIM and TDM/TDMR P/R/F1.
- `per_paper_metrics.json` and `.csv`: all observed papers; CSV also includes auxiliary strict Result.
- `strict_result_metrics.json`: auxiliary finite Decimal numeric equality, aggregate and per paper.
- `tdm_official/eval_results.json`, `eval_values.json`, `invocation.json`: unchanged official-main outputs and arguments.
- `leaderboard/official/*`: unchanged official leaderboard-main outputs, constructed boards and invocation.
- `leaderboard/paper_metrics/leaderboard_metrics.json`: exact-TDM LR, finite-result nonempty rate, official PC/RC/numeric-value RBO, paper-ID AO.
- `leaderboard/leaderboards/gold_vs_predicted.json`: per-board rankings, AO depth calculations, conversion/overwrite and missing-paper diagnostics.
- `leaderboard/adapter_audit.json`: byte-identical helper hashes, actual coverage, RBO version, helper-only placeholder disclosure, corrected display conventions.

## Inspect the new branches, then evaluate available files

```powershell
& $py -B -X utf8 "$a\inspect_runs.py" --out "$a\inspection_ready"
# After checking the inspection and the final CS file location:
& $py -B -X utf8 "$a\inspect_runs.py" --execute --out "$a\evaluations" `
  --cs-normalized "$run\variants\fully_cs\normalization\embedding_normalized_output.json"
```

The CS path above is an **example requiring inspection**. The inspector finds candidates below `variants/fully_cs`, excluding work/runtime/reproducibility/test directories. It selects only a unique candidate, or accepts `--cs-normalized`. Multiple candidates require an explicit selection. It writes `inspection.json` and exact standalone commands in `commands.ps1`.

The ten expected files are:

| Case | Normalized path relative to experiment root | Role |
|---|---|---|
| fully | fully/merged/normalized_output.json | Primary |
| fully_cs | Inspect variants/fully_cs final normalization output | Primary |
| partially_stage1 | variants/partially/stage1/normalized_output.json | Diagnostic |
| partially_stage2 | variants/partially/stage2/leaderboard_normalized_output.json | **Primary** |
| cold_default_stage1 / stage2 | variants/cold_default/stage1/normalized_output.json; stage2/leaderboard_normalized_output.json | Stage1 diagnostic; stage2 primary |
| cold_0_stage1 / stage2 | variants/cold_0/stage1/normalized_output.json; stage2/leaderboard_normalized_output.json | Stage1 diagnostic; stage2 primary |
| cold_42_stage1 / stage2 | variants/cold_42/stage1/normalized_output.json; stage2/leaderboard_normalized_output.json | Stage1 diagnostic; stage2 primary |

The default raw pair for all cases is `fully/merged/output.json`. Each pair must preserve row counts, order, Result strings, and source documents. Lossless numeric raw Result to normalized string conversion is allowed and counted; no cleaning/deduplication occurs. If a worker produces a separate compatible raw artifact, pass its actual path explicitly to `evaluate_offline.py`. The evaluator does not rewrite source data.

## Comparison data for the main worker's final report

```powershell
& $py -B -X utf8 "$a\compare_results.py" `
  --evaluations "$a\evaluations" --out "$a\comparison_ready"
# Override a standalone evaluation directory when needed:
& $py -B -X utf8 "$a\compare_results.py" `
  --run "fully=$a\custom_fully" --out "$a\comparison_custom"
```

This creates `comparison.json`, `comparison.csv`, `per_paper_comparison.csv`, `report.md` (a metrics worksheet), and `source_hashes.json`. CSV numeric values use 0–1 units; Markdown uses percentages. Historical per-paper CSV covers every observed paper for every source configuration and all seven metrics (six official plus strict Result); it has **no prediction-count constant**. All 20 historical configurations currently cover 43 papers, yielding 6,020 long-form per-paper metric rows.

The reader uses direct GPT-4.1 and Sol metric files, including both Partially stages. **Partially stage2 is primary**, superseding the old 24-Oct stage1-primary report wording. Stage1 stays separately labeled. Sol Fully CS exact-TDM LR is read from its own source, **24/27 = 88.89%**; GPT-4.1 Fully CS has **25/27 exact-TDM LR** and **24/27 finite-result nonempty rate**.

The default live layout is `analysis/evaluations/{fully,fully_cs,partially_stage1,partially_stage2,cold_default_stage1,cold_default_stage2,cold_0_stage1,cold_0_stage2,cold_42_stage1,cold_42_stage2}`. The comparison auto-detects each direct directory's `status.json`; it also accepts legacy `case/all27/status.json`. `--run CASE=PATH` overrides an individual directory. All ten cases must cover 43/295 and all27 for a COMPLETE comparison. **Masked10 is optional**, stored at `case/masked10` (or beside legacy `case/all27`); pass `--masked10` to the inspector/executor to add that scope.

All27 and masked10 stay separate. Three-order means and sample SD (ddof=1) appear only when all three Cold Start stage2 evaluations are complete for that scope. Individual seed/order rows are retained. The original paper's verified local transcription provides Tables 3/4/12 (tuple metrics), 5/17 (leaderboards), reported F1 and SD, and explicit paper/board populations. AxCell's 36 papers and appendix masked/threshold-2 scopes never become all43/all27 comparisons. Published AO is not relabeled as numeric-value RBO. No internet/PDF retrieval is performed.

Original evaluator repository HEAD: `8bf74b0a830feb7035c6166dce3394dc344ae532` (also verified locally with read-only Git). Frozen outer/archive commit: `b2a76b52acc736b9cbdcb6bae1c195ac12d3cf25`. They are distinct fields in comparison provenance. Generation context is user-confirmed: request/response alias `deepseek-flash`, documented DeepSeek-V4.1-Flash-1017, thinking enabled, reasoning effort high, no output cap. These utilities do not certify provider execution or usage; the main worker owns that reporting.

## Coverage and formula conventions

The official tuple main averages only the normalized paper IDs it receives. We report that actual denominator and evaluated Gold count. We never pad missing papers into tuple scoring or claim 43-paper completion for a subset. Empty/missing input yields no scores. Malformed JSON, duplicate JSON keys, unknown IDs, changed Results/source documents, invalid types, and row-count changes fail explicitly.

Leaderboard metrics retain all supplied Gold boards and Gold memberships, so absent predictions contribute no entries. The unchanged supplementary helper indexes every Gold paper; a **helper-only view** supplies empty lists for unprocessed papers. It adds no predictions, is verified to construct exactly the same official boards, and lists placeholder IDs in the audit. Its missing/null diagnostics must be read with coverage.json: a missing unprocessed paper is not a normalization failure.

Both official mains are imported directly from the original repository with their formulas unchanged. A tiny in-memory `utils.read_json` binding avoids the original utils module's unused model imports. Audited leaderboard helper scripts are copied byte-for-byte; only their isolated common.py supplies local paths, IO, and integrity checks. No historical runtime is imported.

Official Result IIM/TDMR substring matching is preserved, including possible recall above 1 from duplicates; scores are not clipped. TDM's misspelled official per-paper precision key is mapped correctly. Macro F1 = harmonic mean of macro P/R; mean paper F1 is separately labeled. Strict Result is finite Decimal equality over unique values, with invalid strings retained only in denominators; it does not strip percent signs, scale, round, apply tolerance, or condition on TDM. Nonfinite leaderboard conversions fail supplementary evaluation, leaving FAILED status instead of a successful partial ranking.

## Verification

```powershell
& $py -B -X utf8 "$a\test_offline.py"
```

Tests write only under `analysis/offline_test/regression_*`; `offline_test/verification_latest.json` records the result and artifact directory. They cover exact historical tuple/leaderboard parity, Sol Fully CS LR, masked10, partial/empty/missing coverage, malformed/duplicate JSON, Result conversion, nonfinite board failure, offline/credential/write/process boundaries, stage2-primary comparison, scope-mismatch rejection, and all-paper CSV export. Test runs preserve their artifacts for inspection. Source/input hashes are checked before and after evaluations; copied helpers are verified byte-for-byte. Protected old files, including original 24-Oct outputs, are read-only.

Before using the final worksheet, inspect each case's status/coverage, input SHA-256, the stage2 primary source path, all27 versus masked10 denominator, CS selected output, and per-board unparseable/overwritten tuples. Confirm the main worker's generation/normalization summaries separately. Missing/partial cases keep the comparison INCOMPLETE; no report of DeepSeek model performance is inferred from historical test fixtures.
