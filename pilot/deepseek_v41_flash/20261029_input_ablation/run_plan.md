# DeepSeek input ablation implementation and experiment plan

Goal: compare five fixed papers under cached RAG, complete official parsed text/tables, and PDF page images, with identical extraction instructions and original Fully LLM normalization.

Architecture: reuse the frozen 20261028 transport, result compatibility layer and serial Fully runner byte-for-byte in independent arm directories. Prepare different input messages only. Use unchanged official tuple and leaderboard evaluators on identical selected-paper scope.

Tech stack: existing scilead Python, Poppler, Pillow, httpx, tiktoken, official SCILEAD evaluators.

## Fixed decisions

- Original user request authorizes subset experiment execution. On 2026-10-29 user explicitly accepted full-page images because official DeepSeek Files/Vision documentation supports images, not PDF files.
- Five papers selected before any new request, using input availability and deterministic seed 20261029; never select by prediction scores. Record selection population and strata.
- Model/request parameters copied from 20261028: deepseek-flash, thinking enabled, reasoning_effort high, stream false; no client output cap, tools, response_format or model fallback.
- Images: render every page, in page order, PNG at 150 DPI, no OCR/crops/tile selection. Record official server resizing and 1024-token maximum per image.
- Parsed arm: reuse full cached Unstructured elements. Execute the unchanged official extract_text_and_tables method over cached elements. Supply all resulting per-page NarrativeText/Title text plus all tables, keeping original table flattening and caption association. No embedding, Chroma or retrieval rerun.
- Baseline: selected papers from frozen original Fully LLM 20261028, not improved-alignment variants. Zero new baseline requests.
- Candidate sets and their serialized order copied unchanged (23/71/26). No repeated-field cache. Results retained exactly except existing approved numeric-to-string compatibility.
- No automatic retry. Preserve invalid output and uncertain requests; stop affected processing and report.
- Frozen files never changed. New results stay in this directory. Record hashes before and after.

## Tasks and validation

- [x] Locate original PDFs and complete parser caches; verify table equivalence to frozen RAG evidence.
- [x] Freeze selection and evidence hashes before requests.
- [x] Prepare both arms and test message construction, all-page preservation, unchanged table contents, absence of annotations/predictions in inputs and request parameter identity.
- [x] Render visual spot checks and assert image/request bounds.
- [x] Execute each paper once per arm, original Fully normalization, durable request checkpoints.
- [x] Evaluate same selected-paper denominator with official tuple code. Derive leaderboard memberships by restricting existing Gold boards to selected IDs; disclose board count and singleton boards. Report LR/nonempty/PC/RC/numeric RBO/paper-ID AO and strict numeric auxiliary metric.
- [x] Audit successful/failed coverage, actual usage, frozen file integrity and qualitative errors; deliver Chinese comparison report.

Review focus: missing/full-vs-retrieval-only cache; PDF/cache version mismatch; page omission; accidental table enhancement; subset scope mismatch; unknown API state; unsupported format; invalid JSON.
