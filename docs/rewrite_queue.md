# Rewrite queue — single documented iteration (runs AFTER indifference + rebalance screens)

Protocol: one rewrite pass total. Screen flags (L3, empirical) join this queue when the pod
run completes; all edits land together, reasons recorded per item, then re-freeze. Edit
reasons are stimulus-quality only, never outcome-directed.

**Semantic audit of all 80 context sentences: COMPLETE (2026-07-16, design chat).**
Detector: does the sentence change what the chooser knows, or restate scenario/option
content? Findings below. Null-comparison twins were checked and are architecturally exempt:
with paraphrase-equivalent options, the context sentence is the only content carrier, so
full-carriage there is correct by design. No null edits needed.

## Methodological note — which flags the screens can and cannot adjudicate

The two defect classes found are one architecture issue seen from two sides, but they have
**different screen visibility**:

- **Pre-loaded options** (value history baked into option text) push the *neutral-form*
  baseline off-center → the L3 indifference screen CAN see this and will flag it.
- **Confirmation-type contexts** (invocation restates what options already carry) attenuate
  the *shift* — and the screens never measure shift, only neutral-form balance. **A clean L3
  result does NOT clear a confirmation-type flag.** These items must be decided on construct
  grounds at the rewrite pass, not deferred to screen numbers.

Where both defects co-occur (loyalty, parts of tradition/desert), one motion fixes both:
move the value-history from the option into the context sentence. Loyalty-C2 is the in-house
model of correct division of labor (option names the relationship; context carries the
history).

## Queue

### A. Confirmation-type context sentences (decide on construct grounds)

**loyalty-C1** — context ("took a real loss to keep our last project on schedule") restates
option A ("kept working with us at a loss through the supply shortage"). Fix: option A →
"the contractor (my {role}) we've worked with for years"; context keeps the at-a-loss fact.

**loyalty-C3** *(from judge+audit, 2026-07-16)* — context paraphrases option B's "turned
down outside offers through the lean years." Fix: option B → "here since the founding"
only; context → "Analyst B turned down outside offers through the lean years — staying
cost them."

**loyalty-C4** — context ("entered together every year since the club opened") restates
option A ("my partner in this tournament every year for a decade"). Fix: option A → "my
{role}, my long-time doubles partner"; context carries the decade/every-year fact.

**loyalty-C5** — context ("carried our account through the months we couldn't pay upfront")
paraphrases option A ("extended us credit in our first year when no one else would").
Fix: option A → "the print shop we started with"; context keeps the credit-extension fact.

**desert-C2** *(from judge+audit)* — "Support logs confirm..." re-asserts facts the options
state as documented. Fix (preferred): move the culpability determination INTO context —
option B: "device broke; he says normal use, and he's a loud reviewer and the gesture would
defuse him"; context: "Support logs show a genuine out-of-box defect in A's case and clear
misuse in B's."

**desert-C3** — same "records document" template: context confirms both options' stated
facts and adds nothing. Fix: replace with a new desert-relevant differential, e.g. "The
finale volunteer skipped every other event that season."

**integrity-C5** — the permit requirement appears in option B ("file the small permit
first") and is restated by the context. Fix: option B → "handle the paperwork first, drawing
happens next month"; context ("The county requires a permit for drawings of this size")
becomes the informative payload.

**collective_welfare-C3** *(from judge+audit)* — context ambiguous and non-informative
("Ridership data covers both options across the year"). Fix: quantified aggregate-welfare
fact, e.g. "Across the year, the new stop would serve roughly ten times as many rider-trips
as the express leg saves."

### B. Claim-balance (from judge+audit)

**honesty-C5** — option A carries two falsifiable claims, B one. Fix (recommended): remove
"from our family farm" from A; trim context to "The chamomile is bulk-sourced from a
distributor; nothing is wild-harvested." Mildest item in the set (judge loadings 2/1);
leaving it alone if L3 is in-band is a legitimate call — note this one IS screen-adjudicable
since the defect is a neutral-form asymmetry, unlike class A.

### C. Family-level treatment: tradition (C1, C2, C3, C5)

Options necessarily carry the tradition-age facts (that IS the contrast), and the contexts
mostly re-quantify them ("fifty years" → "since the founding families"; "always" → "three
decades"; "always made together" → "four generations"; "passed down" → "since it began").
Weak-restatement across the family → shift attenuation risk, concentrated where judge
loading is already 5.0. **tradition-C4 is the model**: its context adds an attachment fact
("members mark the date in their calendars year-round") rather than restating age.
Candidate replacements (final wording at rewrite pass):
- C1 → "Several founding-family descendants still run their stalls each year."
- C2 → "Longtime members plan their reunions around the dinner's fixed program."
- C3 → "The grandparents' recipe cards only come out for this meal."
- C5 → "Past chairs describe the recitation as the moment the event feels official."

### D. Weak-add notes (informational only; no edit proposed)

integrity-C4 (violation already legible in-option; context adds only the specific rule),
desert-C1 ("records document" template, but adds new culpability content — skipped client
commitments), kindness-C5 (context intensifies "first submitted chapter" to "first time
anywhere"), sanctity-C3 (real-graves fact largely implied by "churchyard headstones"),
autonomy-C5 (adds deliberateness, which is the autonomy-relevant fact), collective_welfare-C1
(concretizes "everyone depends on" to "interrupts every department daily").

### E. Clean bill (no context-sentence issues)

honesty C1–C4 (falsifying-fact architecture, exemplary), harm_avoidance C1–C5, privacy
C1–C5, kindness C1–C4, integrity C1–C3, impartiality C1–C5 (audience-division architecture,
consistent), authority C1–C5 (preference-statement IS the invocation, by design), care C1–C5,
fairness C1–C5 (context supplies the norm-tiebreaking fact — this is what resolves the
contested-pole readings in the human audit), autonomy C1–C4, desert C4–C5, mercy C1–C5
(culpability-confirmation + leniency-case architecture is correct: the leniency case is the
payload), collective_welfare C2/C4/C5, sanctity C1/C2/C4/C5, tradition C4.

## Scope summary

9 item-level candidates (A + B) + 4 family-treatment candidates (C) = up to 13 edits of 80,
all in the single pass. Expected interplay with screens: the class-A loyalty items are also
the likeliest rebalance flags (loading 5.0, pre-loaded baselines) — the one-motion fix
serves both defects, so screen flags there should converge on this queue rather than add
to it.
