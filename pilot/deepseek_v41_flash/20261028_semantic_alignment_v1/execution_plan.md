# Semantic alignment v1 implementation and execution plan

**Goal:** Rerun Partially and three Cold Start orders with one frozen generic semantic-matching clarification, then compare with the original DeepSeek baseline.

**Authorization:** User explicitly requested suitable requirement additions and rerunning these two settings. This is a separately labeled Prompt-improvement experiment. Existing results stay frozen.

**Architecture:** Reuse all 295 new DeepSeek Extraction predictions across 43 papers. Preserve original official stage1/stage2 mains, input order, masking, dynamic labels, response acceptance and evaluation. Append generic clarification only to masked-normalization and leaderboard-normalization system Prompts in an independent file. Keep the original Fully Metric prompt unchanged. No examples, paper identities, Gold correspondences or new context are added.

**Approaches considered:** Clarifying only stage2 isolates its direct effect but leaves stage1 alias fragmentation unchanged. Changing both matching Prompts addresses the user's two-setting request across their full pipeline. We use the latter, with one pre-frozen version and no score-driven revisions. Broader context or rules/dictionaries would introduce extra changes and are not used.

**Tech stack:** Existing Python scilead environment, audited durable DeepSeek transport, original SCILEAD mains, existing offline evaluator.

## Tasks
- [x] Freeze baseline input/output/source hashes; copy minimal independent runner and runtime paths.
- [x] Freeze Prompt additions and diff; validate two changed keys and unchanged user templates/acceptance behavior.
- [x] Run offline transport + original Partially/Cold tests with synthetic responses and guarded network/credentials.
- [x] Review prepared variant and execute four internally serial branches, preserving checkpoints/no auto retries.
- [x] Evaluate both stages; stage2 primary; all43/295, all27; compare against baseline and prior model references.
- [x] Verify actual requests/Prompts, input/Result preservation, source integrity, usage and report; stop.

## Review focus
No reuse of old normalization responses with changed Prompt; no writes to baseline; no response cleanup; unchanged canonical serialization/order and initial masks; no Gold-specific example or manual correction; HTTP/unknown response never resends automatically. Candidate sets after stage1 may evolve differently as a result of changed model answers, as required by the original algorithm.
