# The gap loop

Goal: converge on one research gap that (1) nobody has filled, (2) SPB + pole changing fills
with a quantified benefit for a 40 t truck on VECTO cycles, (3) Enes can build on his own assets
(SPB GaN hardware, P1–P5 excitation work, loss models), and (4) fits one strong IEEE paper.

## One iteration (leader runs it; ~one round of agent work)

| Step | Who | Input | Output |
|---|---|---|---|
| 1. Propose | leader (+ any agent's "new idea" line) | register, last reviews | new/refined hypotheses in `hypotheses.md`, each with a falsifiable claim and one screening metric |
| 2. Novelty check | lit-scout | top hypotheses | per hypothesis: closest 3 papers, what they did / did not do, novelty verdict (new / partly done / done) in `01_literature/novelty_H<id>.md` |
| 3. Value screen | analyst (simulator where dynamics matter) | claim + metric | number for the metric vs the right baseline, in `02_analytics/results/screen_H<id>.json` |
| 4. Attack | gap-critic | 2 + 3 | `06_reviews/H<id>_review.md`: scores + the strongest argument that kills it + what would save it |
| 5. Decide | leader | 2–4 | status per hypothesis: **promote / refine / merge / kill**; log line; short report to Enes |

Parallelism: step 2 and 3 run together; step 4 waits for both. A killed hypothesis stays in the
register with its reason (negative results are evidence too).

## Scores (gap-critic assigns, 1–5; leader can override with a reason)

| Criterion | 5 means | Weight |
|---|---|---|
| Novelty | no paper does this combination; closest work clearly differs | 0.30 |
| Value | quantified benefit vs the *fair* baseline (fixed-pole, same kVA/volume, best gearing), large enough to survive model error | 0.30 |
| Feasibility | physics and hardware hold; transition, saturation, excitation, device limits checked | 0.20 |
| Enes fit | uses SPB GaN hardware / P1–P5 / loss models; buildable at KTH | 0.10 |
| Paper fit | one clear story for a target venue (TIE, TPEL, TTE, TIA, ECCE) | 0.10 |

**Promote** when weighted score >= 4.0 and no criterion < 3. Stop the loop when one hypothesis is
promoted and confirmed by a second, independent check (simulator or a second model), then hand it
to writer for a paper outline.

## Lessons already learned (iteration 0, T02–T03d)
- Fair baselines matter: against fixed-pole IMs with free gearing, pole changing does not widen
  the envelope; it trades gear stages and inverter kVA (T03b).
- Cruise efficiency is not where pole changing wins at 300 kW (T03d); gear stages dominate.
- Pure WRSM gains nothing from pole changing (T03, confirmed by Enes's OPT FEA, P5).
- All verified on-road e-trucks use PMSM; IM is mining/rail only (T02c).
