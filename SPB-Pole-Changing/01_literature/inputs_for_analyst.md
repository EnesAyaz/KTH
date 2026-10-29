# Published numeric inputs for the analyst (T02, 2026-10-29)

Every row has a bib key (see `refs.bib`). "Sec." = taken from the review Prakht2025review, not from the original paper (original abstract only was read); check before publishing. No row below is a value I computed unless marked "derived".

## 1. Truck / heavy-vehicle motor ratings and speed ranges

| Item | Value | Key | Note |
|---|---|---|---|
| 40 t long-distance truck, WRSM vs IPMSM | max 215 kW, 581 N m; rated speed 3000 rpm, max 8000 rpm; stack OD 258 mm, L 200 mm | Chen2025electromagnetic | Sec. Speed ratio 8000/3000 = 2.67 (derived), matches CPSR 2.67:1 in review table |
| same, duty cycle | about 90 % of operation at high speed; efficiency at high speed 92.46 % (WRSM) vs 87.61 % (IPMSM); cycle-average +4.11 % for WRSM; power factor 0.96 vs 0.45 | Chen2025electromagnetic | Sec. |
| Heavy truck EESM vs PMSM | max 250 kW, 800 N m; rated speed 5041 rpm, max 10 000 rpm; OD 300 mm, L 360 mm; EESM phase current 3.67x lower at max speed | Mademlis2020performance | Sec. 10 000/5041 = 1.98 (derived); review table lists CPSR 1.6:1, inconsistent, flagged |
| 90 t mining dump truck, WRSM vs IM | 370 kW rated; 400 to 4000 rpm (CPSR 1:10); max torque 8833 N m; stator OD 668 mm; WRSM active mass -15 %, phase current 1.3-1.5x lower, losses 9-24 % lower | Dmitrievskii2023comparative | Sec. Mining, not on-road |
| Typical road-vehicle CPSR | 1:3 to 1:4 | Prakht2025review | Statement in section 3.3 |
| Produced WRSM passenger-car CPSR | about 2:1 to 3:1 | Prakht2025review | |
| 41 t long-haul tractor-trailer axle | two PMSM, 1- or 2-speed gearbox; requirements from static driving profiles (kW/N m in paper body, not extracted) | Kampker2022design | Open the paper for the numbers |
| 27 t BE truck | dual e-motor e-axle; both motors at same speed saves up to 5 %, one off saves up to 0.6 % | Gozen2022transmission | Energy benchmark for operating-point matching |
| Inverter oversizing for wide CPSR | 50 kW IM with CPSR 3.5 needs 125 kVA inverter (utilisation 0.4); CPSR 4:1 also 125 kVA | Prakht2025traction | Quoted from its introduction |

## 2. Commercial WRSM traction motors (field weakening by I_f)

| Machine | Rating | Key |
|---|---|---|
| Renault ZOE R135 | 100 kW, max 11 300 rpm | Prakht2025review |
| Renault ZOE R110 | 80 kW, 10 900 rpm | Prakht2025review |
| BMW iX3 | 210 kW, 400 N m | Prakht2025review |
| BMW i7 xDrive60 (rear) | 360 kW, 650 N m | Prakht2025review |
| Rolls-Royce Spectre | two WRSMs, 550 kW total, 1075 N m | Prakht2025review |
| Valeo/Mahle plan | 220-350 kW, brushless excitation | Prakht2025review |
| ZF I2SM | 75-550 kW, inductive brushless exciter | Prakht2025review |
| Statement | all mass-produced traction WRSMs use brushes (at review date) | Prakht2025review |

Hussain2022wound: 60 kW WRSM, 2768 rpm rated, 191.46 N m, 120.5 V rms back EMF, 178.5 A rms; efficiency better than Prius 2010 IPMSM at light load above base speed.

## 3. Pole-changing machine parameters (prototype or FEM)

| Machine | Parameters | Key |
|---|---|---|
| WICSC IM (KTH), two designs 2-pole and 6-pole | 20 kW, 64 N m, 3000 rpm; DC bus 300 V (machine limit 150 V); current limit 22 A (about 2.5x rated torque); 2-pole: best pole 2 to 4 at about 2x rated torque, 4-pole voltage-limited near 2400 rpm, 2-pole again from 2645 rpm; no envelope extension for current limit <= 18 A; 4-pole lowest loss above 73 N m at 1500 rpm; 6-pole: 8-pole +12 % torque below 1680 rpm, 2/4-pole widen flux weakening | Bitsi2022design |
| 9-phase 6-terminal PAM IM | pole ratio 2:1; constant power over more than 4 pu speed | AbdelKhalik2019nine |
| 6-phase pole-changing IM | 1 kW prototype; +15 % peak torque vs 3-phase pole changing | Mallampalli2021six |
| 48 V 8/4-pole IM | starter-generator; stack shortened vs baseline | Mallampalli2020starter |
| Dahlander IM, variable frequency | speed ratio 2:1 | vanderGiet2007induction |
| PM pole-changing, 8/4 poles | core loss -49 % (no load), -33 % (load); speed range x2 | Sakai2013permanent |
| PM pole-changing, 8/4 poles | iron loss -46 to -55 %; speed range x3 | Sakai2014permanent |
| Dual-harmonic PM motor | 250 V bus; 8-pole 15 N m to about 2750 rpm; 24-pole to about 16 000 rpm (8.9x base, 5.8x 8-pole maximum) | Du2022dual |
| WRSM with reversible field set (vernier) | two field winding sets, one reversed; FEA, no ratings in abstract | Baloch2019distributed |

No parameters (resistances, inductances) of any pole-changing IM or WRSM were extracted. The analyst will need to build a parametric model; Bitsi2022design is the closest published geometry-level data (full text has maps, not tabulated electrical parameters).

## 4. Low-voltage-device inverter data

| Item | Value | Key |
|---|---|---|
| 5-cell stacked inverter | 2.5 kW, 300 Hz torque bandwidth (simulation) | Silverman2022software |
| IMMD for open-winding PMSM | 97 % peak efficiency at 1.63 kW; loss-model error 3.6 % | Siccardi2023integrated |
| Multilevel low-voltage Si MOSFET vs IGBT vs SiC | cycle efficiency and cost comparison on reference vehicle (values not extracted) | Chang2019improving |

## 5. Not found, analyst must assume or ask the leader
- A 40 t long-haul drive cycle with speed/torque histogram (Drive Cycle sibling folder has it).
- Rail and bus traction ratings (no verified source).
- Rotor-field exciter ratings for a truck WRSM with polarity reversal.

## 6. Own-work seeds (T02b, own-work)
| Item | Value | Key |
|---|---|---|
| PC-WFSM 10 kW draft (unpublished, parameters unverified) | 4-pole 3000 rpm / 2-pole 6000 rpm, 400 V dc, stator OD/ID 200/122 mm, stack 80 mm, 36 slots, 48 turns/phase, kw 0.925, airgap 0.5 mm, field 24 turns/12.5 A/R_f 0.093 ohm/300 A-turns per pole; loss 822 W (4-pole, 92.4 %) and 798 W (2-pole, 93.1 %); stator Cu 488 W | Ayaz2026optical |
| Bipolar WPT exciter bench | 72 V in, 600 uH / 14.2 ohm load, +/-2.88 A, 118 W, 99 % rectifier efficiency (87 % at 0.61 A), 95 kHz resonance, 97-105 kHz detuning; pole-change gap = free-wheel (tau_f = L_f/R_f) + blanking | Ayaz2026primary |
| 250 kW SiC inverter, 1.2 kV | efficiency ~99.12 %, 49.4 kW/L, loss model within ~10 % | Ayaz2026dclink |
| Variable phase-pole IM configurations | 3ph/6-pole <-> 9ph/2-pole; 3ph/4-pole <-> 6ph/2-pole; 9-phase and 18-phase prototypes | Raj2022design, Tilahune2023performance, Tilahune2026speed, Wu2024open |
