# H04 review: pole-phase modulation with m > 3 in a multiphase SPB

Gap-critic, gap-loop iteration 1, step 4, 2026-11-02.
Inputs: `01_literature/novelty_H04.md`; `02_analytics/results/screen_H04.json` (T08, still finishing; read as of 2026-11-02 13:29); `02_analytics/assumptions.md#t08`; `03_simulation/validation.md` (flag 1, slot leakage).

## Verdict: **kill** (merge the surviving constraint set into H01 / H10). Weighted score **2.0 / 5**.

| Criterion | Score | Reason |
|---|---|---|
| Novelty (0.30) | 2 | The claim as written ("more pole/phase states -> better torque/A and part-load efficiency") is published experimentally for the IM (Libbos2020loss: -1/3 average loss, 2x torque/A at part load; Chaubal2024 / Maheshwari2025: continuous pole sharing, +11.5 % DC-bus use), and nine/fifteen-phase PPM is Keerthipati-group work; only a fixed-module-voltage m-sweep is unpublished, which is a parameter study, not a contribution. |
| Value (0.30) | 1 | The screen shows **no benefit from m > 3**: T_peak per converter kVA is 6.777 Nm/kVA for every m with the 8/4 pair (identical to 4 digits), and 85 km/h DC-to-wheel efficiency is 86.48 % (m=3, N=16) vs 86.40 % (m=5), 86.41 % (m=6), 86.22 % (m=7, N=12), 86.14 % (m=9, N=10); the 12/4 pairs that m=5/7/9 enable are worse (85.6-85.9 %, 6.337 Nm/kVA). |
| Feasibility (0.20) | 3 | Physically buildable (m legs per module, isolated neutral, the H01 closed-form rule says which modes exist), but more legs per module at fixed kVA means lower per-leg current and more gate drivers / isolated supplies per module, a cost the screen does not count. |
| Enes fit (0.10) | 3 | Uses the SPB module and Enes's GaN loss model, but m = 5-9 per module is a new module design, not the existing 3-leg SPB hardware. |
| Paper fit (0.10) | 2 | A null result ("m > 3 does not help at fixed kVA") is a section in an H01 paper, not a paper of its own. |

Weighted: 0.3 x 2 + 0.3 x 1 + 0.2 x 3 + 0.1 x 3 + 0.1 x 2 = **2.0**. Two criteria below 3; far from the 4.0 promote bar.

## Strongest kill argument (the reviewer comment)
> "The authors claim that a higher phase number gives more pole/phase states and therefore better torque per ampere and part-load efficiency. Their own sweep shows torque per kVA identical across m = 3...9 and cruise efficiency spread of 0.34 percentage points, with m = 3 the best. The extra states the higher m provides (7-8 states vs 6 for m = 3, N = 16) are never visited at the operating points that matter. The underlying idea, selecting the pole count by operating point, is Libbos et al. (TTE 2020), and it already works with m = 3."

Supporting points:
1. **The benefit is smaller than the model error.** The 0.08 pt cruise difference between m = 3 and m = 5/6 at N = 16 is below the slot-leakage sensitivity of the same metric in the same model (`slot_leakage_2x_sensitivity`: cruise eta shifts -0.04 % for m=3 and -0.08 to -0.15 % for m=5), and the simulator puts the real slot leakage at 2.0-2.3x the analyst's (validation.md flag 1). The sign of the m-ranking is not resolved, and the magnitude is noise either way. P at 90 km/h for m=5 is flagged sensitive (-6 to -13 %).
2. **The screen is iso-kVA by construction, which is the fair baseline, and it is exactly why m drops out.** With turns rescaled to equal EMF per volt and the same total VA, torque per kVA depends only on flux caps and winding factor; m = 3 at N = 16 already has k_w 0.966/0.793 with k_d = 1 (H01 rule), so m has nothing left to improve at the fundamental.
3. **Not iso-N.** m = 7 and m = 9 were evaluated at N = 12 and N = 10 (the only (N, Q) combinations that fit), so their lower efficiency mixes m with the module voltage class (EPC2361 vs EPC2304-class devices). The comparison that is iso-N (m = 3, 5, 6 at N = 16) shows no gain either.
4. **What higher m usually buys was not screened and is published anyway:** harmonic current injection for torque density (x-y planes are not blocked by an isolated neutral in m >= 5) and fault tolerance (H08 territory, Wu2024open). Neither rescues the claim as written.

## What would save it
Nothing that keeps H04 as a separate hypothesis. The only SPB-specific content is the **admissible mode set under isolated neutrals and a series DC stack**: conditions (i)-(iii) in assumptions.md#t08 and the closed-form rule (mode p available with k_d = 1 iff c | p and m does not divide p/c; constant module power additionally needs m not dividing 2p/c; 1221/1221 enumerated cases agree). That rule belongs to **H01** (zero-extra-hardware design rules), and condition (iii) (no 2nd-harmonic power pulsation per module) belongs to **H10** (series-stack power balance). If the leader wants one more test before closing: run the iso-N (N = 16) m = 3/5/6 cruise and 50 km/h/3 % part-load points on the simulator's slot leakage after R01; a < 0.3 pt spread confirms the kill.

## Spin-off ideas
1. **Merge, not spin-off:** fold the m-generalised closed-form mode rule (incl. the m | 2p/c constant-power condition) into H01 as its "phase number" section, and hand condition (iii) to H10 as one of its admissible-mode tests.
2. (Low priority) **x-y harmonic injection in an isolated-neutral multiphase module:** whether m >= 5 modules can use the non-torque planes for something SPB needs (e.g. rotor excitation for H03, or cell power balancing for H10) rather than for torque. Only worth a line in H03/H10, not a hypothesis on its own.
