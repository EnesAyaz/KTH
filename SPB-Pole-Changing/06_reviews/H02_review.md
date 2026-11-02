# H02 review: pole changing cuts inverter kVA, so a co-designed SPB needs fewer cells and wins on system cost and loss

Gap-critic, gap-loop iteration 1, step 4, 2026-11-02.
Inputs: `01_literature/novelty_H02.md`; `01_literature/gap_matrix.md` (stack / isolated-neutral / shared-bus columns); `02_analytics/results/screen_H02.json` (N16_m3_Q48_8/4 and its two fixed-pole baselines, all designs); `02_analytics/results/sensitivity_slot_leakage_2x.json`; `02_analytics/assumptions.md#t08`; `03_simulation/validation.md` (flag 1 slot leakage; flux-cap difference at the flux-limited points).

## Verdict: **refine** (reframe; kill as stated). Weighted score **2.5 / 5**.

| Criterion | Score | Reason |
|---|---|---|
| Novelty (0.30) | 2 | The inverter-sizing argument is published: Libbos2022inverter (TPEL) shows a fixed-pole 3-leg drive needs 1.5x oversizing and the variable-pole GaN drive has 50 % lower loss and up to 45 % lower part-load loss; Raj2022 gives 37 vs 56 kW (ratio 1.51, ours 1.74). Truck scale and module count as a variable are a re-run, not a new idea. |
| Value (0.30) | 2 | Against the fair baseline (fixed-pole IM at its own best gear, G = 17.3) the device count is **identical (672 vs 672)** and start loss identical (1557 W); the only win is -1.27 kW at 85 km/h, carried by the gear and windage models. Against the same-gear baseline the device win (-42 %) is paid by +1.34 kW at 85 km/h cruise. |
| Feasibility (0.20) | 3 | Physics is sound and current-limited start torque is leakage-insensitive, but the cruise penalty and the start torque both sit on the unreconciled flux cap (validation.md: simulator cap 0.038 vs 0.0439 Wb in 2p=4, flux-limited points 14-19 % low), device area is not computed, and gate-charge scaling for non-EPC2361 classes is assumed. |
| Enes fit (0.10) | 4 | N = 16, m = 3, EPC2361, Enes's loss model: this is his hardware and his model. |
| Paper fit (0.10) | 3 | A truck system-level co-design paper (TTE) is plausible, but only with the reframing below; as stated it is Libbos2022 at a larger rating. |

Weighted: 0.3 x 2 + 0.3 x 2 + 0.2 x 3 + 0.1 x 4 + 0.1 x 3 = **2.5**.

## The numbers the reviewer will look at (N = 16, m = 3, Q = 48, 8/4, EU2017 gear, 85 km/h flat, P_wheel 152 kW)

| Loss (W) | PC IM, G 9.8, 672 dev | Fixed 2p4, G 9.8, 1152 dev (kVA x1.74) | Fixed 2p4, G 17.3, 672 dev (free gear) |
|---|---|---|---|
| machine EM | 4600 | 3201 | 2848 |
| friction + windage | 941 | 857 | 1956 |
| gear | 17433 | 17433 | 19435 |
| inverter | 769 | 910 | 772 |
| **system** | **23743** | **22401 (PC +1342)** | **25011 (PC -1268)** |
| start inverter loss | 1557 | 2717 | 1557 |

At 60 km/h (PC in 2p8): PC 14676 W, same-gear fixed 14856 W (PC -180), free-gear fixed 16149 W (PC -1472).

## Strongest kill argument (the reviewer comment)
> "The claimed 42 % device reduction exists only against a fixed-pole machine forced onto the pole-changing machine's gear ratio, a design nobody would build. A fixed-pole IM at its own optimal gear needs exactly the same 672 devices and the same start loss. The remaining cruise advantage (1.3 kW of 25 kW) comes from a regulatory default gear-loss model and a windage term, not from the drive; with the same-gear baseline the pole-changing machine is 1.3 kW worse at cruise because its 4-pole mode is yoke-limited. The lower start loss is irrelevant: junction temperature is 50.5 C in both designs. Libbos et al. (TPEL 2022) have already reported the inverter-sizing benefit."

Supporting points:
1. **Pick-your-baseline problem.** The benefit flips sign depending on which fixed-pole design is used: devices (-42 % vs 0 %) and cruise loss (+1.34 kW vs -1.27 kW) are never both favourable against one baseline. A fair reviewer accepts only the free-gear baseline for devices and the same-gear baseline for the machine, and then PC wins neither.
2. **The free-gear cruise win is a gear-model result.** The 2.0 kW gear difference is the EU 2017/2400 regulatory baseline (axle drag T_d0 = 70 + 20 i), which is deliberately pessimistic: the PC design loses 17.4 kW in EU2017 but 11.6 kW in certified_like. The certified_like free-gear fixed baseline is not reported, so the 1.27 kW win may shrink to well below 1 kW. The windage half (-1.0 kW at 7512 vs 4250 rpm) depends on the gap-windage coefficients that were just corrected by 2x in T03d. Both carriers of the benefit are the least validated parts of the chain.
3. **Start loss has no value as reported.** start_Tj is 50.4-50.5 C in every design, so the inverter is nowhere near a thermal limit at start; the -1.2 kW buys no cooling, no device, nothing measurable over a cycle (start lasts seconds).
4. **The cruise penalty is larger than the model error on the side that hurts.** The +1.4 kW machine loss comes from the yoke-capped 4-pole flux with k_w 0.793. The simulator's flux cap in 2p=4 is 13 % lower than the analyst's (0.038 vs 0.0439 Wb), which would raise the 4-pole current and copper loss further; the slot-leakage sensitivity (< 0.15 pt cruise eta) does not cover this. The same flux-cap difference makes 2p=8 start torque 14-19 % lower in the simulator, which would eat into the 1.74 kVA ratio (Raj2022 already gives only 1.51).
5. **Cost does not save it at long haul (order of magnitude, assumptions to be checked).** 480 fewer EPC2361 plus their share of drivers is a one-off saving of the order of a few k EUR. The +1.34 kW at 85 km/h, at ~1100 h/yr of cruise for a long-haul tractor and ~0.25 EUR/kWh, is ~1.5 MWh and ~0.4 k EUR per year, i.e. the device saving is eaten within the vehicle life, before counting the larger battery. The trade does not favour PC on the primary cycle (VECTO Long Haul).
6. **The baseline set is incomplete.** All verified on-road e-trucks use a PMSM (T02c), most with a 2-4 speed gearbox. A TTE reviewer will ask for a PMSM + 2-speed baseline; neither IM baseline answers that.

## Would a fair reviewer accept it as a benefit?
Not as "fewer devices and lower loss". They would accept a **trade** stated honestly: *for a single-reduction e-axle (no shiftable gearbox), electronic pole changing replaces a 1.5-1.7x inverter oversizing or a second gear stage, at a cruise cost of about 0.9 % of wheel power.* That is defensible only where start/grade duty, not cruise, dominates the energy or the sizing.

## What would save it
One analysis: **cycle energy and component cost on VECTO Regional Delivery (and Urban as sensitivity), against three baselines** — fixed IM at free gear, fixed IM + 2-speed gearbox, and PMSM + 2-speed — with (a) the yoke re-dimensioned for the 4-pole mode (co-designed machine, not the 8-pole T03 stator), (b) the certified_like gear model reported next to EU2017, and (c) the flux cap from R01. The claim survives if PC removes the second gear stage (cost, mass, shift-torque interruption) with < 0.5 % cycle energy penalty, or wins outright on Regional Delivery where low-speed grade work is a larger share. Also compute device area (package data request in the screen) so "volume" is a number, not a word.

## Spin-off ideas
1. **"Electronic gearbox" for single-reduction e-axles**: pole changing as the replacement of the 2-speed gearbox in a truck e-axle (no shift interruption, no clutch, no synchroniser), judged on Regional Delivery cycle energy and gearbox cost/mass. This is the reframing above as its own hypothesis; it competes with ISCAD's "virtual gearbox" claim (Runde2019iscad), so it must beat a real 2-speed AMT model.
2. **Grade-start sizing with SPB device shedding**: size the SPB for the 12 % start in 8-pole and shed parallel devices at cruise (H05 screen: -4 % at 85 km/h, -16 to -19 % at 60 km/h inverter loss). Small, but it recovers part of the oversizing penalty in either machine; a section, not a paper.
