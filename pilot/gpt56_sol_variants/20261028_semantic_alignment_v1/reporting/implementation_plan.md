# Sol offline audit implementation plan

Goal: audit existing Sol artifacts and render a Chinese report without importing runtime, running evaluation, or making network/model calls.

Scope: all writes stay in this reporting directory. Read the new root's 83-entry protected_hashes.json only; do not inventory historical trees. Use the flat four-branch layout and baseline 20261024. Fixed experiment invariants: 43 papers, 335 predictions, 295 Gold, 27 boards; gpt-5.6-sol, medium, 32768, stream=false; byte-identical DeepSeek prompt. Stage2 is primary and stage1 diagnostic.

Implementation:

1. Add synthetic offline tests for incomplete stages, failed/unknown attempts and authorized retries, changed request/accepted hash, source/order preservation, comparison provenance, and output containment. Observe failure before implementation.
2. Implement a standard-library-only audit_and_report.py, with --out accepting the experiment root or its reporting directory. Scan all api_calls before checking stage completion; preserve unknown usage as null, count accepted logical calls separately from physical attempt evidence. Validate actual messages/parameters and accepted response path/hash.
3. Implement report rendering from the DeepSeek comparison schema. Missing or incomplete analysis is pending; never fabricate metrics. Validate normalized input hashes and scope before reporting full P/R/F1 and leaderboard tables. Derive change examples from matched events and their source hashes.
4. Run focused tests and the real-root audit under a Python audit hook that blocks network/process creation and writes outside reporting. Save proof including before/after protected hashes and actual UTC/Shanghai timestamps. Document final invocation and exit statuses.

Review focus: missing state with a saved request; unknown original followed by accepted retry; malformed accepted reference; a COMPLETE summary with incomplete events; stale comparison from another experiment. Tests live only under reporting and use temporary fixtures there.
