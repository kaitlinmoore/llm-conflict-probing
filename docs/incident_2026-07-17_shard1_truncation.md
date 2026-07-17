# Incident: shard-1 output truncation, 2026-07-17

**What happened.** IV run shard 1/2 (run
`20260716_165900_llama8b_instrument_validation_shard1of2`, pod EUR-IS-1)
completed cleanly at ~04:49 UTC: run.log shows 497/497 prompt-sets,
generations.csv contains all 2,057 rows. Its activations_llama8b.pt and
manifest.json were subsequently found as zero-byte files with mtimes
~05:55 UTC. Shard 2/2, running the identical write pattern on a second pod
against the same network volume, persisted all outputs intact (04:39 UTC).

**Investigation.** Bash histories on both pods audited: every command touching
the results tree was read-only; the sole `rm` targeted data/pretest/ during an
unrelated pull fix. merge_shards.py opens shard inputs read-only and its first
invocation failed reading the already-empty manifest, timestamping the
truncation as prior to any merge. dmesg unavailable in-container. Volume quota
exonerated (29GB free at discovery).

**Verdict.** Unattributed durable-write failure on the pod-1 MooseFS mount
during run finalization: consistent with page-cache writes succeeding (and
completion log lines printing) while write-back to the volume server failed,
leaving created-but-empty files at flush-attempt time. Contributing design
exposure: whole-file in-place checkpoint rewrites of the activations artifact.

**Impact.** No generation data lost (CSV intact and committed). Shard-1
activations and manifest require a re-run; the administration itself (frozen
instrument sha 659afb97…, fixed seeds) is unaffected. Loss bounded to
GPU-hours by prior design decisions: incremental CSV writes,
activations-declared-re-derivable, manifests-from-runs-only.

**Response.** Hardening landed same-day (this commit): atomic
tmp-then-fsync-then-rename on all manifest/activation writes in runner and
merge; completion digests computed by re-reading persisted files and printed +
recorded in manifests; scripts/verify_run.py for immediate post-run
verification; env guard against duplicate-venv builds. Deferred to the
pre-certification round: part-file (append-style) activation checkpoints to
eliminate in-place rewrites entirely; RunPod support ticket optional.

**Process rule adopted.** A run's outputs are committed (text artifacts) and
sha-recorded (binary artifacts) immediately upon completion, before any other
operation touches the run directory.
