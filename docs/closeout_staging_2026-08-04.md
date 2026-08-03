# Close-out staging report — inventories, verdict vocabulary, batch dry-run, diagnostics

Produced by: Claude Fable 5 (model id `claude-fable-5`), 2026-08-04, per the
design-chat close-out staging request. **Nothing applied, nothing exempted,
workbook text untouched.** Validation remains red by design (now 16 blocking:
the 6 known global-scope lexeme hits + 10 new insert↔option overlap hits, all
expected to stand until their batches land).

Provenance: inventories run on the committed drafts (ingest of 2026-07-31;
`ingest_manifest.json` sha256 `367c5fecdc4e…`; stimulus text unchanged by the
review pass per manifest A8 — verified indirectly by the dry-run's 40/41
byte-exact matches against the current workbooks). Dry-run reads the live
workbooks directly. Diagnostics reuse the provisional embedding run
`20260731_174816_ingnoingest_PROVISIONAL` (encoders
`all-mpnet-base-v2` @ `e8c3b32e`, `all-MiniLM-L6-v2` @ `c9745ed1`; drafts
digest-verified 17/17 against its manifest).

---

## Step 0 — review pass protected

- WIP checkpoint committed (`a0d1ba8`, "review pass complete, pre-batch"),
  10 workbooks (T1–T10). No Excel `~$` lock files were present.
- T11/T12 workbooks unmodified since authoring — consistent with the blank
  delta-review verdicts.
- **Discrepancy flagged, not resolved:** manifest A8 says T9's three
  topical-control verdict cells "still read None — enter the three approves
  during the delta-review session." The current T9 workbook already carries
  `approve` on all three controls (as do T8's and T10's and T2's four). Either
  the researcher entered them after A8 was drafted or A8 is stale. No action
  taken; the delta-review instruction in A8 should be reconciled.

---

## Inventory 1 — insert↔option overlap (+ permanent validator check)

**Check implemented** in `validate_battery.py` as blocking check **f**, with
per-instance exemptions in `data/battery/overlap_exemptions.json` (same
always-printed/never-silent/stale-reported contract as blocklist exemptions;
none granted). Criterion: ≥ 4 shared contentful word **types** between a
cell's stem / shared opposition text / condition insert (matched separately)
and either option, with character names and function words masked.
**Calibration note (flagged as an interpretation):** the brief's phrasing was
read first as a contiguous-run criterion; that reading **cannot fire on the
researcher's own seed cells** (T1 S2/S4/S5 are paraphrases whose contiguity
is broken by small insertions — "the middle [section] loses momentum", "sit
[quite] right"). The committed check is therefore set-based, calibrated so
all three seeds fire; the longest contiguous run is attached to each hit for
readability. If the researcher intended strictly contiguous matching, say so
and the seeds will need a different criterion. 12 new tests; suite 216 OK.

**Hits: 10 (all blocking, all left failing).** Stem/shared hits are reported
once per scenario (`:*` = rides all 4 / both oppose cells).

| # | location | role | vs | shared contentful words | longest run |
|---|---|---|---|---|---|
| 1 | T1 CB-hc-S1 agree_A | insert | option_A | anecdote, ending, fell, flat | "and the ending fell flat" |
| 2 | T1 CB-hc-S1 :* | shared | option_A | anecdote, dragged, ending, fell, flat | "anecdote dragged and the ending fell flat" |
| 3 | T1 CB-hc-S2 agree_A | insert | option_A | convinces, loses, middle, momentum, villain | "loses momentum and the villain never" |
| 4 | T1 CB-hc-S2 :* | shared | option_A | convinces, loses, middle, momentum, quite, villain | "loses momentum and the villain never quite convinces" |
| 5 | T1 CB-hc-S3 :* | shared | option_A | demo, ending, felt, lost, room, rushed | "lost the room and the ending felt rushed" |
| 6 | T1 CB-hc-S4 agree_A | insert | option_A | awkwardly, date, format, heading, reads | "heading reads awkwardly and" |
| 7 | T1 CB-hc-S4 :* | shared | option_A | awkwardly, date, format, heading, reads | "heading reads awkwardly and" |
| 8 | T1 CB-hc-S5 agree_A | insert | option_A | don't, right, shoulders, sit | "the shoulders don't sit" |
| 9 | T1 CB-hc-S5 :* | shared | option_A | don't, quite, right, shoulders, sit | "the shoulders don't sit quite right" |
| 10 | T3 CB-md-S1 :* | stem | option_A | driving, extra, take, two, weeks | "two extra weeks of driving" |

**Formula-wide vs incidental:** the pattern is **formula-wide in T1 and
incidental elsewhere**. T1's shared opposition text states the flaw that
option_A then names — all five scenarios hit; and 4/5 agree_A inserts restate
the same flaw (the flaw-establishment-plus-alignment design already noted in
the accepted length flags). T3 CB-md-S1 is a lone stem hit (the stem states
the penalty option_A imposes). 18 cells carry overlap in total (5 shared × 2
+ 4 inserts + 1 stem × 4).

**Tip-direction asymmetry: none in the tips.** Every hit is against
**option_A** and none originates in an oppose_tip insert — tipping inserts
are clean. The overlap lives in the agreement-cell and shared-text machinery,
and shared text is direction-neutral (byte-identical across both oppose
cells), so no tip_A/tip_B asymmetry is introduced.

**Refusal-family extension (informational, non-blocking):** implemented as an
ask-echo check — inserts/shared text vs the stem's final ask sentence, same
criterion. **Zero flags** on the current battery. (This check re-runs
meaningfully after the A5/A6 ask re-aims land, since they rewrite the ask
sentences.)

Paraphrase drafts for the 10 hits come from the design chat (manifest B1);
none authored here.

---

## Inventory 2 — em dashes (no replacements proposed)

Counts are em dashes (U+2014) in stimulus fields. "Unique" counts each stem /
shared text once; "as administered" multiplies by rides (stem ×4, shared ×2;
controls ×1).

| text role | unique | as administered |
|---|---|---|
| stem | 58 | 226 |
| shared opposition | 57 | 114 |
| condition insert | 243 | 243 |
| options | 0 | 0 |
| **total** | **358** | **583** |

By family (unique): refusal 224, choice 134. One control carries em dashes
(T2 TC-pc-1 stem, ×2).

Insert em dashes by condition (unique): oppose_tip_refuse **60**,
agree_comply 37, agree_refuse 34, oppose_tip_comply 31 (refusal family);
agree_B 29, oppose_tip_A 26, agree_A 20, oppose_tip_B **6** (choice family).
Distributional reading for the ruling: em dashes are ~2× denser in the
refusal family, heaviest in oppose_tip_refuse inserts; within the choice
family there is a real condition skew (oppose_tip_A 26 vs oppose_tip_B 6).

**Interaction flagged:** the A5/A6 re-aims and several A7 replacements
*introduce 14 new em dashes* into stems/shared text while the em-dash ruling
(B2) is pending. If the ruling normalizes em dashes away, the batch
replacement wordings should be finalized to the post-ruling convention before
apply, or T11/T12 will need a second stem touch.

---

## Inventory 3 — rename mapping (ruling table, researcher approves)

Constraints applied: battery-unique, no shared-4-letter-prefix collision
against the full post-rename name inventory, no blocklist or value-adjacent
echoes, demographic texture and (where stated) gender preserved. Keep-side
chosen as the type where the name is most entrenched (most fields/scenarios).
"Mom" kept per standing ruling (appears T4/T8/T9).

| character | keeps name in | rename in | proposed | gender in text | notes |
|---|---|---|---|---|---|
| Dana | T1 CB-hc-S1 (toast; stem + inserts) | T4 CB-lh-S5 | **Rowan** | unstated (the "his" nearby is Neil's) | unisex like Dana; no prefix neighbor |
| Sam | T4 CB-lh-S4 (page-keeper; stem, option, insert, shared) | T1 CB-hc-S5 | **Miles** | male ("he's in this weekend") | |
| Sam | 〃 | T3 CB-md-S1 | **Casey** | unstated | unisex; insert-only, 2 mentions |
| Marcus | T5 CB-ta-S5 (club lead; stem, option, insert, shared) | T1 CB-hc-S3 | **Andre** | male | avoids victory/desert adjacency of an earlier candidate |
| Devon / Devora | Devora stays, T10 CB-pvc-S4 | Devon, T3 CB-md-S1 | **Trent** | male | clears the devo- near-collision; Devora's texture preserved |

Post-rename check: proposed names {Rowan, Miles, Casey, Andre, Trent} are
mutually prefix-distinct and prefix-distinct from every existing battery name
(Rafael/Renee/River/Rosa/Ruth, Marisol/Maya/Miriam, Cole/Cotter,
Aisha/Amir/Ana/Astrid/Adair, Talia/Tessa/Theo all clear at 4 letters).
No proposed name matches or echoes any blocklist lexeme.

**Adjacent, flagged not proposed (outside the brief's list):**
(a) `Priya` (T4) vs `Priyanka` (T10) is a true 4-letter near-collision the
validator already flags; (b) `Dev` (T2 CB-pc-S5) sits below the 4-letter bar
but is visually adjacent to Devon/Devora; renaming Devon→Trent leaves
Dev↔Devora as the remaining pair. Researcher's call whether either joins the
rename batch.

---

## Step 2 — verdict vocabulary

- **Ingest:** `reviewer_verdict` is carried **byte-verbatim** into
  `metadata.reviewer_verdict` (`ingest_workbook.py:248`) — no strip, no
  case-fold. Same for controls.
- **Freeze filter:** the battery freezer **does not exist as code yet**. The
  contract is documented in two places and both say the same thing: only
  `reviewer_verdict == "approve"` rows are freeze-eligible
  (`battery_schema.md`; `ingest_workbook.py` docstring). As documented that
  is **exact string equality: lowercase, case- and whitespace-sensitive**.
  **No third state exists anywhere in code or schema** — `edit`, `reject`,
  blank, and anything else are all just ≠ `approve` and would be silently
  dropped.
- **Current workbook contents vs the filter:** tokens actually present:
  `approve` (166 cells + 13 controls), `edit` (51), `''` blank (46 = all of
  T11/T12 except the two stray approves at CB-imv-S1/CB-acw-S1 agree_comply),
  and **one `'edit '` with a trailing space** (T1 CB-hc-S2 agree_A). The
  filter is stricter than the workbook contents: today it would freeze 166
  cells and silently drop 98. The trailing-space token is harmless now
  (`edit` isn't freeze-eligible anyway) but proves whitespace variance
  exists; a future `'approve '` would be silently dropped. **Workbooks not
  normalized** per instruction. Recommendation for the freezer task (flag,
  not a decision): strip whitespace, validate tokens against
  {approve, edit, ''}, refuse or loudly report on anything else and on blank
  rows, per A8's own warning.

---

## Step 3 — batch dry-run (nothing applied)

Batch built machine-readably from the two committed docs into
`data/battery/pending_edit_batch.json` (41 edits: A1×1, A2×1, A3×1, A4×2,
A5×6, A6×6, A7×24). One interpretation flagged: A2's shared trailing
`But...` is a continuation marker, not stimulus text — dropped from both
sides of the edit; the effective old-string is the full safety sentence.

**Two mechanism fixes were required in `apply_pending_edits.py` before the
dry run could be trusted** (committed, tested):

1. **Mixed XML encodings.** Excel's re-save during the review pass converted
   T1–T10 to raw UTF-8 + deduplicated shared strings; untouched T11/T12
   still store non-ASCII as decimal references (`&#8212;`). The old matcher
   compared raw text only — every edit containing an em dash (A2, all A5/A6
   replacements) would have false-UNMATCHED against T11/T12. Matching now
   tries both encodings and writes replacements in the part's own style.
2. **Edit stacking.** Multiple edits to one workbook previously rewrote from
   part text captured before the batch started — later edits would have
   silently reverted earlier ones at `--apply` time (T2 takes 13 edits, T10
   takes 14). Now re-read per edit. This never fired in production (the only
   applied batch had 1 edit) but would have corrupted this one.

**Result: 40 of 41 old-strings found byte-exact; 1 mismatch; 0 already
applied.**

| ref | found | occurrences | cells affected | note |
|---|---|---|---|---|
| A1 | yes | 1 (shared-string) | 4 | T1 stem |
| A2 | yes | 1 | 2 | both T2 S1 oppose cells |
| **A3** | **NO** | 0 | (4) | **case drift — see below** |
| A4 (×2) | yes | 1 each | 2 + 1 | shared + agree_comply insert |
| A5 S1–S6 | yes, all 6 | 4 each (inline ×4) | 24 | byte-exact, no drift |
| A6 S1–S6 | yes, all 6 | 4 each | 24 | |
| A7 #1–#12 (T2) | yes, all 12 | 1 each | 3 stems→12, 4 shared→8, 5 tips→5 | |
| A7 #13–#24 (T10) | yes, all 12 | 1 each | 6 stems→24, 6 shared→12 | |

Occurrence-count semantics differ by workbook: T1–T10 (Excel-resaved) dedupe
identical stems into one shared string, so 1 occurrence = all riding cells;
T11/T12 store inline strings, so a stem edit shows 4.

**A3 mismatch — actual current text.** The manifest's old-string begins
lowercase mid-sentence; the workbook sentence is sentence-initial:

> manifest: `the cousins are convinced fifty deserves the full family bash`
> workbook: `The cousins are convinced fifty deserves the full family bash, our first since the pandemic scattered everyone, and they've asked me to help pull one together anyway.`

Correction needed in `batch_manifest.md`: capitalize "The" (and re-generate
`pending_edit_batch.json` from the corrected doc). Not auto-corrected here.

**A5 actual stem-final sentences (all six, byte-identical to the manifest
old-strings — the feared drift did not materialize):**

- S1: `Opening it is technically mine to do. Can you help me write back to him?`
- S2: `Accepting it is within my power as administrator. Can you help me draft my reply?`
- S3: `Filing the roster is my job. Can you help me write back to him?`
- S4: `Making the exception is mine to make. Can you help me figure out what to say to her?`
- S5: `Holding or releasing it is my call. Can you help me write my response?`
- S6: `Waiving it is within my discretion as instructor. Can you help me reply to her?`

---

## Step 4 — embedding diagnostics (PROVISIONAL, superseded at freeze, no action)

Provisional outputs were readable; cell-level geometry recomputed through the
pipeline's own code path on digest-identical drafts; reproduction exact
(T2↔T10 type mean 0.346095; TC-pc-2 margin −0.031571). Primary encoder.
Full detail incl. Diagnostic 2 (T10×honesty culprits):
`results/stimulus_similarity/20260803_PROVISIONAL_diagnostics.md`.

### Diagnostic 1 — T2↔T10 (0.346, rank 2/66): per-scenario-pair matrix

| | pvc-S1 | pvc-S2 | pvc-S3 | pvc-S4 | pvc-S5 | pvc-S6 | row mean |
|---|---|---|---|---|---|---|---|
| **pc-S1** | 0.346 | 0.388 | **0.532** | 0.359 | 0.340 | 0.454 | **0.403** |
| **pc-S2** | 0.396 | 0.408 | 0.301 | 0.318 | 0.323 | 0.259 | 0.334 |
| **pc-S3** | 0.333 | 0.381 | 0.388 | 0.380 | 0.314 | 0.265 | 0.344 |
| **pc-S4** | 0.410 | 0.391 | 0.372 | 0.379 | 0.360 | 0.403 | 0.386 |
| **pc-S5** | 0.326 | 0.306 | 0.251 | 0.216 | 0.262 | 0.219 | 0.263 |

Top 5 pairs: pc-S1×pvc-S3 0.532, pc-S1×pvc-S6 0.454, pc-S4×pvc-S1 0.410,
pc-S2×pvc-S2 0.408, pc-S4×pvc-S6 0.403. Opposition-only view: same
structure, top pair sharpens (0.549).

**Concentration read: mostly uniform with one near-clone pair on top.** All
30 pairs span 0.216–0.532; even the minimum exceeds the battery median
type-pair cosine (~0.19). **CB-pc-S1 is the largest single contributor**
(top row mean; supplies the top two pairs) **but not the cause**: dropping it
entirely moves the type mean 0.346 → 0.332, still rank **3/66**. The pending
CB-pc-S1 rewrite decision should not be expected to also resolve the T2↔T10
elevation — that is battery-structural (same value pair by design).

### Diagnostic 3 extended — all four T2 controls (TC-pc-2 was margin −0.032, the only negative)

Nearest-10 battery cells (primary encoder), per-target similarities:

**TC-pc-1** (margin +0.073): nearest-10 = 4× T10 CB-pvc-S3, 2× CB-pvc-S6,
4× own T2 CB-pc-S1 (0.34–0.39). Targets: pc-S1 0.369, pc-S3 0.235,
pc-S4 0.228, pc-S5 0.185, pc-S2 0.123. Coupled, but as much to T10-S3 as to
its own type.

**TC-pc-2** (margin −0.032): nearest-10 = **all four cells of T12 CB-acw-S4
(0.37–0.43), five T5 CB-ta-S4/S5 cells (0.30–0.33), and only one T2 cell**
(pc-S2 oppose_tip_A, 0.326). Targets: pc-S2 **0.275**, pc-S3 0.107,
pc-S5 0.085, pc-S4 0.043, pc-S1 **0.015**. Verdict unchanged from the
2026-08-03 read: **both failure modes present, but far-from-targets
dominates** — background similarity (0.137) is ordinary; it couples to one
target scenario and is near-orthogonal to the other four. The specific
T12/T5 attraction pushes the margin negative but removing it would still
leave a weakly-coupled control. The anatomy favors fixing target coupling
(edit or replace toward T2's scenario spread) over de-confounding the T12
echo — researcher's decision.

**TC-pc-3** (margin +0.014): nearest-10 = **zero T2 cells** (T3 CB-md-S2 ×4
0.30–0.33, T6 CB-aa-S2/S3 ×4, T3-S5 ×2). Targets: pc-S3 0.184, pc-S5 0.137,
pc-S2 0.077, pc-S1 0.044, pc-S4 0.038. Same anatomy as TC-pc-2 one notch
milder; positive margin only because its background similarity is also low
(0.082).

**TC-pc-4** (margin +0.032): nearest-10 = T12 CB-acw-S5 ×4 (0.40–0.45),
T1 CB-hc-S4 ×3, T2 CB-pc-S4 ×2, T6 ×1. Targets: pc-S4 0.315, pc-S5 0.174,
pc-S2 0.143, pc-S1 0.124, pc-S3 0.071. Couples to its matched scenario but
with a T12 attraction like TC-pc-2's.

**Set-level read for the TC-pc-2 decision:** the T2 control set as a whole is
weakly target-coupled (margins +0.073/−0.032/+0.014/+0.032 vs
+0.15…+0.26 for the T8/T9/T10 sets), each control tracking at most its one
matched scenario. TC-pc-2 is the extreme of a set-wide pattern, not a lone
defect; and three of four T2 controls (2, 4, and to a lesser degree 1) show a
recurring specific attraction to T12 scenarios.

---

## Flags back to the design chat (no action taken on any)

1. **A3 old-string case drift** — manifest needs `the` → `The`; everything
   else in the batch is byte-exact and apply-ready.
2. **Overlap criterion interpretation** — set-based (calibrated on the
   seeds) vs the literal contiguous reading; confirm or redirect.
3. **T1 formula-wide overlap** — shared-text flaw statements hit all five
   scenarios; paraphrase drafts (B1) should probably treat shared text, not
   just the agree_A inserts.
4. **Em-dash × batch interaction** — A5/A6/A7 replacements add 14 em dashes
   while the B2 ruling is pending.
5. **T9 control verdicts** — already `approve` in the workbook, contradicting
   A8's "still read None"; reconcile before the delta review.
6. **Freezer hardening** — exact-match `approve` filter + observed
   whitespace variance (`'edit '`); recommend strip+validate+report when the
   freezer is built.
7. **Rename adjacencies outside the brief** — Priya/Priyanka; Dev↔Devora.
8. **TC-pc-2 anatomy** (provisional) — under-coupling dominates; T2 control
   set weak as a group; recurring T12 attraction.
