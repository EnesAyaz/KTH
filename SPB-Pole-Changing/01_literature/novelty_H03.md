# novelty_H03.md  H03: SPB modules inject stator harmonics to excite a pole-changing WRSM/HESM (no exciter hardware)
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Partly done.** Stator-harmonic brushless excitation of WRSMs (including PPM on multiphase stators) is established for fixed-pole machines; for isolated-neutral modules, bipolar field reversal in a pole-changing machine and traction power it is new.

## 1. Closest papers
1. **Potter2022experimental / Potter2023harmonic** (TU Dortmund): prototype WRSM, excitation by superimposed harmonic field of different pole-pair number using existing coil groups and a modified converter; full torque at start; iron loss and dc-link voltage demand are the penalties. Did not: pole change, isolated neutrals, stack, traction power.
2. **Talebi2022asynchronously / Seyedi2025comparison** (Toliyat, TAMU): nine-phase single winding, PPM gives 6-pole synchronous plus 2-pole asynchronous harmonic; rotor induction winding plus rectifier feeds the field; 2025 comparison of PPM versus MRH, both 7 % more torque than an IM. Did not: change the main pole count, work with isolated neutrals (the 6-pole field uses common-mode currents of phases 1,4,7), or give a truck rating.
3. **Bukhari2020dual** (Ro group): open-winding, two inverters, third-harmonic injection to a rotor harmonic winding. Did not: pole change; FEA only.
4. **Sirewal2020analysis**: stator harmonic winding with thyristors. Extra winding.
5. **Ayaz2023variable / Ayaz2023concurrent / Ayaz2026primary** (own): carrier-harmonic WPT excitation, 118 W bipolar bench. Did not: harmonics through the stator coil groups.

Technical flag (own reasoning): isolated neutrals remove common-mode paths inside a module, so the excitation harmonic must be formed by inter-module phase shift, not zero-sequence current. Whether the needed rotor-side coupling survives that restriction is the first check. Series stack also forces equal average DC current through all cells, so asymmetrical harmonic power per module needs a balancing path.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Toliyat, Texas A&M (Talebi, Seyedi)**: nearest (PPM excitation, traction-oriented, nine phases).
- **Pfost, TU Dortmund (Potter)**: only experimental harmonic-excited WRSM; documents the penalties SPB must beat.
- **Ro / Kwon (Hanyang; Bukhari, Sirewal)**: open-winding variants.
- **Ayaz / Peretti, KTH**: own precursors.

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Talebi2022asynchronously,
  author = {Talebi, Dorsa and Gardner, Matthew C and Seyedi, S. Mehdi and Toliyat, Hamid A.},
  title = {{An Asynchronously Excited Brushless Wound Field Synchronous Machine}},
  booktitle = {2022 International Conference on Electrical Machines (ICEM)},
  year = {2022},
  doi = {10.1109/icem51905.2022.9910953}
}

@inproceedings{Seyedi2025comparison,
  author = {Seyedi, S. Mehdi and Talebi, Dorsa and Toliyat, Hamid A.},
  title = {{Comparison Between Pole-Phase Modulation (PPM) Technique and Modulated Rotational Harmonic (MRH) Excitation in Nine-Phase Brushless Wound-Field Synchronous Machine}},
  booktitle = {2025 IEEE International Electric Machines \&amp;amp; Drives Conference (IEMDC)},
  year = {2025},
  doi = {10.1109/iemdc60492.2025.11061165}
}

@inproceedings{Potter2022experimental,
  author = {Potter, Jan and Pfost, Martin and Schullerus, Gernot},
  title = {{Experimental Analysis of a New Type of Harmonic-Excited Synchronous Machine with Special Consideration of the Core Losses}},
  booktitle = {2022 International Conference on Electrical Machines (ICEM)},
  year = {2022},
  doi = {10.1109/icem51905.2022.9910845}
}

@inproceedings{Potter2021topology,
  author = {Potter, Jan and Pfost, Martin and Schullerus, Gernot},
  title = {{Topology Analysis of Harmonic-Excited Wound-Rotor Synchronous Machines}},
  booktitle = {2021 IEEE International Electric Machines \&amp; Drives Conference (IEMDC)},
  year = {2021},
  doi = {10.1109/iemdc47953.2021.9449529}
}

@phdthesis{Potter2023harmonic,
  author = {P{\"o}tter, Jan},
  title = {{Design and Evaluation of a New Type of Harmonic-Excited Synchronous Machine for Variable-Speed Applications}},
  school = {TU Dortmund University},
  year = {2023},
  doi = {10.17877/DE290R-26088}
}  % doi.org resolves to eldorado.tu-dortmund.de/handle/2003/44320 (not in Crossref); abstract page read

@article{Sirewal2020analysis,
  author = {Sirewal, Ghulam Jawad and Ayub, Muhammad and Atiq, Shahid and Kwon, Byung-Il},
  title = {{Analysis of a Brushless Wound Rotor Synchronous Machine Employing a Stator Harmonic Winding}},
  journal = {IEEE Access},
  year = {2020},
  doi = {10.1109/access.2020.3017102},
  volume = {8},
  pages = {151392-151402}
}

@article{Bukhari2020dual,
  author = {Bukhari, Syed Sabir Hussain and Sirewal, Ghulam Jawad and Chachar, Faheem Akhtar and Ro, Jong-Suk},
  title = {{Dual-Inverter-Controlled Brushless Operation of Wound Rotor Synchronous Machines Based on an Open-Winding Pattern}},
  journal = {Energies},
  year = {2020},
  doi = {10.3390/en13092205},
  volume = {13},
  number = {9},
  pages = {2205}
}
```
