# Independent DeepSeek variants implementation plan

**Goal:** Prepare Fully CS, Partially, and Cold Start default/string `0`/string `42` adapters for the new Fully extraction, without running models or reading credentials.

**Architecture:** Retain the historical runtime's official mains, observer paths, same-position replay, masks and candidate rules. Replace its provider dependency with the parent `transport.py`. Preparation waits for both complete Fully artifacts, freezes their content in the original paper order, and derives counts from the new data. Fully CS retains the existing CPU FP32 adapter and local weights.

**Scope:** All writes, test outputs and temporary files stay under this variants directory. Historical source and the scilead environment are read-only. No installs, downloads, evaluations, new extraction, semantic cache or semantic repair. Direct execution in the shared filesystem was explicitly requested; no worktree/commit workflow.

- [x] Add offline boundary tests before implementation: exact DeepSeek payload, immutable same-position replay, blocked uncertain/failed resend, original observer locations, waiting inputs, variable prediction counts and frozen order.
- [x] Adapt `variant_runtime.py` and implement parameterized `prepare_variants.py` with frozen input/config copies, masks and provenance.
- [x] Adapt `fully_cs/cs_common.py` and `fully_cs/run_cs.py`; defer all model imports/loads until explicit execution.
- [x] Run the original observer scenarios with mocked HTTP and confined writes; test the default/string cold orders using the actual official main.
- [x] Review, run the complete owned offline suite, and document files, evidence and commands for main.

Review focus: partial/missing Fully inputs; numeric/type incompatibility without silent repair; source/order drift; uncertain response replay; unknown prediction counts and first-paper CS branch coverage.

Execution complete: five owned offline suites passed in `reproducibility/test_run_1793193203723531700`; current evidence index is `reproducibility/offline_tests.json`. Actual Fully preparation remains waiting for full-scope completion. No model or API execution was performed.

Review: independent read-only review by Cicero. Alternate output-root integration fixed and verified with a failing then passing CS launcher test. Ruling: preserve the inherited crash boundary before `accepted.json`; automatic promotion would change recovery behavior beyond the requested minimal adaptation. Cost: such a crash requires main's manual inspection, with no automatic resend. The new transport regression test confirms this boundary. No deferred minor findings.

User follow-up incorporated: CS alone before concurrent API branches; 4 GiB minimum available physical RAM plus the existing 7.5 GiB commit gate; ctypes maxRSS in checkpoints; no automatic process closing.
