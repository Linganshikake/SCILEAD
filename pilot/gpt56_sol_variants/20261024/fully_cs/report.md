# GPT-5.6 Sol Fully+CS offline run

Status: COMPLETE; verification PASS. 43 papers, 335 predictions, 295 Gold tuples; fixed 27 Gold leaderboards / 140 entries.

## Tuple metrics

| Metric | Precision | Recall | F1 |
|---|---:|---:|---:|
| Task IIM | 0.962209302 | 0.988372093 | 0.975115239 |
| Dataset IIM | 0.912796916 | 0.909017846 | 0.910903461 |
| Metric IIM | 0.883411421 | 0.884061546 | 0.883736364 |
| Result IIM | 0.777471471 | 0.836690441 | 0.805994669 |
| TDM Exact Match | 0.813763046 | 0.798404632 | 0.806010682 |
| TDMR Exact Match | 0.628759398 | 0.674180019 | 0.650678025 |

Official per-paper macro P/R; reported F1 is the harmonic mean of aggregate P/R. Official Result IIM and TDMR use substring Result matching, not strict numeric equality. No result rewriting or deduplication was introduced.

## Fixed 27-board evaluation

| Metric | Value |
|---|---:|
| gold_leaderboards | 27 |
| nonempty_valid_result_boards | 24 |
| tdm_hit_boards | 24 |
| LR_exact_tdm_hit | 0.888888889 |
| LR_nonempty_finite_result | 0.888888889 |
| PC_official | 0.784215168 |
| RC_official | 0.623677249 |
| RBO_official_value_rankings | 0.553057035 |
| AO_paper_id_macro_all_gold_boards | 0.713887091 |
| AO_nonempty_only_DIAGNOSTIC | 0.803122978 |
| supplementary_joint_paper_result_coverage | 0.611640212 |

PC, RC and RBO are from unchanged official leaderboard_eval.main. RBO ranks deduplicated numeric values with the installed rbo default p=1. Official numeric conversion, less-than-one scaling, metric directions and last-valid-record overwrite order are preserved. LR coverage and paper-ID AO are supplementary and retain all 27 boards in the denominator. AO sorts score then paper ID for ties.

## Method and reproducibility

- Official commit: `8bf74b0a830feb7035c6166dce3394dc344ae532`.
- Frozen extraction input: `D:\C++\SCILEAD\pilot\gpt56_sol_fully\20261024_A2_result_type_recovery\merged\output.json`.
- Input SHA256: `8cca0455ff36be0ab3d2898c5685602b949af6b7044082bf283c1e75b43bc073`.
- Model: `Lajavaness/bilingual-embedding-large`, weights `e83179d7a66e8aed1b3015e98bb5ae234ed89598`; code `dangvantuan/bilingual_impl` at `8079a782f9671d3696b5ab189781480fcca58d25`.
- CPU FP32, four torch threads, seed 0, PYTHONHASHSEED=0. Existing local weights and code were used; no downloads or model API calls.
- Unmodified official normalization main; local model factory, diagnostic search wrapper and per-paper checkpoints reused from full43_cs. Exact labels bypass encoding; all other labels use cosine semantic_search(top_k=1). The official method has no similarity threshold.
- Candidate counts: 23 Task / 71 Dataset / 26 Metric; actual candidate lists and order match frozen full43_cs. No candidate filtering, sorting, thresholding, embedding cache reuse, batching change or preprocessing change.
- 328 exact fields; 677 cosine mappings; 0 top-score tie cases.
- Normalization wall time including model loading/probe: 138.766 seconds.
- Immediately before model load: {"physical_available_GiB": 6.229393005371094, "commit_available_GiB": 17.39307403564453, "working_set_GiB": 0.27166748046875, "peak_working_set_GiB": 0.2716712951660156, "private_GiB": 0.685028076171875, "peak_private_GiB": 0.6851654052734375}.
- Final normalization memory / process peaks: {"physical_available_GiB": 4.294219970703125, "commit_available_GiB": 15.275402069091797, "working_set_GiB": 2.699676513671875, "peak_working_set_GiB": 4.456012725830078, "private_GiB": 3.7348670959472656, "peak_private_GiB": 5.458957672119141}.
- Source, Gold, extraction, previous full43_cs artifacts, model weights/code and package versions passed before/after hash checks. All runtime writes were restricted to this owned branch; network and credential-file access were guarded.
- Official repository initial and final status: `?? __pycache__/`. The pre-existing untracked __pycache__ was not created or removed by this run.

## Files

- normalization/embedding_normalized_output.json: official compatible normalized output.
- normalization/mapping_audit.jsonl and papers/: actual selections, cosine scores, candidate IDs and checkpoints.
- evaluation/: unmodified official tuple outputs, aggregate F1, per-paper metrics and invocation.
- leaderboard_evaluation/official/: official 27-board outputs and invocation.
- leaderboard_evaluation/paper_metrics/ and leaderboards/: supplementary coverage/AO and numeric conversion traces.
- config.json, model_manifest.json, freeze_before.json, reproducibility/: settings, versions, hashes and adapter audit.
- verification.json, metrics.json, artifact_sha256.json: final checks and machine-readable results.

Only the Fully+CS branch was executed; Partially, ColdStart and provider configuration were outside this run.
