# novelty_H11.md  H11 (merged H01+H10+H08): admissible pole/phase modes and DC power balance in series-stacked isolated-neutral drives, including after bypassing cells
Gap-loop, lit-scout, 2026-11-02. Keys in refs.bib; notes in papers/.

## Verdict
**Partly done for the ingredients, not found for the combination.** Online bypass of a module in an SPB is published (Verkroost2024Reconfiguration), multiphase post-bypass operation with extra degrees of freedom is published for cascaded H-bridge drives (CascadedHBridgefault), and fault survival of an SPB exists (Nikouie2016operation). I did not find any paper that gives the admissible set of pole/phase modes (or the torque derating) of a stacked isolated-neutral drive after one or two cells are bypassed, or that links that set to DC-power balance per mode. The claim must be narrowed to the mode table and its power-balance condition, not to bypass itself.

## 1. Closest papers
1. **Verkroost2024Reconfiguration** (IET EPA, online 2023, Ghent): online isolate/reactivate one inverter in the SPB series string in motoring, two extra switches per inverter, 100 ms, no torque interruption, extended fault tolerance and speed range, 4 kW modular axial-flux PMSM. Did not (per abstract): say which pole/phase modes survive. Abstract only; the Wiley PDF returned HTTP 403.
2. **CascadedHBridgefault** (TPEL 2025): bypass damaged H-bridges in an n-phase CHB drive and use xy degrees of freedom to keep the speed range without field weakening or torque ripple; five-phase experiment. Did: post-bypass admissible operating region of a multiphase cascaded drive. Did not: pole changing; cells have separate sources, not a series stack.
3. **Nikouie2016operation** (IECON 2016, KTH): SPB survives a transistor short circuit; stability under fault. Not a mode set.
4. **Gjerde2014SeriesFault** (TIA 2014): modular series-connected converter with fault-tolerant modes and limits of fault tolerance (100 kV wind generator).
5. **Cengelci2000MMMI**: winding groups on separate inverters continue at reduced power after inverter faults.
6. **Zoric2017voltage, Verkroost2024PowerDistribution, Che2014SeriesConnected**: DC split and power sharing at a fixed mode (see novelty_H10.md).
7. **Wu2024open / Wu2023openphase** (KTH): open-phase pole transition on a common DC bus; not a series stack.

## 2. Question-by-question
- **Cell power balance under a change of pole or phase mode, or unequal coil-group loading?** Unequal loading yes (fixed mode); mode change no (see novelty_H10.md).
- **Admissible mode set after bypassing a cell?** Cascaded H-bridge multiphase: the post-bypass speed/torque region is treated (CascadedHBridgefault). SPB: bypass mechanism and DC reconfiguration are treated (Verkroost2024Reconfiguration). A pole/phase mode table after bypass is not found. Caveat: the Ghent IET paper was read at abstract level only.

## 3. What a reviewer would cite against H11
Verkroost2024Reconfiguration ("bypass in an SPB is published, with fault tolerance and speed range"), CascadedHBridgefault ("post-bypass strategy using multiphase degrees of freedom"), Zoric2017voltage and Verkroost2024PowerDistribution ("power balance across winding sets"). The residual novelty is the combination with electronic pole/phase mode selection, the exact mode rule (c, m, p) and the capacitor-drift/balancing headroom per mode.

## 4. New refs
All merged on 2026-11-02 (refs.bib block "imported from Review-Paper-SPB/ref.bib" plus Nikouie2016operation, Zoric2018arbitrary, Subotic2019active).


## Pulsation law (added 2026-11-02 after the H10 screen sharpened H11)
Law as stated: in a series-stacked isolated-neutral drive with m-phase cells, two simultaneous spatial orders a and b (pole-change overlap, field sweep, harmonic excitation, rotor harmonics) make each cell's power pulsate at f_a +- f_b with amplitude m V I when m divides (a +- b)/c; prime m = 5 or 7 removes the pulsation.

**Verdict: the law itself was not found in the literature checked; every ingredient is standard. Treat as new but narrow, abstract-level for the IEEE papers.**

1. **Levi group (series-connected multiphase multi-machine, Zoric).** Levi2006series (and the Jones/Duran/Vukosavic series-connected two-motor six-phase / five-phase / nine-phase papers in the search) put two machines with different frequencies and orders on one inverter by phase transposition. They exploit the orthogonality of the planes for independent control, with one common DC link; no per-cell power in a series stack, no pulsation rule. Zoric2017voltage (three isolated neutrals, cascaded VSIs) shows imbalance gives unequal average power sharing and unequal DC voltages, and Zoric2018arbitrary / Subotic2019active move average power between sets with x-y currents at the fundamental frequency (same frequency, so a DC cross term). That is the equal-frequency special case of the law (consistent with the sequence rule: cross power exists for a given phase sequence, none for the opposite). They do not derive pulsation from two different simultaneous orders, and they do not select the phase number to cancel it. Che2014SeriesConnected uses x-y degrees of freedom for mid-point balance at a fixed mode.
2. **Cascaded / modular multilevel motor drives.** Module power pulsation is standard there: Sau2019modular and the MMC-drive literature (low-speed capacitor ripple, circulating-current or common-mode injection, DC-bus reduction at low speed) and CHB drive work. Precisely how ours differs: (i) in an MMC/CHB the pulsation is a product of one arm/cell current and one voltage at the same fundamental (single order, frequency f or 2f, set by the output frequency), whereas ours is a product of two different spatial orders' voltage and current in different phase planes of an isolated-neutral cell, at f_a +- f_b; (ii) the MMC cure injects a common-mode or circulating component, impossible in an isolated-neutral 3-phase cell (no zero-sequence path) while ours is cured by choosing m (m not dividing (a +- b)/c, e.g. prime 5 or 7) or by sizing capacitance; (iii) the trigger is an operating mode (pole overlap, excitation), not low output frequency. I did not find a paper that states the divisibility condition.
3. **PPM / pole-transition papers.** Libbos2025bumpless (abstract only, IEEE blocked), Wu2025minimum, Wu2023pole, Olson2024enabling, Wu2024open: no mention of DC-side or capacitor ripple during the overlap (text search of the full texts of the Wu/Olson papers: their converters share a common DC link, and the only DC-capacitor statement is the steady-state 62 % capacitance reduction cited from Libbos2022inverter). The overlap-induced pulsation is therefore unaddressed there; on a common DC bus it averages out across legs, which is why they did not need it.

**Closest paper:** Zoric2018arbitrary (same machine class, isolated neutrals possible, cascaded-DC context via Zoric2017voltage, power transferred between sets by orthogonal-plane currents). Second: Sau2019modular for the pulsation/capacitor-sizing language.
**What a reviewer would cite against it:** Sau2019modular and the MMC low-frequency ripple literature for "per-cell power pulsation and capacitor sizing is standard", Zoric2017voltage / Zoric2018arbitrary for "multiphase winding-set power sharing and DC balance", Levi2006series for "two independent orders on one inverter".
**Caveats:** IEEE full texts of Zoric, Levi, Sau, Libbos2025bumpless were not available; the Levi multi-machine papers beyond Levi2006series were seen only as search hits. 'Not found' does not prove absence.
