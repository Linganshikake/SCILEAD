# Execution notes

- Free preflight confirmed 43 original Few-shot extractions, 293 records, 295 Gold rows, 426 exact field matches and 453 required model requests. Candidate serialization and normalization Human messages match B; the System message changes to the author's complete Few-shot normalization template.
- All 453 live normalization attempts succeeded on the first attempt. No extraction request, automatic retry, extra model, parsing or retrieval was executed.
- During offline three-setting report generation, A's strict numeric metric was found in `evaluation/strict_result_metrics.json`, whereas B stores it inside `metrics_with_f1.json`. The new adapter was corrected to read the existing A artifact. Official tuple evaluation had already succeeded; no predictions or historical files were changed.
- The copied leaderboard common adapter initially referenced `manifest.json`; this new run uses `input_manifest.json`. The new adapter and its generator were corrected to that filename. The original leaderboard algorithm and both audited wrapper scripts remain unchanged. This was a local file lookup failure before evaluation, not an API failure.
- Both offline path corrections were verified by rerunning only the affected free evaluation stage. Their existence does not add API attempts or alter scores.
- The experiment uses the user-requested independent directory rather than a Git worktree because all official source and historical experiment files must remain unchanged.
