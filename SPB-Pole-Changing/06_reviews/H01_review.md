# H01 review: zero-extra-hardware pole changing, design rules for (N, m, Q, p1/p2)

Gap-critic, gap-loop iteration 1, step 4, 2026-11-02.
Inputs: `01_literature/novelty_H01.md`; `01_literature/gap_matrix.md` (stack / isolated-neutral / shared-bus columns and the 2026-11-02 coverage note); `02_analytics/results/screen_H01.json` (rule, rule_check, best_designs, best_ratio3_designs); `02_analytics/results/sensitivity_slot_leakage_2x.json`; `02_analytics/assumptions.md#t08`; `03_simulation/validation.md` (flag 1); own quick search (see the novelty check below).

## Verdict: **merge with H10** (one paper-level gap; see the end). H01 standalone weighted score **2.9 / 5**.

| Criterion | Score | Reason |
|---|---|---|
| Novelty (0.30) | 2 | The rule (mode p available with k_d = 1 iff c \| p and m does not divide p/c) is the star-of-slots symmetry condition written for legs instead of phases; PPM feasibility for arbitrary input counts is Magill2015 / Olson2024, and slot count versus (m, p) as a design variable is Reddy2020 (TIE). What is new is only the filter that the inputs are grouped into N isolated-neutral modules on a series stack, and the stacked-multiphase-with-isolated-neutrals topology itself is published without pole changing (Che2014, Verkroost2024; not in our refs, see below). |
| Value (0.30) | 2 | The rule tells which pole pairs exist, but it carries no benefit versus a fair baseline by itself: "zero extra hardware" is also true of every independently fed coil drive (WICSC, ISCAD, Libbos 18-leg), and the benefit of the modes it unlocks is what H02 must show, which is weak (see H02 review). The one sharp design outcome, that 3:1 pairs (12/4, 6/2) with k_w = 1.0/1.0 need m = 5, 7 or 9 per module while m = 3 gives only 2:1 pairs at k_w 0.966/0.793, has no shown system value (H04 review: m > 3 gives no gain in torque/kVA or cruise). |
| Feasibility (0.20) | 5 | Exact algebra, checked 1221/1221 against the enumeration, leakage-insensitive (it is a winding result; leakage only shifts the voltage-limited consequences by 6-13 %). |
| Enes fit (0.10) | 4 | N = 16, m = 3, Q = 48 is the SPB reference and works for 8/4, 4/2, 16/8 with no change; the 3:1 designs need m >= 5 legs per module, which is a new module, not the existing hardware. |
| Paper fit (0.10) | 3 | A design-rule table is a good section or a TIE/TEC letter; on its own it reads as a tutorial unless it is tied to a constraint the PPM literature does not have (the series stack, i.e. H10). |

Weighted: 0.3 x 2 + 0.3 x 2 + 0.2 x 5 + 0.1 x 4 + 0.1 x 3 = **2.9**. Two criteria below 3; not promotable alone.

## Novelty check (own quick search, 2026-11-02)
lit-scout's gap matrix says no source combines a series stack, isolated neutrals and pole changing. That holds for pole changing, but the matrix misses the stacked-multiphase literature that a reviewer will cite first:
- **Che, Levi, Jones, Duran, Hew, Rahim, "Operation of a six-phase induction machine using series-connected machine-side converters", IEEE TIE 61(1), 2014, doi 10.1109/TIE.2013.2248338**: two 3-phase converters on a cascaded DC link, each feeding an isolated-neutral winding set; mid-point balancing through the extra multiphase degrees of freedom.
- **Verkroost, Vande Ghinste, ..., Sergeant, Vansompel, IET Power Electronics 2024**: "stacked polyphase bridges" converter on a 4 kW modular axial-flux PMSM; consensus-based DC voltage balancing per module.
- **Verkroost et al., IET Electric Power Applications 2023** ("Dynamic multi-agent dc-bus reconfiguration in modular motor drives with a stacked polyphase bridge converter"): isolate/reactivate one inverter of the stack online, two extra switches per inverter, 100 ms, no torque interruption.
- A nine-phase machine with three isolated neutrals fed by three cascaded 3-phase VSIs to reach a high DC-link voltage (IEEE ISIE 2017, found by abstract only; lit-scout to confirm the key).
None of these changes poles or phases, so the combined gap is still open, but the "SPB topology" part is not ours to claim, and **Ghent (Sergeant/Vansompel) uses the name "stacked polyphase bridges"**. lit-scout should add these four to `refs.bib` and the gap matrix before any novelty score of 4+ is given to H01 or H10.

## Strongest kill argument (the reviewer comment)
> "The 'design rules' are the classical winding-symmetry conditions (coils of one phase in phase for the target pole number, phase phasors forming a balanced set) applied to a drive where every coil group already has its own inverter. That such a drive changes poles with no added hardware is known since Osama and Lipo (1997) and is the premise of WICSC and of Libbos et al.; the paper's own enumeration confirms the closed form, which is to be expected. The only new constraint, constant module power for the series DC link, is automatically met for odd phase numbers, so for the authors' 3-phase modules it adds nothing."

Supporting points:
1. **The constant-power condition is empty for odd m.** With spaced/interleaved wiring the module leg phasors are exp(j 2 pi (p/c) t / m), t = 0..m-1; they sum to zero iff m does not divide p/c, and their squares sum to zero iff m does not divide 2p/c. For odd m the first implies the second. Condition (iii) only bites for even m (e.g. m = 6, p/c = 3). So in steady state every admissible mode of the m = 3 SPB already has constant module power, and the "H10 overlap" inside H01 is one line for m = 6. The real H10 content is elsewhere: transitions (k-sweep), unequal coil loading, turns changes (H09), harmonic excitation (H03) and cell bypass (H05/H08).
2. **Only one wiring family is proved.** The closed form covers spaced wiring with interleaved modules (k_d = 1). Contiguous and matched-triple wirings add modes with k_d < 1 that the rule does not describe; a design-rule paper must either cover them or show they are never better.
3. **The k_w = 1.0/1.0 3:1 designs are concentrated (q = 1 per leg) and pay in MMF harmonics**: N = 2, m = 9, Q = 36, 12/4 has sigma_diff 9.2 % in the 12-pole mode, against 0.6 % for the 4/2 m = 9 design. Winding factor alone overstates them; the differential leakage feeds straight into the leakage dispute (R01).
4. **"Zero extra hardware" is not quite true at the system level**: the 2:1 pair costs the low-pole mode its pitch factor (k_w 0.793), which is the root of the yoke-capped, +1.3 kW cruise penalty in H02. The hardware is saved by paying in copper and iron.

## What would save it
Make the rule the front half of a constraint paper, not a standalone claim: **the admissible pole/phase mode set of a series-stacked, isolated-neutral drive, steady state AND transition**. That means extending H01 with (a) the post-bypass case (N -> N - 1 modules: with N = 16, m = 3, Q = 48, c = Q/(mN) is no longer an integer for N = 15, so the rule says which modes survive a bypassed cell; this is new and directly useful for H08), and (b) the H10 transition power-balance limits. Then the novelty is the stack, which nobody in PPM has, and the value is a design tool that also answers "what can the SPB still do after a fault".

## Spin-off ideas
1. **Merge H01 + H10 (+ the post-bypass part of H08) into one gap: "Pole/phase-mode admissibility and DC power balance in series-stacked isolated-neutral drives."** Steady-state rule (H01), transition and unequal-loading balance limits plus balancing headroom (H10, using the multiphase degrees of freedom as Che2014 does for a fixed pole), and the mode set after one cell bypass (H08). Estimated merged scores, to be confirmed after the H10 screen and the novelty additions above: N 4, V 3, F 4, E 4, P 4 -> **3.7**; it reaches 4.0 only if the H10 screen shows a real constraint (e.g. a k-sweep transition that drives a cell capacitor out of its band within the transition time) that a design-rule table then removes.
2. **Fault-reconfiguration table**: for each (N, m, Q), which pole modes remain feasible with one or two modules bypassed (Verkroost2023-style bypass), with k_w and torque derating. Cheap to compute from the existing enumeration; a natural Section V of the merged paper.

## Note on the merge
The merge is right at paper level, but sell it correctly: the steady-state rule is the enabling result, not the novelty. If H10 screens to "the series stack never limits any practical mode or transition", the merged gap falls back to roughly H01's 2.9 and should be parked as a design note in the main SPB paper.
