# Execution ledger — AxCell ECS single-paper validation, 2026-10-22

Scope: one frozen paper 1511.08308.pdf, source 1511.08308v5; no paid API, no batch.
User specification: latest single-paper limits and permission to continue on the configured ECS.
1. Audit ECS and fixed source/resources.
2. Transfer allowlisted existing source/models/one TeX with hashes; isolated legacy environment; pinned official images.
3. Run official TeX conversion, inspect artifacts, stop converter.
4. Start only required local Elasticsearch, execute official CPU AxCell extraction with resource monitoring.
5. Preserve raw results, reports and integrity checks; stop own services and await batch authorization.

Ruling: reuse the frozen single-paper selection; move execution to ECS under a new task directory, preserving all Windows resources. Windows 6 GiB gate is replaced by the same minimum available RAM on the actual Linux execution host. No Windows WSL/Docker is started.
Ruling: this is environment/experiment execution, not a production-code branch; use task-local scripts and checkpoint ledger without changing frozen repositories or creating unrelated git commits.
Shared interfaces: frozen manifests -> hash-checked transfer -> original environment/source; official parsed files -> original ResultsExtractor; raw output -> field-only SCILEAD adapter. No method changes authorized.

Status: audit in progress.

Task 1 complete: ECS 8 CPU, ~29 GiB free RAM, ~70.8 GiB disk free; existing Docker active with no containers/images. No new global Docker service. Task 2: allowlisted source/bootstrap (84 files) and archived models transferred; source hashes verified. Solver dry-run active.
Engineering issue: helper import changed sys.path[0]; explicit local path corrected before any solver had run. No experiment output was affected.

Task 2 update: remote model archive and all 7 extracted model files verified against existing local SHA256; no model loaded. Monitoring smoke and graceful SIGTERM timeout tests passed. Original Conda dry-run succeeded after 550.67s, all 20 explicit original version pins match, 141 packages / 201390244 download bytes. Frozen conda-explicit.txt installed in isolated prefix; installation in progress.
Ruling: use official torch 1.3.1+cpu / torchvision 0.4.2+cpu artifacts for CPU execution, retain original environment.yml unchanged and all other official pip requirements; no algorithm/weight/threshold alteration.
Ruling: restore only upstream 100755 bits for two shell scripts after Windows transfer; content hashes unchanged.
Docker Hub direct access timed out; existing daemon mirrors are fetching the exact previously verified image digest, no global daemon configuration changed.

Task 2 update: Conda explicit install completed (1074.39 s, 141 packages). pip GitHub transfer exhausted bounded timeouts before package installation. Verified original spaCy 2.2.5 official archive relayed via local HTTPS + pinned SSH, SHA256 60b69065c97fd2e4972c33300205e1dead3501d2e0bfd6a182c3a033e337caee. Public SciSpacy package local DNS failed; server official S3 transfer works and is in progress. Existing task pip cache and all original pins retained. CPU artifacts use official PyTorch URLs. No global pip settings changed.
Ruling: do not add an explicit Paper.init/Fragment.init step. The original results-extraction notebook starts a fresh ES instance and directly calls ResultsExtractor; preserve that sequence and its indexing behavior. Adding mappings without an upstream call would change context retrieval behavior. Future genuine schema failure must be diagnosed, not silently bypassed.

Independent read-only review completed: official entry points and observer payloads match upstream; no algorithm changes identified. Fixed three orchestration findings before any conversion/extraction: stable Docker collection proxy ensures actual run receives digest/memory/CPU/network/task-label guards; failed-attempt output directory prevents overwrite; monitor finally cleanup covers early parent exit, signals and monitor exceptions, preserving ES only across its explicit startup-success boundary. Regression evidence: original volatile-collection test failed then passed; original orphan test left a live owned child (safely killed by test), revised test had zero remaining live descendants after bounded graceful/forced cleanup. Only synthetic child processes were used, no model inference. New scripts remain outside official source.

Task 2 compatibility finding: real original Docker SDK 4.1.0 failed with solver-selected requests 2.32.2 / urllib3 2.2.1 (http+docker transport). Fixed only these unpinned transitive HTTP dependencies to requests 2.31.0 / urllib3 1.26.20. Exact two-package diff saved; actual SDK automatic negotiation succeeded against Engine 29.9.2 API 1.56. Runtime transport wrapper requests version=auto only for original PaperExtractor construction; no official source modification. Actual SDK containers property is not stable, confirming guard fix was necessary.
Task 3 complete: TeX conversion/parse succeeded once for 1511.08308v5, 25.493 s original call / 27.37 s monitored stage, 154 fragments, 11 parsed table regions (includes Figure 4 tabular content; unchanged). Container sampled peak 295030784 bytes; cgroup exact memory.peak unavailable and recorded null. Host process group sampled peak 127287296 bytes. No swap, no OOM, conversion container removed by original remove=True; no task container left running. Original parsed output preserved; model extraction pending full Python dependencies. Both fixed images downloaded and original 7 model files reused.

Final status: single-paper official CPU extraction complete. pip check passes; all original explicit pins match with CPU wheel build exception; seven transitive compatibility constraints recorded. First model initialization failed before inference on fastprogress console zero-total division; original failure preserved. A display-only wrapper passed empty/nonempty equivalence checks; second initialization and single inference pass succeeded, 2 raw predictions, 4.643 s model loading / 65.271 s inference. Offline source-table inspection found Recall/F1 misbinding and dataset-size row extraction; no predictions corrected or regenerated. Owned services and temporary PyPI relay stopped. All allowlisted original local/remote assets and synchronized report hashes match. No paid API, normalization, evaluation or batch executed. See final reports and manifest.
