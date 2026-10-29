# Published numeric inputs for the analyst (T02, 2026-10-29)

Every row has a bib key (see `refs.bib`). "Sec." = taken from the review Prakht2025review, not from the original paper (original abstract only was read); check before publishing. No row below is a value I computed unless marked "derived".

## 1. Truck / heavy-vehicle motor ratings and speed ranges

| Item | Value | Key | Note |
|---|---|---|---|
| 40 t LONGRUN truck, 2 machines, EESM vs PMSM | peak torque 581.33 N m (0-3000 r/min); 200 kW at 5000 r/min (6 % slope, 50 km/h, 20 min); cruise 80 km/h for 200 min; efficiency EESM vs PMSM: start-up 94.10 vs 96.30 %, 200 kW 94.19 vs 95.85 %, cruise 92.46 vs 87.61 %; weighted 92.65 vs 88.54 % | Chen2025electromagnetic | Full text read. Max speed 8000 rpm is from the review (not found in text) |
| same, power factor and current at cruise | PF 0.96 vs 0.45; stator current 50.19 A vs 113.60 A | Chen2025electromagnetic | Full text; the 4.11 is percentage points |
| Heavy truck EESM vs PMSM | 40 t, 2 motors each 250 kW peak / 800 N m, 10 000 rpm max, peak torque to 3000 rpm, 800 V dc, gear ratio 19, gearbox efficiency 0.94, wheel radius 0.5 m; CPSR = 10 000/3000 = 3.33 (relative to 200 kW point at 5041 rpm: 1.98); the review's 1.6 is not reproducible | Mademlis2020performance | Full text read |
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

## 7. HESM parameters (D03, T02c)
Source for all of section 7: Conto2022hybrid (full text; sub-kW proof-of-concept; use for ratios, not absolute size).
| Item | Value |
|---|---|
| Pole counts | 8 poles (positive field current) and 4 poles (negative field current); rotor only reverses half of the field coils, the other half keep direction (and can be PMs) |
| PM flux share vs field share | design rule: no-load air-gap flux of the PM equals that of the field coils; field MMF N_e I_e = 450 A-turns (220 conductors x 2.05 A); field and PM flux each about 50 % of the 8-pole rotor flux. In the 4-pole mode PM and field flux add |
| PM | NdFeB UH35, 25 x 4 mm per pole; rotor OD 95 mm; field current density 10 A/mm2 (water cooling needed); copper fill 0.44 |
| Stator | 36 slots, OD 150 mm, ID 96 mm; each phase split in two halves, each half on its own inverter (each inverter half power); winding factor k_w 0.96 (8-pole) and 0.62 (4-pole) |
| Torque (MTPA) | 4.4 N m (8-pole), 1.9 N m (4-pole): ratio 0.43; base speed 1010 and 2810 r/min: ratio 2.8 (so rated power rises 1.2x in the low-pole mode: 470 W to 560 W) |
| Efficiency | 76 % (8-pole), 67 % (4-pole), IPM reference 89 % (all sub-kW; rotor Joule loss dominates) |
| Power factor | 0.97 / 0.99 (HESM) vs 0.93 (IPM) |
| Transition | not simulated |
Related HESM-type data: Bratke2022study (stator-cage HESM, drive-cycle maps; numbers not read), Cinti2025impact (I_f in flux weakening; numbers not read). KTH variable-pole machine transition cost: torque dip 10 % (<7.5 % voltage-limited) with scheduled transition, Wu2025minimum.

## 8. Drivetrain loss calibration data (T02d)
Everything here is published; items marked "derived" are my own arithmetic from a published formula, not a published result.

### 8.1 Regulatory default losses, Regulation (EU) 2017/2400 (key EU2017regulation; text from the legislation.gov.uk mirror because EUR-Lex returned a bot challenge)
| Item | Value |
|---|---|
| Axle standard loss, wheel side | T_loss,std = T_d0 + T_out/eta - T_out; T_d0 = T_0 + T_1 * i_axle |
| Single reduction axle (SR) | eta = 0.98, T_0 = 70 N m, T_1 = 20 N m |
| SR tandem / single portal | eta = 0.96, T_0 = 80, T_1 = 20 |
| Hub reduction (HR) | eta = 0.97, T_0 = 70, T_1 = 20 |
| HR tandem | eta = 0.95, T_0 = 90, T_1 = 20 |
| Transmission fallback loss at input shaft | T_l,in = (T_d0 + T_add0) + (T_d1000 + T_add1000) * n_in/1000 rpm + (f_T + f_T_add) * T_in, as printed in Annex VI Appendix 8 |
| f_T | 0.01 direct gear, 0.04 indirect gears; f_T_add = 0.04 for an angle drive |
| Drag torque T_dx = T_d0 = T_d1000 | 0.005 * T_max,in (10 N m per 2000 N m) for tooth-clutch transmissions; 0.015 * T_max,in with friction shift clutches; angle drive T_addx = 0.005 * T_max,in |
| Certified-method gear mesh efficiency (App. 7) | 0.986 external-external, 0.993 external-internal, 0.97 angle (bevel) drive, constant |
Note: with T_d0 = T_d1000 the printed formula gives a drag term that grows linearly with input speed (drag at 1000 rpm = T_d0 + T_d1000); VECTO may implement it differently, check before relying on speed dependence.

### 8.2 Gear, bearing, seal, windage models (key Yan2024power, tested on a light-duty truck e-axle; formulas transcribed from the paper)
| Loss | Model |
|---|---|
| Meshing (Ohlendorf) | P = P_in * H_V * mu_mZ; mu_mZ = 0.048 (F_bt/b / (v_Sigma,C * rho_redC))^0.2 * eta_oil^-0.05 * Ra^0.25 * X_L (exponents as in the paper's Eq. 3, check the original); lubricant factor X_L = 0.86 (mineral), 0.66 (PAO) |
| Churning (Changenet; keys Changenet2006model, Changenet2011note) | C_ch = 0.5 * rho * omega^2 * R_p^3 * S_m * C_m; C_m = 0.373 Re^-0.3 Fr^-0.25 (h_p/R_p)^1.5 (p_b/R_p)^-0.124 (V_p/V_o)^-0.576 |
| Gear windage (Ohlendorf) | P_w,p = 1.05e-4 (1 + 2.3 p_b) n_p^2.8 R_p^1.6 (0.028 mu_eq + 0.019) 0.2 D / R_p (as in the paper, check) |
| Bearing (SKF; key SKF2006friction) | M_t = M_rr + M_sl + M_drag + M_seal; M_rr = phi_ish phi_rs G_rr (nu n)^0.6; M_sl = G_sl mu_sl; phi_ish = 1/(1 + 1.84e-9 (n d_m)^1.28 nu^0.64); M_seal = K_S1 d_s^beta + K_S2 |
| Shaft seal (Freudenberg Simrit, via Yan2024power) | P = 7.69e-6 d_sh^2 n (d_sh mm, n rpm; units not stated in the paper, W assumed) |
| Measured result | Light-duty truck e-axle gearbox, input 20-60 N m, 1000-12 000 rpm, oil 50/80 C: no-load loss is above 80 % of total almost always; best oil gains up to 1.04 % efficiency; model error under 8 % |
| Mesh efficiency models | Xu2005frictional (helical), Mughal2023integrated (30 % asperity load share in mixed lubrication); Michaelis2011influence: gearbox losses can be cut by 50 % on average by oil and bearing choice |

### 8.3 Heavy-duty axle / e-axle numbers
| Item | Value | Key |
|---|---|---|
| Gearbox efficiency used in truck studies | constant 0.94, ratio 19, 2 motors | Mademlis2020performance, Filippini2024design |
| Prototype HCV e-axle, two gears | ratios 14.847 and 46.128, planetary stage costs about 1 % efficiency over the map; model error 5 % at 100 N m, up to 10 % at zero torque; maps measured at 100-400 N m input, 2500-7500 rpm | Uerlich2022experimental |
| Allison eGen Power marketing claim | large torque-speed area at 97 % efficiency, more than 65 % of the map at 95 % or higher; helical ground gears, oil shielding against churning, wheel torque 47 000 N m on 100D/130D, 550-850 V | brochure URL in traction_machine_survey.md |
| Energy share, conventional HD truck (VECTO fleet data) | aero + rolling about 70 % of energy downstream of the engine | Tansini2019calculating |
| Not found | published loss maps of ZF AxTrax 2, Meritor/Cummins 14Xe, Dana Spicer Electrified, Bosch eAxle. Manufacturers publish only peak power (AxTrax 2: 210 kW continuous, 250 kW peak per a distributor listing) and marketing efficiencies. The best open data is Uerlich2022experimental plus the VECTO defaults |

### 8.4 Motor friction and windage
| Item | Value | Key |
|---|---|---|
| Air-gap windage formula | P = k1 C_f pi rho omega^3 r^4 l; C_f = 0.515 (delta/r)^0.3 Re^-0.5 (500 < Re < 1e4), C_f = 0.0325 (delta/r)^0.3 Re^-0.2 (Re > 1e4); Re = rho omega r delta / mu; k1 = 1 smooth rotor | Bilgen1973functional, Saari1998thermal |
| Derived example (air 1.2 kg/m3, mu 1.8e-5 Pa s) | rotor radius 0.169 m, stack 0.12 m, gap 1.1 mm (Filippini2024design geometry): 21 W at 3000 rpm, 118 W at 6000 rpm, about 460 W at 10 000 rpm (Re 3.9e3, 7.8e3, 1.3e4) | derived |
| Measured mechanical loss (the only measured data found) | 2004 Prius motor + gear system: 2.4 kW at 6000 rpm with 30 kW load (7.4 % drop), falling at lower speed; 50 kW motor, not 100-400 kW | Hsu2004report |
| Measurement method | windage and bearing loss separation by rotor pairs | Long2025loss |
| Not found | a measured friction/windage loss for a 100-400 kW traction motor at known speed. Use the derived windage example plus bearing and seal models of 8.2 and flag the uncertainty |  |

### 8.5 Updated truck cycle numbers (full texts now read)
See section 1 above for corrected Chen2025electromagnetic and Mademlis2020performance values and the CPSR 3.33 vs 1.98 resolution.
