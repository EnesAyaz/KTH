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
