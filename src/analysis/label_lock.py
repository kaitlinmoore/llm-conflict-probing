#!/usr/bin/env python3
"""
label_lock.py — blindness support (analysis_pipeline_brief.md).

Two functions:
  1. `export_audit` — the researcher's per-cell audit export: generation +
     designed condition + automatic label + uncertainty flag, and NO
     analysis quantity anywhere in the file.
  2. `write_lock` / `verify_lock` — the label lock: sha256 digest of the
     audited label file; the verified tier refuses to run without a lock
     whose digest matches. Any post-lock change is a documented amendment.

Usage:
  python src/analysis/label_lock.py export --run-dir <dir> --out audit.txt
  python src/analysis/label_lock.py lock --labels labels_final.csv \
      --out label_lock.json
"""

import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.pretest.runner_lib import atomic_write, file_digest

FORBIDDEN_IN_AUDIT = ("separation", "cosine", "projection", "r2", "layer",
                      "direction")   # belt-and-braces: none may appear as keys


def export_audit(run_dir: Path, out_path: Path):
    from src.battery import labeler as lb
    rows = list(csv.DictReader(
        (run_dir / "capture_rows.csv").open(encoding="utf-8", newline="")))
    lines = ["# Audit export — generations + designed conditions + automatic "
             "labels. NO analysis quantities. Read blind.", ""]
    for r in rows:
        if r["arm"] != "open_ended":
            continue
        if r["family"] == "refusal":
            lab = lb.prelabel_response(r.get("generation", ""))
            auto = (f"auto={lab['label']}"
                    + (f"/{lab['disclaimer_reluctance']}"
                       if lab["disclaimer_reluctance"] else "")
                    + (" UNCERTAIN" if lab["uncertain"] else ""))
        else:
            auto = "auto=(choice-family: labeled by parse, not this export)"
        lines += [f"=== {r['row_id']}",
                  f"designed: {r['condition']} / "
                  f"expected {r.get('expected_response') or r.get('expected_pick')}",
                  auto, "generation:", r.get("generation", ""), ""]
    text = "\n".join(lines)
    for kw in FORBIDDEN_IN_AUDIT:
        assert f"{kw}=" not in text, f"analysis quantity {kw!r} in audit export"
    atomic_write(out_path, lambda f: f.write(text), mode="w",
                 encoding="utf-8", newline="\n")
    sha, size = file_digest(out_path)
    print(f"DIGEST {sha} {size} {out_path.name}")


def write_lock(labels_path: Path, out_path: Path):
    sha, size = file_digest(labels_path)
    lock = {"labels_file": labels_path.name, "sha256": sha, "bytes": size,
            "locked_utc": datetime.datetime.now(
                datetime.timezone.utc).isoformat(timespec="seconds"),
            "note": "any later label change is a documented amendment, "
                    "never a silent edit"}
    atomic_write(out_path, lambda f: f.write(json.dumps(lock, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    print(f"LOCKED {sha} {labels_path.name}")


def verify_lock(lock_path: Path, labels_path: Path):
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    sha, _ = file_digest(labels_path)
    if sha != lock["sha256"]:
        raise SystemExit("VERIFIED TIER REFUSED: audited label file does not "
                         "match the lock digest (labels changed post-lock — "
                         "re-lock with a documented amendment)")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--run-dir", required=True)
    e.add_argument("--out", required=True)
    l = sub.add_parser("lock")
    l.add_argument("--labels", required=True)
    l.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "export":
        export_audit(Path(args.run_dir), Path(args.out))
    else:
        write_lock(Path(args.labels), Path(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
