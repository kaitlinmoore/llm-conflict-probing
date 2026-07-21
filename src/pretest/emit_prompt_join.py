#!/usr/bin/env python3
"""
emit_prompt_join.py — regenerate the rendered prompt for every prompt_key of a
completed run and emit <run_dir>/prompt_join.csv (columns: prompt_key,
prompt_text), one row per distinct prompt_key in generations.csv.

The mapping goes through the runner's own rendering path
(runner_lib.enumerate_tasks over the frozen probe file), so prompt_text is the
prompt as administered — freezer output with self_template application, role
rendering, and swap_at_freeze already applied — never re-derived from raw
probe fields. Chat templating (manifest anchor_spec) is applied by the runner
at tokenization time and is deliberately NOT included: prompt_text is the user
message the model was shown.

Verifications (exit 1 on any failure):
  - sha256 of --probes matches the run manifest's probe_file_sha256
  - every distinct prompt_key in generations.csv joins to exactly one rendered
    prompt (zero misses, zero duplicates)
  - every needs_manual_label=yes choice row's rendered prompt contains both
    option texts verbatim (rubric C1 applicability)

On success the file's sha256+bytes are recorded in the manifest's
output_digests (same style as the runner's entries; verify_run.py then checks
it like any other output) and a DIGEST line is printed.

Usage: python src/pretest/emit_prompt_join.py \
    --run-dir results/pretest/<run_id> --probes data/pretest/pretest_probes_v2.jsonl
"""

import argparse
import csv
import json
import sys
from pathlib import Path

try:
    from src.pretest import runner_lib as rl
except ImportError:  # running as a plain script
    import runner_lib as rl


def build_prompt_map(records):
    """prompt_key -> rendered user_text via the runner's task enumeration.
    Raises on duplicate prompt_keys (would make the join ambiguous)."""
    mapping = {}
    for task in rl.enumerate_tasks(records):
        key = task["prompt_key"]
        if key in mapping and mapping[key] != task["user_text"]:
            raise ValueError(f"Duplicate prompt_key with differing text: {key!r}")
        mapping[key] = task["user_text"]
    return mapping


def distinct_keys_in_order(gen_rows):
    seen, order = set(), []
    for row in gen_rows:
        k = row["prompt_key"]
        if k not in seen:
            seen.add(k)
            order.append(k)
    return order


def choice_record_for_key(records_by_render_id, prompt_key):
    """Frozen record behind a choice prompt_key ('<render_id>::<variant>')."""
    render_id = prompt_key.rsplit("::", 1)[0]
    return records_by_render_id.get(render_id)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--probes", required=True)
    args = ap.parse_args(argv)

    run_dir = Path(args.run_dir)
    probes_path = Path(args.probes)
    failures = []

    def check(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)
        return ok

    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    probe_sha, _ = rl.file_digest(probes_path)
    check("probe file sha256 matches manifest probe_file_sha256",
          probe_sha == manifest["probe_file_sha256"],
          f"{probe_sha[:12]}… vs manifest {manifest['probe_file_sha256'][:12]}…")

    records = [json.loads(l) for l in probes_path.read_text().splitlines() if l.strip()]
    prompt_map = build_prompt_map(records)
    records_by_render_id = {r["render_id"]: r for r in records if "render_id" in r}

    with open(run_dir / "generations.csv", newline="", encoding="utf-8") as f:
        gen_rows = list(csv.DictReader(f))
    keys = distinct_keys_in_order(gen_rows)

    misses = [k for k in keys if k not in prompt_map]
    check("every generations.csv prompt_key joins (zero misses)",
          not misses, f"{len(keys)} distinct keys" if not misses else f"missing: {misses[:5]}")

    # rubric C1 applicability: manual-label choice rows must show both options
    manual_keys = sorted({r["prompt_key"] for r in gen_rows
                          if r.get("needs_manual_label") == "yes"})
    print(f"needs_manual_label=yes rows: {len(manual_keys)} distinct prompt_keys")
    for k in manual_keys:
        rec = choice_record_for_key(records_by_render_id, k)
        text = prompt_map.get(k, "")
        ok = (rec is not None
              and rec.get("option_a", "") in text
              and rec.get("option_b", "") in text)
        check(f"both option texts present in rendered prompt: {k}", ok)

    if failures:
        print(f"EMIT FAIL — {len(failures)} check(s) failed; prompt_join.csv not written")
        return 1

    out_path = run_dir / "prompt_join.csv"

    def write_rows(f):
        # LF terminator (csv default is \r\n): keeps bytes identical across
        # platforms so the recorded digest verifies everywhere (.gitattributes
        # disables eol conversion for *.csv for the same reason)
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["prompt_key", "prompt_text"])
        for k in keys:
            w.writerow([k, prompt_map[k]])

    rl.atomic_write(out_path, write_rows, mode="w", newline="", encoding="utf-8")

    sha, size = rl.file_digest(out_path)
    manifest.setdefault("output_digests", {})[out_path.name] = {
        "sha256": sha, "bytes": size}
    rl.atomic_write(manifest_path,
                    lambda f: f.write(json.dumps(manifest, indent=2)), mode="w")

    print(f"Wrote {out_path} ({len(keys)} rows)")
    print(f"DIGEST {sha} {size} {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
