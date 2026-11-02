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

## Iteration 1 result (2026-11-02)
| H | Score | Decision |
|---|---|---|
| H01 | 2.9 | merged into H11 |
| H02 | 2.5 | refine -> H02r (electronic gearbox vs 2-speed, needs T07 cycle) |
| H03 | 2.9 | refine -> H03s (SPB self-excitation of fixed-pole WRSM/HESM) |
| H04 | 2.0 | killed (rule -> H01/H11) |
| H05 | 1.7 | killed (cell bypass already published, Verkroost 2024) |
| H06 | 2.0 | killed as stated (done for IM by UIUC/KTH) |
| H07 | 2.4 | killed (yoke-capped 4-pole flux) |
| H08 | – | folded into H11 (post-bypass table) |
| H09 | – | open (per-mode turns change; open-end feeding admissible per H10) |
| H10 | – | screened, merged into H11 |
| H11 | 2.8 | **refine — front-runner** |

What iteration 1 established: pole changing pays only for the IM, and mainly as inverter sizing / single-ratio gearing, not
cruise efficiency. The SPB-specific novelty concentrates in the series stack: cell power pulsation under multi-order
operation (H11), which makes the phase number a design variable. Critic's framing: a design law with two positive
designs (m = 3 + pulsation-constrained schedule / bulk C vs m = 5 with overlap and exciterless excitation), cost
crossover, and a cheap Rev B cell experiment. Target TPEL Letter or ECCE 2027 -> TIE.

## Iteration 2 plan
- simulator: confirm_H10 with the nonlinear MEC + DC cells (m = 3 and m = 5, flat and 2 % grade): true crossfade
  envelope, saturation residual for m = 5, V8·I4 term in the sequential handover.
- analyst: cost table m = 3 + bulk C vs m = 5 (IM transient, continuous H03s excitation, post-bypass N−1);
  H11s pulsation-constrained m = 3 handover (≤ ±10 % at 2.9 mF, gap ≤ 0.2 s, no torque reversal); post-bypass mode table.
- lit-scout: full-text check of Zoric2018arbitrary, Subotic2019active, Sau2019modular for the law; AMT shift-interruption
  numbers for trucks; Verkroost2024PowerDistribution vs module interleaving under eccentricity.
- then gap-critic re-scores H11 (and H11s, H02r, H03s if evidence exists).

