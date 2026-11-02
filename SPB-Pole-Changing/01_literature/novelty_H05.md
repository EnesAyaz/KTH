# novelty_H05.md  H05: pole changing lowers cruise voltage, SPB parks cells, joint pole-and-cell scheduling
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**New (no paper found), with a serious feasibility flag.** Pole scheduling for loss is published (Libbos); cell deactivation for motor-drive efficiency is not.

## 1. Closest papers
1. **Libbos2022inverter / Libbos2020loss**: pole count as an efficiency variable (-45 % combined loss at partial load). Did not: deactivate legs or modules; all legs stay active.
2. **Chaubal2024continuously**: blending poles for loss; no module scheduling.
3. **Sarrazin2011cascaded**: cascaded H-bridge EV, better cell management, spread losses, fault operation. Did not: pole changing or deliberate cell parking.
4. **Tarisciotti2020modular**: MMC for low-voltage drives. No cell scheduling for efficiency.
5. Search hits not opened: converter-side phase shedding (parallel inverters, interleaved dc-dc) and MMC traction studies (Birmingham) reporting better efficiency at reduced speed; treat as unverified.

Feasibility flag (own reasoning): in a series DC stack every cell passes the same average DC current. A parked cell either needs a DC-side bypass switch (then the remaining cells see V_dc/(N-1), eating device headroom at 75 V class on a 1200 V bus) or it keeps conducting DC current through its capacitor. This could kill H05 unless a bypass-plus-voltage-margin design is shown.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Libbos / Krein / Banerjee**: partial-load loss logic (without module parking).
- **Cardenas / Tarisciotti (Chile / Nottingham)**: modular low-voltage drive converters.
- **Chalmers / Birmingham CHB-MMC EV work**: cell-level management (not verified in detail).

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Sarrazin2011cascaded,
  author = {Sarrazin, B. and Rouger, N. and Ferrieux, J.P and Crebier, J.C},
  title = {{Cascaded Inverters for electric vehicles: Towards a better management of traction chain from the battery to the motor?}},
  booktitle = {2011 IEEE International Symposium on Industrial Electronics},
  year = {2011},
  doi = {10.1109/isie.2011.5984149}
}

@article{Tarisciotti2020modular,
  author = {Tarisciotti, Luca and Costabeber, Alessandro and Tardelli, Francesco and Cardenas, Roberto},
  title = {{Modular Multilevel Converter Based Topology for High-Speed, Low-Voltage Electric Drives}},
  journal = {IEEE Transactions on Industry Applications},
  year = {2020},
  doi = {10.1109/tia.2020.3006462},
  volume = {56},
  number = {5},
  pages = {5202-5211}
}

@inproceedings{Chaubal2024continuously,
  author = {Chaubal, Soumil and Libbos, Elie and Mukherjee, Debranjan and Maheshwari, Anuj and Banerjee, Arijit and Krein, Philip T.},
  title = {{Continuously-Variable-Pole Induction Machine Drive for Electric Vehicles}},
  booktitle = {2024 IEEE Transportation Electrification Conference and Expo (ITEC)},
  year = {2024},
  doi = {10.1109/itec60657.2024.10598847}
}

@inproceedings{Libbos2020modular,
  author = {Libbos, Elie and Hao, Ruomu and Ku, Bonhyun and Banerjee, Arijit and Krein, Philip T.},
  title = {{Modular Multiphase Drives for Variable-Pole Induction Machines in Electric Vehicles}},
  booktitle = {2020 IEEE Applied Power Electronics Conference and Exposition (APEC)},
  year = {2020},
  doi = {10.1109/apec39645.2020.9124085}
}
```
