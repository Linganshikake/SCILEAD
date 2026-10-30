# DeepSeek standardization variants

Independent adapters for Fully CS, Partially, and Cold Start default / string `"0"` / string `"42"`. All output paths are under this directory. The frozen repository, historical experiments, model assets and existing `D:\miniconda3\envs\scilead` environment stay unchanged. Main owns Fully extraction and all evaluations.

This delivery performs offline preparation/testing only. No credentials, network requests, model weights, model inference, installs or downloads are needed for the offline suite. It uses the actual parent `transport.py` with `httpx.MockTransport`. Test subprocesses prohibit sockets, credential-file reads, model-weight reads and writes outside this directory. Original stage modules import installed libraries; their model factories are never called.

## Changed files

| File | Purpose / changes from the reference |
| --- | --- |
| `variant_runtime.py` | Adapted from the Sol runtime: deferred parent `transport.py` import; DeepSeek model/endpoint; credential loader delegated to parent only for later live execution; owned library-cache paths; optional mocked HTTP for full-branch tests. Official mains, observer imports, field decisions and replay are retained. Empty extraction checkpoints do not assume a first field event. |
| `prepare_variants.py` | Parameterized input readiness, copies, orders, masks, config, counts and integrity manifest. Does not run models. |
| `runtime_policy.py` | Owned path validation and offline test/preparation guards. |
| `fully_cs/cs_common.py` | Existing local CPU FP32 adapter; paths adapted; verifies prepared source/input hashes and existing model hashes at explicit execution; ctypes peak working set exposed as `max_rss_bytes` / `max_rss_GiB`. |
| `fully_cs/run_cs.py` | Existing original-main execution, top-1 cosine, tie audit and paper checkpoints. First-paper exact/nonexact coverage is recorded instead of assumed. Adds durable execution status with memory/peak RSS. |
| `run_offline_tests.py`, `offline_entry.py` | Isolated, repeatable, guarded offline suite and JSON evidence. |
| `test_transport.py` | Historical durable transport cases adapted to exact DeepSeek wire contract. |
| `test_original_partially.py`, `test_original_cold_start.py` | Historical official-main observer scenarios; only output roots/import bindings changed. |
| `test_adapters.py`, `test_frozen_protocol.py` | Readiness, variable/zero prediction counts, original observer paths, actual frozen masks/orders and CS resource/import checks. |
| `implementation_plan.md`, `adapter_changes.json`, this file | Plan, source/destination hashes and handoff. |

Generated `reproducibility/` artifacts are synthetic test evidence, not experimental predictions. Each suite run gets a separate directory; previous evidence is retained. `reproducibility/offline_tests.json` points to the latest complete suite. Existing library warnings are retained in logs; no dependency changes are made to remove them.

## Preparation and input contract

Default inputs:

- `../fully/merged/output.json`: new extraction with main's approved Result-to-string compatibility already applied. Do not use `raw_output.json`.
- `../fully/merged/normalized_output.json`: completed Fully LLM normalization.
- `../fully/verification.json`: full-scope completion marker from main.
- `../evaluation_scope.json`: main's frozen Gold and leaderboard scope, checked against the historical reference.
- Reference: `D:\C++\SCILEAD\pilot\gpt56_sol_variants\20261024`.

Preparation waits until the marker reports the full frozen paper count, no protected-file changes, no stop, and a passing secret scan; both files must contain that exact paper set. The marker's record count must match the extraction. Each paper must preserve Result values, row count and source documents between extraction and normalization. Malformed/incompatible complete data is rejected without semantic repair. Prediction count can be zero or any other value; no historical `335`, `1005`, first-paper branch-coverage or call-count assumption is used.

The frozen order is taken from the reference's `partially/paper_order.json`; only the outer paper dictionary is reordered. Per-paper extraction strings, row/field order, duplicate rows and source documents remain intact. Cold permutations use `random.Random("0")` and `random.Random("42")`, and must equal the historical order files. The official main still performs its original `random.seed`/`random.sample` sequence using those string seeds. Masking stays at seed 0, and `PYTHONHASHSEED=0` is required before interpreter startup.

Preparation copies Gold, leaderboards, masks, initial labels, candidate labels and small existing Hugging Face implementation files. Model weights remain at their existing pinned local snapshot. No old extraction predictions or embeddings are reused. Counts and exact/CS field budgets are derived from the new input. A second preparation verifies immutable hashes and returns the existing manifest; changed prepared inputs are rejected.

`--output-dir` must be this directory or a descendant. Other parameters: `--fully-output`, `--fully-normalized`, `--fully-verification`, `--reference`, `--scope`, `--poll-seconds` (default 15, maximum 60), `--timeout-seconds` (0 = indefinite), and `--no-wait` (exit 2 when incomplete). No background waiter is started by this delivery.

## Commands

Run the offline suite now or later, using the unchanged environment:

```powershell
$taskPython = 'D:\miniconda3\envs\scilead\python.exe'
$variantRoot = 'D:\C++\SCILEAD\pilot\deepseek_v41_flash\20261028\variants'
$env:PYTHONHASHSEED = '0'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $taskPython -X utf8 -B "$variantRoot\run_offline_tests.py"
```

Wait for Fully and prepare the actual variants (no credentials/model/API required):

```powershell
& $taskPython -X utf8 -B "$variantRoot\prepare_variants.py"
```

For an immediate readiness check, add `--no-wait`. Exit 2 means Fully is not yet complete; it is not permission to run a partial scope. The new normalized Fully file is copied to `inputs/normalized_output.json` and `merged/normalized_output.json` for main/evaluator consumers. The four LLM variants and CS all use `inputs/output.json` as their extraction input.

After preparation, main runs CS **alone first**. This command loads the existing local embedding model and is intentionally not part of the offline suite:

```powershell
& $taskPython -X utf8 -B "$variantRoot\fully_cs\run_cs.py"
if ($LASTEXITCODE -ne 0) { throw 'CS blocked or failed; inspect its execution_status.json and resource checkpoints' }
```

CS checks at least 4 GiB available physical RAM and the existing 7.5 GiB available commit headroom before importing torch and again before model loading. RAM is measured afresh; the earlier user-reported free memory is not reused. No process is automatically closed. `blocked_resources.json`, `memory_before_torch_import.json`, `memory_before_model_load.json`, per-paper `complete.json`, `normalization/summary.json`, and `execution_status.json` preserve resource results. `memory.max_rss_bytes` is the process's Windows peak working set, measured by ctypes; no psutil dependency.

After CS exits successfully and releases its model, main can run four independent branches concurrently; each remains internally serial. These are live API commands and are intentionally not executed by this delivery:

```powershell
$branchProcesses = foreach ($branch in @('partially', 'cold_default', 'cold_0', 'cold_42')) {
    Start-Process -FilePath $taskPython `
        -ArgumentList @('-X', 'utf8', '-B', "$variantRoot\variant_runtime.py", '--branch', $branch) `
        -WorkingDirectory $variantRoot -WindowStyle Hidden `
        -RedirectStandardOutput "$variantRoot\$branch\runtime.stdout.log" `
        -RedirectStandardError "$variantRoot\$branch\runtime.stderr.log" -PassThru
}
Wait-Process -Id $branchProcesses.Id
$branchProcesses | ForEach-Object { $_.Refresh(); [pscustomobject]@{ Id = $_.Id; ExitCode = $_.ExitCode } }
```

To run or resume one branch, use `variant_runtime.py --branch cold_0` (or another branch name). If preparation used an alternate `--output-dir`, pass that same prepared root to `variant_runtime.py --output-dir ...` and `fully_cs/run_cs.py --output-dir ...`; the installed adapter's offline evidence is shared. Stage outputs are `<branch>/stage1/normalized_output.json` and `<branch>/stage2/leaderboard_normalized_output.json`. CS output is `fully_cs/normalization/embedding_normalized_output.json`. No evaluation script is added here.

## Preserved protocol and checks

The runtime imports `D:\C++\SCILEAD\pilot\full43_partially\engine.py` and `...\full43_cold_start\engine.py` observers, binding their `common` import to this adapter. Actual normalization runs the unchanged `tdm_llm_masked_normalization.main`, `leaderboard_llm_normalization.main`, and (CS) `tdm_embedding_normalization.main` in the frozen repository. The official seven-key `prompts.json` is used; the Fully preparation's three-key subset is not substituted.

Parent transport owns the exact request payload and response validation: `deepseek-flash`, thinking enabled, high reasoning effort, `stream=false`, no client output caps. It accepts its exact documented alias/version variants. No prompt cleanup, output cleanup, candidate sorting, new thresholds, batching, repeated-name memoization or embedding cache is added.

Durable responses are replayed only at their original request position after checking request and response hashes; replay rebuilds official mutable label state and verifies events. Failed/unknown attempts never resend automatically. The inherited explicit one-retry mechanism remains limited to matching 524 or the historical exact quota-error authorization, and no such authorization files are created for actual runs. Identical names at different method positions remain independent calls.

The inherited acceptance boundary is intentionally retained: if execution stops after `response.json` is saved but before `accepted.json`, restart pauses even for HTTP 200. It neither promotes the response automatically nor sends again. That boundary requires manual inspection/recovery by main; changing the reference recovery semantics is outside this adaptation.

Offline verification covers original null/exact skips, exact candidate answers, new-label additions under the original Partially/Cold rules, invalid/quoted answers, unchanged Result/documents, stage-2 member mapping and unmatched preservation, interruption/replay event equality, no duplicate sends, frozen masks, all string-seed paper orders, input completion and prediction counts including an empty extraction. CS import and resource checks never instantiate an encoder; numerical CS output is deliberately untested until main's explicit local execution.
