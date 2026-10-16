# Threshold=2 source audit and offline preparation

- [x] Freeze all seven requested experiment/reference directories and the official code/Gold files, without reading credentials.
- [x] Inventory original local data and archives; inspect official public source pages and small attachments without executing archive scripts.
- [x] Strict JSON audit: duplicate object keys, schemas, exact TDM strings, distinct paper membership, conflicting Results, missing IDs and duplicate boards.
- [x] Compare original annotations, provided 27 boards and all official candidate artifacts. Generate raw-group diagnostic inventories only, never substitute reconstructed boards for an author artifact.
- [x] Apply READY/BLOCKED gate. No official threshold2 score or masking preview unless provenance and compatibility pass.
- [x] Resolve Fully LLM/CS outputs from manifests; validate identical Zero-shot extraction and frozen predictions. Inspect Partially/Cold Start source dependencies and existing seed/order records.
- [x] If READY, reuse audited offline evaluators for both Fully settings, create original seed0 masking preview, compare all common boards. If BLOCKED, record exact missing materials and leave formal evaluation pending.
- [x] Verify all frozen hashes and emit the requested audit/report/next-stage configuration files; stop with zero LLM/API inference.

Scope: threshold is minimum distinct Gold paper IDs per exact TDM. No prediction-size filter, no name cleaning, no Gold changes, no new extraction/normalization, no API credentials, no package installation. All new files remain in this directory.

Final: audit/reuse/integrity checks complete; READY gate failed. Conditional scoring and masking intentionally NOT RUN. No model inference.
