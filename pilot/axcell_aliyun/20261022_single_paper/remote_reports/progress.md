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
