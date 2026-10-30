# Offline semantic-alignment evaluation utilities

Goal: implement the user's authorized offline-only specification in this analysis directory.
Architecture: byte-identical audited evaluator and leaderboard helpers; relocate only the IO boundary's analysis/helper roots. A separate readiness/provenance layer gates evaluation and comparison.
Stack: existing Python, standard library, already-installed rbo required by unchanged official evaluator.

1. Write failing boundary/summary/aggregation tests; copy the audited evaluator and helpers with recorded hashes.
2. Implement evaluate_ready.py: eight fixed cases, complete summary + output hash + full 43/295/27 validation, verified reuse, missing-stage polling/skip, no overwrites of unverified evaluations.
3. Implement compare_results.py: same-case baseline differences, all tuple P/R/F1 and six board metrics, per-paper differences, full three-order mean and sample SD, Chinese report and immutable historical references.
4. Run offline unit tests and re-evaluate one completed baseline case inside analysis/verification; compare official numeric results, per-paper values and board results. Generate an honest incomplete report if variant stages are absent.

Constraints: writes only below this analysis path; no credentials, network/API, models, dependency installation, other agents, runtime/Prompt/prediction changes, or baseline changes. No git mutations. The user's explicit instruction to code now supersedes interactive design/approval steps.

Review focus: incomplete/malformed summaries; stale output or evaluation hashes; path traversal and redirected output paths; confusing macro F1 with mean paper F1; incomplete cold-order sets and mismatched scope; report freshness during concurrent generation.
