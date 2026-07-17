#!/usr/bin/env python3
"""
verify_run.py — immediate post-run verification of a pre-test run directory.

Process rule (docs/incident_2026-07-17_shard1_truncation.md): a run's outputs
are committed (text artifacts) and sha-recorded (binary artifacts) immediately
upon completion, before any other operation touches the run directory. Run
this on the pod right after the runner's DIGEST lines print.

Checks:
  - manifest.json parses and contains the required keys
  - the run CSV's row count matches the manifest's expected_rows
  - activations file loads and its `partial` flag is False
    (skipped for screen runs — detected via manifest screen_mode)
  - recomputed sha256 + byte size match the manifest's output_digests
    (skipped with a note for pre-hardening manifests without the key)

Prints PASS/FAIL per check; exit 0 only if every check passes.
stdlib-only except torch, which is imported lazily and only needed to load
activations (screen runs verify without it).

Usage: python scripts/verify_run.py results/pretest/<run_id>
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

REQUIRED_KEYS = ["run_id", "run_role", "model", "model_tag",
                 "probe_file_sha256", "expected_rows", "schema_version"]


def file_digest(path):
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: verify_run.py <run_dir>")
        return 2
    run_dir = Path(argv[0])
    results = []

    def check(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        results.append(ok)
        return ok

    # ---- manifest parses + required keys ----
    try:
        manifest = json.loads((run_dir / "manifest.json").read_text())
        check("manifest.json parses", True)
    except Exception as e:
        check("manifest.json parses", False, repr(e))
        print(f"VERIFY FAIL {run_dir.name}")
        return 1
    missing = [k for k in REQUIRED_KEYS if k not in manifest]
    check("manifest required keys", not missing,
          f"missing: {missing}" if missing else ", ".join(REQUIRED_KEYS))

    # ---- CSV row count vs expected_rows ----
    screen_mode = manifest.get("screen_mode")
    csv_name = f"screen_{screen_mode}.csv" if screen_mode else "generations.csv"
    try:
        with open(run_dir / csv_name, newline="") as f:
            n_rows = sum(1 for _ in csv.DictReader(f))
        check(f"{csv_name} row count == expected_rows",
              n_rows == manifest.get("expected_rows"),
              f"{n_rows} rows vs expected {manifest.get('expected_rows')}")
    except Exception as e:
        check(f"{csv_name} row count == expected_rows", False, repr(e))

    # ---- activations load + partial flag (generation runs only) ----
    if screen_mode:
        print(f"SKIP  activations (screen run '{screen_mode}': logits-only, none expected)")
    else:
        act_path = run_dir / f"activations_{manifest.get('model_tag')}.pt"
        try:
            import torch
            blob = torch.load(act_path, map_location="cpu", weights_only=False)
            check("activations file loads",
                  isinstance(blob.get("activations"), dict),
                  f"{len(blob.get('activations', {}))} prompt_keys")
            check("activations partial flag is False", blob.get("partial") is False,
                  f"partial={blob.get('partial')!r}")
        except Exception as e:
            check("activations file loads", False, repr(e))

    # ---- recompute digests against manifest output_digests ----
    digests = manifest.get("output_digests")
    if not digests:
        print("SKIP  output_digests (key absent — pre-hardening manifest)")
    else:
        for name, recorded in digests.items():
            try:
                sha, size = file_digest(run_dir / name)
                check(f"digest {name}",
                      sha == recorded.get("sha256") and size == recorded.get("bytes"),
                      f"{size} bytes, sha {sha[:12]}… vs recorded "
                      f"{recorded.get('bytes')} bytes, {str(recorded.get('sha256'))[:12]}…")
            except Exception as e:
                check(f"digest {name}", False, repr(e))

    ok = all(results)
    print(f"VERIFY {'PASS' if ok else 'FAIL'} {run_dir.name}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
