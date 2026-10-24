# AxCell formal preparation — stage 0

Goal: produce a hash-frozen proposal and current resource evidence, then stop at P0. The user's supplemental staged protocol supersedes any earlier authorization to batch automatically.

- [x] Read fixed upstream method, official paper Appendix B, local source manifests, Gold metadata and evaluation scripts.
- [x] Audit 43 Gold IDs and 39 existing TeX containers read-only; distinguish byte integrity, source mapping and unknown author-36 membership.
- [x] Read Administrator SSH alias, use prior pinned-host credential mechanism, and audit current ECS without starting services or models.
- [x] Verify existing single-paper artifacts and the two errors from saved cell evidence; no regeneration or phase-1 service startup.
- [x] Save input_manifest.csv, experiment_manifest.json, environment_preflight.md, resource_preflight.md, scope_and_gold_audit.md and evidence hashes.
- [x] Verify output consistency and unchanged protected inputs; report P0 and wait.

Ruling: this is a bounded read-only experimental audit, not a software feature branch. All new files are isolated here; do not change frozen source, credentials, Gold or previous experiment artifacts. No git mutation, package installation, model/TeX download, service start, paid API or batch script execution.
Ruling: author-36 membership must be evidence-backed. Input-ready does not establish original membership or exact TeX-version identity. Proposed input eligibility and approved evaluation scope are separate fields; no formal evaluation is authorized yet.
Ruling: later normalization checkpoint reuse may skip an identical completed request; it must not silently deduplicate repeated fields within a fresh official run. Resolve actual requests at P4, not during stage 0.

Outputs use local root D:\C++\SCILEAD\pilot\axcell_aliyun\20261022_formal. Proposed remote output root /root/scilead/axcell/runs/20261022_formal. Phase-0 data and reports are written locally; remote operations are read-only.

Phase 0 completed. Evidence gates passed; scope author-36 remains UNVERIFIED. STOP AT P0. No P1/batch/model/API authorization inferred.
