# novelty_H06.md  H06: torque-gap-free pole transition via per-module control
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Done for IM** (experimentally, three independent groups). Open only for synchronous rotors, where the rotor field time constant, not the stator, sets the gap.

## 1. Closest papers
1. **Libbos2025bumpless** (TTE 2025): droop-control bumpless transition, flux transitions as fast as 200 ms, torque within machine ripple, 18-leg. Did: the claim for IM.
2. **Wu2025minimum** (KTH, TEC): 10 % torque dip (below 7.5 % with voltage limit) versus hard switch 133 %, PPM 83 %, premagnetisation 50 %. 15 kW lab.
3. **Haq2024ripple** (KTH, ECCE): ripple-free phase-pole modulation of a 9-phase IM. **Lin2025optimal**: constant-torque current distribution with minimum copper loss.
4. **Wu2023pole**: HPD-based loaded transition, 0.528 s pre-demagnetisation.
5. Own: P1 (free-wheel to zero, tau_f = L_f/R_f) and P5 (field reversal to 95 % in 677 ms) show the synchronous gap.

The SPB-specific statement that per-module control removes the gap is therefore not a differentiator; the hypothesis should be restated as a synchronous-rotor transition (excitation handover, k-sweep of P4) or dropped.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Libbos / Krein / Banerjee**: bumpless, experimental.
- **Peretti / KTH**: minimum dip, sensorless, fault cases.
- **Keerthipati group; Magill/Krein**: earlier transition models.

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@article{Libbos2025bumpless,
  author = {Libbos, Elie and Chaubal, Soumil and Maheshwari, Anuj and Banerjee, Arijit and Krein, Philip T.},
  title = {{Bumpless Electronic Pole-Changing for Variable-Pole Induction Machines}},
  journal = {IEEE Transactions on Transportation Electrification},
  year = {2025},
  doi = {10.1109/tte.2024.3401613},
  volume = {11},
  number = {1},
  pages = {1201-1213}
}

@inproceedings{Magill2015dynamic,
  author = {Magill, Matthew P. and Krein, Philip T.},
  title = {{A dynamic pole-phase modulation induction machine model}},
  booktitle = {2015 IEEE International Electric Machines \&amp; Drives Conference (IEMDC)},
  year = {2015},
  doi = {10.1109/iemdc.2015.7409030}
}

@inproceedings{Wu2023openphase,
  author = {Wu, Yixuan and Peretti, Luca},
  title = {{Pole Transition Under Open Phase Fault Conditions in a Variable Pole Machine}},
  booktitle = {IECON 2023- 49th Annual Conference of the IEEE Industrial Electronics Society},
  year = {2023},
  doi = {10.1109/iecon51785.2023.10312343}
}
```
