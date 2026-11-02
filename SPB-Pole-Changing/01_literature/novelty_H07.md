# novelty_H07.md  H07: hybrid-excited machine makes SPB pole changing worthwhile at truck scale
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Partly done.** HESM pole changing exists at sub-kW; truck-scale value and SPB stator are new, but the T03c result already weakens the value case.

## 1. Closest papers
1. **Conto2022hybrid** (Padova): 8/4-pole HE-IPM, field coils reverse, stator two-inverter half-phase supply (k_w 0.96 versus 0.62), 0.5 kW, static FEA, 76/67 % efficiency. Did not: transitions, scale, many modules.
2. **Bratke2022study**: HESM with stator cage, pole changing, drive-cycle energy benefit (abstract only). Did not: truck, low voltage.
3. **Conto2023pole / Conto2022dual**: reluctance-PM rotor with Dahlander stator; 4-pole reluctance mode about 50 % efficient.
4. **Baloch2020wound** (WF vernier prototype), **Dey2024novel** (bipolar exciter).
5. **Boxriker2017effects**: PMSM pole changing as a torque-speed area lever; no field coil.

No new HESM pole-changing paper surfaced in the new searches beyond these.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Bianchi / Padova (Conto)**: direct owner of HESM pole changing; the 2-inverter stator is a 2-module SPB.
- **Doppelbauer / KIT** (PMSM pole changing); **Ayaz / Peretti** (own bipolar excitation).

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Boxriker2017effects,
  author = {Boxriker, Miriam and Kolb, Johannes and Doppelbauer, Martin},
  title = {{Effects of coil configuration switching, pole-changing and multi-phase windings on permanent magnet synchronous motors}},
  booktitle = {IECON 2017 - 43rd Annual Conference of the IEEE Industrial Electronics Society},
  year = {2017},
  doi = {10.1109/iecon.2017.8216325}
}

@inproceedings{Potter2022experimental,
  author = {Potter, Jan and Pfost, Martin and Schullerus, Gernot},
  title = {{Experimental Analysis of a New Type of Harmonic-Excited Synchronous Machine with Special Consideration of the Core Losses}},
  booktitle = {2022 International Conference on Electrical Machines (ICEM)},
  year = {2022},
  doi = {10.1109/icem51905.2022.9910845}
}
```
