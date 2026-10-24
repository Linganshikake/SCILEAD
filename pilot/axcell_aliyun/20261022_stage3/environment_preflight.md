# Stage 3 preflight (read-only audit)

- CPU: 8 logical CPUs. MemAvailable: 28.917 GiB. Filesystem free: 55.811 GiB.
- Persistent mount: /dev/nvme0n1p3, ext4, /root/scilead/axcell. /data is not assumed.
- No running containers, worker units or tmux task at preflight. Port 127.0.0.1:9200 was free.
- 37 PARSE_COMPLETE, 2 FAILED. 643/643 parse artifact hashes matched.
- 91/91 source/model files matched. Dependency pip check passed.
- Prior successful 1511.08308.pdf extraction: 2 records, source SHA256 pinned; reuse only.
- Frozen author36 membership UNVERIFIED.
- Prior kernel oom_kill=1 belongs to recovery cleanup, used as baseline; no claim of historically zero OOM.
- New safeguards: 7 policy tests, 2 cleanup fault-injection tests, transient parent/child process-tree service test passed. No test loaded a model.
- Service isolation changes are transient/per-task; no global memory/swap configuration changed.
- Real generation authorized for 36 additional papers only; no GPT, normalization or evaluation.

Remote-first hashes are in remote_before.json. Local historical protection snapshot: local_frozen_before.json (1661 files).
