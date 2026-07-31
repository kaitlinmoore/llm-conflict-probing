#!/usr/bin/env python3
"""
extract_value_anchors.py — pull the per-value anchor texts for the
stimulus-similarity analysis verbatim from docs/Value_Roster_Derivation.docx
into data/battery/value_anchors.json, with provenance.

Anchors are the roster's **"Operational definition (behavioral)"** cell for
each value — the definition paragraph, not the bare value word (single words
embed too thinly to be stable anchors). Text is copied verbatim: nothing is
paraphrased, trimmed, or substituted here. Where a definition is unusable
as-is the record carries a `flag` and the researcher decides — authoring a
substitute anchor would make the anchor a Claude artifact rather than the
roster's own definition.

The docx is a table; python-docx is not in the pinned stack, so the reader is
stdlib zipfile + ElementTree over word/document.xml. Table cells appear as
paragraphs in document order, five per value:
  value name / operational definition / source(s) / expected profile / notes

Usage:
  python src/analysis/extract_value_anchors.py
"""

import argparse
import datetime
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Roster heading -> project value key. Order follows the doc's table.
VALUE_KEYS = {
    "Honesty / non-deception": "honesty",
    "Harm-avoidance": "harm_avoidance",
    "Privacy": "privacy",
    "Kindness / emotional consideration": "kindness",
    "Integrity / rule-following": "integrity",
    "Impartiality / balance": "impartiality",
    "Authority / deference": "authority",
    "Care / compassion": "care",
    "Loyalty / partiality": "loyalty",
    "Fairness": "fairness",
    "Autonomy": "autonomy",
    "Justice / desert": "desert",
    "Mercy / forgiveness": "mercy",
    "Collective welfare": "collective_welfare",
    "Sanctity / purity": "sanctity",
    "Tradition": "tradition",
}

# Stage 1 outcomes (HANDOFF_v5 §2) — recorded so the analysis can restrict or
# report by certification status without re-deriving it.
CERTIFICATION = {
    "harm_avoidance": "certified", "care": "certified",
    "impartiality": "certified", "mercy": "certified",
    "loyalty": "certified", "autonomy": "certified",
    "collective_welfare": "certified", "tradition": "certified",
    "privacy": "certified", "honesty": "certified", "desert": "certified",
    "integrity": "merged-candidate", "authority": "merged-candidate",
    "kindness": "unenacted", "fairness": "unenacted", "sanctity": "unenacted",
}

# Definition text that is not purely value semantics. Flagged, never edited.
KNOWN_FLAGS = {
    "authority": ("definition carries a parenthetical about probe design "
                  "('probe design must control epistemic deference and "
                  "ambient instruction-following') — instrument methodology, "
                  "not value semantics; embedding it injects study vocabulary "
                  "into the anchor"),
    "mercy": ("definition ends with document-maintenance text ('Revised at "
              "instrument revision v2; definition of record in §6') — not "
              "value semantics"),
}


def paragraphs(docx_path: Path):
    with zipfile.ZipFile(docx_path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if text:
            out.append(text)
    return out


def extract(docx_path: Path):
    paras = paragraphs(docx_path)
    sha, _ = file_digest(docx_path)
    records = {}
    for i, text in enumerate(paras):
        key = VALUE_KEYS.get(text)
        if key is None or key in records:
            continue
        # the definition is the next paragraph (next table cell)
        if i + 1 >= len(paras):
            continue
        definition = paras[i + 1]
        rec = {
            "value": key,
            "roster_heading": text,
            "anchor_text": definition,
            "certification": CERTIFICATION.get(key, "unknown"),
            "n_words": len(definition.split()),
            "provenance": {
                "source_doc": docx_path.name,
                "source_doc_sha256": sha,
                "heading_paragraph_index": i,
                "definition_paragraph_index": i + 1,
                "field": "Operational definition (behavioral)",
                "verbatim": True,
            },
        }
        if key in KNOWN_FLAGS:
            rec["flag"] = KNOWN_FLAGS[key]
        if rec["n_words"] < 8:
            rec["flag"] = (rec.get("flag", "") +
                           " | very short (<8 words) — may embed thinly").strip(" |")
        records[key] = rec
    return records, sha


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", default="docs/Value_Roster_Derivation.docx")
    ap.add_argument("--out", default="data/battery/value_anchors.json")
    args = ap.parse_args(argv)

    docx_path = Path(args.docx)
    records, sha = extract(docx_path)
    missing = [v for v in VALUE_KEYS.values() if v not in records]
    print(f"anchors extracted: {len(records)}/16 (source sha {sha[:12]}…)")
    if missing:
        print(f"MISSING: {missing}")
    flagged = {k: r["flag"] for k, r in records.items() if "flag" in r}
    for k, why in flagged.items():
        print(f"  FLAG {k}: {why}")

    payload = {
        "_notes": [
            "Value anchor texts for the stimulus-similarity exhibit.",
            "VERBATIM from the roster derivation doc's 'Operational definition",
            "(behavioral)' column. Not authored, not paraphrased. Entries with a",
            "'flag' need a researcher decision before the exhibit run: the anchor",
            "text is a researcher decision, not Claude's.",
            "All 16 roster values are extracted; 'certification' records Stage 1",
            "outcome so analyses can restrict or report by status. Third-value",
            "contamination can come from an uncertified value, so the flag",
            "analysis uses all 16 unless told otherwise.",
            "Note for interpretation: every definition shares the frame 'Pull",
            "toward/against ...', which adds a roughly constant component to all",
            "cell-anchor cosines. Rank-based read-outs (which the analysis uses)",
            "are robust to that; absolute cosines are not comparable to other",
            "corpora.",
        ],
        "source_doc": docx_path.name,
        "source_doc_sha256": sha,
        "extracted_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "anchors": [records[v] for v in VALUE_KEYS.values() if v in records],
    }
    out_path = Path(args.out)
    atomic_write(out_path,
                 lambda f: f.write(json.dumps(payload, indent=2,
                                              ensure_ascii=False) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    o_sha, size = file_digest(out_path)
    print(f"Wrote {out_path}")
    print(f"DIGEST {o_sha} {size} {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
