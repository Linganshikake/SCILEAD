# Author full Few-shot branch

All writes stay in this directory. Frozen experiments, official source, prompts and Gold remain read-only. Python: `D:\miniconda3\envs\scilead\python.exe`; PowerShell process setting `$env:PYTHONHASHSEED='0'`; flags `-B -X utf8`.

1. `prepare.py` runs once. It resolves each original extraction from the prior manifest, verifies the original rendered prompt, freezes raw predictions/evidence, hashes historical directories, and builds the exact Few-shot normalization request plans.
2. `test_offline.py` runs the original normalization main with mock answers and no network. It checks the true Few-shot dispatch, examples/braces, in/out-of-set handling, unchanged Result/evidence, repeated fields and uncertain-request guards.
3. `normalize.py` executes only normalization, sequentially. Existing completed/failed stage summaries are skipped. Identical completed positions can be replayed locally after a worker interruption; unresolved attempts cannot be resent automatically. It never imports a callable extraction workflow or performs PDF/embedding/retrieval work.
4. `evaluate.py` merges completed papers and runs original tuple evaluation. It preserves failed coverage, compares A/B/C, and asserts unchanged Result scores for complete coverage. Strict numeric calculations are copied from the prior audited implementation.
5. For complete 43-paper coverage run `leaderboard_evaluation/run_official_leaderboard_eval.py`, then `leaderboard_evaluation/evaluate_paper_metrics.py`. These files are byte-identical to the previous audited wrappers; only common.py points to this run's predictions. No LLM calls.
6. `finalize.py` replays the original normalizer offline using recorded responses, checks actual HTTP payloads/usage and frozen hashes, and writes reports and final artifact hashes.

`status.py` reads progress only. Live HTTP bodies and sanitized states are at `normalization/api_calls/<paper-stem>/<call-index>/`. Original per-paper input/config and normalized results are under `papers/<paper-stem>/normalization_input/`. The aggregate official-compatible result is `normalization/normalized_output.json`.

Only the model factory is adapted: official `tdm_llm_normalization.main` receives `is_few_shot=True`, GPT legacy dispatch type, and no output limit. Actual transport uses GPT-4.1 snapshot, temperature0, seed0, streamFalse and SDK retries0; no output-limit fields, tools or response_format. Actual author Few-shot System and Human messages are asserted before every request. No cross-record cache, cleaning, extra context, manual mappings or Gold tuple answers are used.

Author examples remain static. Current field candidates are the exact full-Gold sets, serialized with hash seed0; their order equals prior B. Original raw extraction is reused, never prior null/mapped fields. Records associate by paper ID and original one-based index.

Settings: A=Zero Extraction+Zero Normalization; B=Few Extraction+Zero Normalization; C=this Few Extraction+Few Normalization. C is the author full Few-shot prompt branch. GPT-4.1, omitted default output cap and frozen data-version differences remain disclosed. Leaderboard evaluation is supplementary to the paper's Table7 tuple-level comparison.

Do not rerun preparation or remove attempt files. Any further attempt after an unresolved failure needs review. Historical attempts and results are not overwritten. Stop after this experiment; no threshold=2 or other experiments.
