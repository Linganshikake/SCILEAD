# Pending bounded recovery — NOT authorized or executed

The user explicitly prohibited automatic retries. An asynchronous exception question is pending. No retry may be performed until the user answers affirmatively.

All 43 extractions and 40 normalizations are complete. Three papers failed at their first normalization call with Cloudflare HTTP 502:

| Paper | Failed first input | Total remaining calls |
| --- | --- | --- |
| D19-1367.pdf | Dataset: PTB | 3 |
| K19-1036.pdf | Dataset: SWDA | 3 |
| N19-1373.pdf | Dataset: SwDA | 2 |

The proposal is exactly eight new attempts: one replacement for each of the three failed calls, plus five never-attempted fields. Payloads remain identical to the existing request plans. Already successful extractions and normalization stages must not be repeated.

If authorized later:

1. Record the user's explicit exception and preserve this partial-40 report/evaluation snapshot.
2. Keep all three failed ledgers unchanged. Use separate recovery normalization directories; never remove an `attempt.json` to bypass the guard.
3. Call the existing `normalization(row)` adapter against those new directories, using the same original extraction and original Fully normalization prompt/candidate sets. No automatic retry within recovery; stop a paper again if any request fails.
4. Update manifest indices only to the selected completed recovery results. Keep failed-attempt directory indices for accounting.
5. Include all three historical failed attempts and their unknown usage in API totals. If all eight succeed, expected experiment totals are 499 attempts / 496 successes / 3 archived failures, not 496 attempts.
6. Merge/re-evaluate all 43, run original leaderboard evaluation plus audited supplemental LR/AO, verify unchanged successful files and frozen baselines, and regenerate artifact hashes.

Current known usage: 491 attempts, 488 successes; prompt 416769 + completion 11424 = 428193 tokens. Three failed attempts have unknown billed usage. These are observations, not a provider invoice.
