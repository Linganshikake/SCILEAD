# SCILEAD format follow-up implementation plan

**Goal:** Execute the explicitly authorized V2 structural recovery and one conditional 2048 diagnostic without altering formal42.
**Architecture:** Separate immutable raw inputs, frozen parser, checkpointed author-stage replay, and fixed-scope evaluation. All files are in this independent experiment directory, not the official repository.
**Spec:** User attachment c55aad55-df3e-4ab2-8068-e5519c5c334b.
**Tech:** Existing Python/Transformers/LangChain environments; pinned AutoDL SSH; no installations.

- [x] Hash all formal42 files and prior protected source/Gold/evidence; remote GPU/process and manifest check.
- [x] Diagnose complete arrays and truncated object, preserving offsets and exact raw excerpts.
- [x] Write and run failing parser tests; implement V2; run full boundary suite (19 tests).
- [x] Freeze parser/rules/tests hashes before scoring; apply identically to all42 and verify unchanged40.
- [x] Execute official Fully and CS only for recovered rows; reuse unchanged outputs with exact provenance.
- [x] Replay Partially from original start/state/order, reusing only exact position/input/prompt/candidates/config; generate changed requests once.
- [x] Run one authorized 2048 Extraction if input+budget fits; keep independent, Fully/CS single-paper completed.
- [x] Run unchanged official fixed42 tuple/leaderboard evaluators plus existing strict diagnostics; compare unrounded V1/V2.
- [x] Verify original hashes, collect remote artifacts with hashes, summarize real/new/replayed calls and release task models.

Review focus: bracket/escape handling, duplicate keys, alternative-answer headings, trailing partial numbers/records, reuse under changed dynamic candidate state. Tests cover all five; unknown prose is rejected instead of interpreted.

Execution uses the already approved detailed user plan; no new approval gate. No git commit or change to official source is needed. Checkpoint and test evidence are retained instead of deleting a plan workspace.

Final review: self-review (no independent subagent reviewer). Parser boundary suite19 and reuse safety suite6 passed. All40 prior outputs are byte-identical; all4 prior normalization results are unchanged. Full source/state/request exact matching verified for1211 reused requests. Actual record extension compared without Gold.

Engineering rulings: unknown external prose is rejected conservatively; old Token IDs are reconstructed and never presented as original captures. CS custom-code cache isolation was repaired using two byte-identical fixed-revision files; no predictions changed and original failure logs retained. These limitations are disclosed in the reports.

Final remote delivery has its own hash receipt in reports/delivery_transfer.json; this plan is not a substitute for that receipt.
