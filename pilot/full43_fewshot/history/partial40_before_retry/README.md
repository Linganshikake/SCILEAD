# Few-shot experiment execution

Only this directory may be written. Official source and all frozen experiments remain read-only. Python: `D:\miniconda3\envs\scilead\python.exe`. Set `$env:PYTHONHASHSEED='0'` before every command; use `-B -X utf8`.

1. `prepare.py` runs once: hash frozen experiments, verify 43 evidence bundles, capture official demonstration and immutable request plans.
2. `test_offline.py` is free: actual RetrievalQA formatting and original normalization with mock replies; verifies checkpoint replay and failure controls.
3. `run.py --stage extract`, then `run.py --stage normalize`: paid API stages already authorized for this experiment. Recorded complete or failed stages are skipped. An unresolved `attempt.json` cannot be automatically resent. Repeated normalization values at different positions each retain their original independent request.
4. `evaluate.py`: merge eligible outputs, run original `tdm_eval.main`, aggregate usage and comparisons. Failed papers remain in manifest and explicit coverage.
5. `leaderboard/run_official_leaderboard_eval.py`, then `leaderboard/evaluate_paper_metrics.py`: original leaderboard evaluation and previously audited supplemental LR/AO; run only with full 43-paper coverage.
6. `finalize.py`: offline original normalization replay, original baseline evaluation recheck, frozen directory/source/Gold/dependency hash verification and reports. `artifact_sha256.json` indexes this directory's final artifacts, excluding itself.

No automatic API retries, JSON repair, evidence truncation, response selection, or semantic normalization cache. Failed/uncertain requests require human review before any new attempt. Restart replays only identical completed positions if a worker was interrupted before the final stage summary. HTTP payloads and raw response bodies are saved without Authorization headers or keys.

Normalization's separate `normalization_input/config.json` deliberately sets the upstream dispatch flag `is_few_shot=False`: the requested experiment changes extraction only. The extraction config remains `is_few_shot=True`. Result strings are not changed.

Official F1 is derived from macro Precision/Recall. Strict numerical equality, LR and AO are explicitly supplemental; PC/RC/RBO retain original functions. Do not change mathematical behavior (including duplicate handling or substring Result matches) to improve scores.

Old source_documents are scientific paper text, never extracted answers or Gold mappings. The official MATCHSUM demonstration is included once in System, preserving its ROGUE spelling and apparent Multi-News/WikiHow mismatch.

Stop after this run; no threshold=2, other models or algorithm improvements.
