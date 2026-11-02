# Gap matrix (T02, 2026-10-29)

Legend: Y = yes, N = no, P = partly / indirectly, - = not applicable. "Traction rating" means a traction-class power is stated (>= ~50 kW) in the paper or in the source it is cited from. "Low-voltage devices" means a stack or module of low-voltage (<= ~100 V) devices or a 48 V system.
Machine type: IM, PMSM, WRSM (includes EESM), SM-gen = synchronous generator. Access level per paper is in `papers/<key>.md`; rows marked (s) rely on secondary numbers from Prakht2025review.

| Paper (bib key) | Machine type | Pole change mechanism | Multiphase? | Isolated neutrals? | Electronic pole change? | Traction rating? | Efficiency over cycle? | Low-voltage devices? | Series-stacked? | Isolated neutrals (stack)? | DC-bus shared? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Silverman2022software | any 3-ph | none | N (3-ph) | N | N | N (2.5 kW sim) | N | Y | Y | - | - |
| Chang2019improving | PMSM (car) | none | N | N | N | Y (car) | Y | Y (Si MOSFET stack) | Y (multilevel) | - | - |
| Josefsson2012evaluation | car | none | N | N | N | Y (car) | Y | P | N | - | - |
| Siccardi2023integrated | PMSM | none | P (open winding) | P | N | N (1.63 kW) | N | Y | N | - | - |
| Zhao1995space | IM | n/a (VSD theory) | Y (dual 3-ph) | Y | N | N | N | N | N | - | - |
| Levi2007multiphase | IM | n/a | Y | P | N | N | N | N | N | - | - |
| Levi2016advances | multiphase | n/a (lists uses) | Y | P | P | P | N | N | N | - | - |
| Zhu2007electrical | IM/PM/SRM | none | N | N | N | P | P | N | N | - | - |
| Chau2008overview | PMSM | none | N | N | N | P | N | N | N | - | - |
| Soong2002field | IM/SynRM/IPM | none | N | N | N | N (2.2 kW) | N | N | N | - | - |
| Popescu2018electrical | IM/PMSM/WRSM | none | N | N | N | Y (car) | N | N | N | - | - |
| Kampker2022design | PMSM | gearbox (1/2-speed) | N | N | N | Y (41 t truck) | Y | N | N | - | - |
| Gozen2022transmission | e-axle | gearbox (2-4 speed) | N | N | N | Y (27 t truck) | Y | N | N | - | - |
| Rahman2015advances | PMSM | none | N | N | N | Y (rail, HEV) | N | N | N | - | - |
| Mademlis2020performance | WRSM vs PMSM | none (I_f weakening) | N | N | N | Y (250 kW truck) | Y | N | N | - | - |
| Chen2025electromagnetic | WRSM vs PMSM | none (I_f weakening) | N | N | N | Y (215 kW, 40 t class) | Y | N | N | - | - |
| Dmitrievskii2023comparative (s) | WRSM vs IM | none (I_f weakening) | Y (9-ph, per review) | P | N | Y (370 kW mining) | Y | N | N | - | - |
| Hussain2022wound | WRSM | none (I_f weakening) | N | N | N | Y (60 kW) | Y | N | N | - | - |
| Prakht2025traction | WRSM | none | N | N | N | P | N | N | N | - | - |
| Prakht2025review | WRSM | none (review) | P | N | N | Y | P | N | N | - | - |
| Krupp2015rotary | WRSM | exciter only | N | N | N | Y | N | N | N | - | - |
| Stella2024excitation | WRSM | exciter only | N | N | N | Y | N | P (800 V SiC) | N | - | - |
| Margner2010control | WRSM | none | N | N | N | Y (car) | P | N | N | - | - |
| Ran2024drive | WRSM vs IPM | none | N | N | N | Y | Y | N | N | - | - |
| Graffeo2020cylindrical | WRSM | none | N | N | N | Y | N | N | N | - | - |
| Baloch2019distributed | WRSM (vernier) | rotor field coil-group current reversal | N | N | N (field reversal) | N | N | N | N | - | - |
| Gerber2024evaluation | SM-gen | rotor field MMF shaping | N | N | N | N | N | N | N | - | - |
| Osama1997modeling | IM | stator coil-group reversal | Y | P | Y | N | N | N | N | - | - |
| AbdelKhalik2019nine | IM | stator, 9-ph PAM | Y (9) | N (6 terminals) | Y | P (EV) | N | N | N | - | - |
| Bitsi2019induction | IM | independent coils | Y | Y | Y | N | N | N | N | - | - |
| Bitsi2022design | IM | independent coils, pole-phase | Y | Y | Y | N (20 kW) | P (maps, no cycle) | P (150 V machine limit) | N | - | - |
| Mallampalli2021six | IM | stator, 6-ph | Y (6) | N | Y | N (1 kW) | N | N | N | - | - |
| Mallampalli2020starter | IM | stator 8/4-pole | P | N | Y | N (48 V SG) | P | Y (48 V) | N | - | - |
| Yang2012electronic | IM | stator, 9-ph | Y (9) | N | Y | N | N | N | N | - | - |
| Latif2021loss | IM | stator 4/2-pole | P | N | Y | N | P (loss-optimal) | N | N | - | - |
| Rohith2018pole | IM (2-ph) | stator 2/4-pole | P | N | Y | N | Y (WLTP-derived) | N | N | - | - |
| vanderGiet2007induction | IM | Dahlander (contactor) | N | N | N | N | N | N | N | - | - |
| Ostovic2002pole | PM memory | re-magnetisation | N | N | P (pulses) | N | N | N | N | - | - |
| Sakai2013permanent | PM memory | re-magnetisation | N | N | P (pulses) | N | P | N | N | - | - |
| Sakai2014permanent | PM memory | re-magnetisation | N | N | P (pulses) | N | P | N | N | - | - |
| Du2022dual | PMSM | harmonic + switched winding | N | N | N (switches) | N (15 N m) | N | P (250 V) | N | - | - |
| Wang2015design | PM memory | re-magnetisation | N | N | P (pulses) | N | N | N | N | - | - |
| **Ayaz2026primary (own-work, P1)** | WRSM/EESM | rotor field coil-group reversal (2/4-pole), bipolar WPT exciter, anti-parallel rectifiers + self-driven switch | N | N | P (rotor side electronic, no contactor; stator side not described) | N (118 W bench) | N | N | N | - | - |
| **Ayaz2026optical (own-work, P2, unpublished)** | WRSM | rotor coil-group reversal, 3-channel optical exciter | N (3-ph assumed) | N | P | P (10 kW, 4/2-pole FEA) | P (two operating points, FEA) | N | N | - | - |
| Ayaz2023variable (own-work) | EESM | none (unipolar exciter) | N | N | N | N | N | P (inverter harmonics reused) | N | - | - |
| Ayaz2023concurrent (own-work) | dc motor | none | N | N | N | N | N | P (GaN) | N | - | - |
| Ayaz2024evaluation (own-work) | PMSM-type | none | P (2L-6Ph) | N | N | Y (HDV) | Y | N | N | - | - |
| Ayaz2026dclink (own-work) | HDV | none | N | N | N | Y (250 kW, 1.2 kV) | P | N (SiC) | N | - | - |
| Bocker2025minimizing | PMSM | none | N | N | N | Y (long-haul) | Y | N | N | - | - |
| Baloch2020wound | WRSM (vernier) | rotor field-set reversal, prototype | N | N | N | N | N | N | N | - | - |
| Conto2023pole | hybrid reluctance-PM | rotor + stator polarity change | N | N | N | N | N | N | N | - | - |
| Conto2022hybrid | hybrid-excited PM | excitation windings change rotor poles, stator polarity change | N | N | N | N | N | N | N | - | - |
| Mingardi2017geometry | line-start PM | stator winding rearranged | N | N | N | N | N | N | N | - | - |
| Filippini2024design | EESM | none (I_f optimisation) | N | N | N | Y (truck cycle) | Y | N | N | - | - |
| Dey2024novel | EESM/HESM | bipolar exciter, rotary transformer, frequency-selected | N | N | N | N | N | N | N | - | - |
| Huang2024novel | PMSM | none | Y (6 stator windings) | P | N | N (0.725 N m) | N | N | N | - | - |
| Raj2022design | IM | 3-ph/6-pole <-> 9-ph/2-pole | Y | P | Y | P (EV) | N | N | N | - | - |
| Latif2023control | IM | 4/2-pole electronic | P | N | Y | P (traction) | N | N | N | - | - |
| Libbos2023winding | IM | variable-pole windings, 18 legs | Y | P | Y | P (EV) | P | N | N | - | - |
| Wu2023pole | IM (WICSC) | independent coils, HPD | Y | Y | Y | N | N | N | N | - | - |
| Olson2024enabling | IM | HPD modelling | Y | Y | Y | N | N | N | N | - | - |
| Wu2025minimum | IM | 9-ph, transition control | Y | P | Y | N | N | N | N | - | - |
| Lin2025optimal | IM | transition current distribution | Y | P | Y | N | P (loss min.) | N | N | - | - |
| Tilahune2026speed | IM (9-ph) | sensorless transition | Y | P | Y | N | N | N | N | - | - |
| Tilahune2023performance | IM | 3-ph/4-pole <-> 6-ph/2-pole (FEM) | Y | P | Y | P (traction) | N | N | N | - | - |
| Haq2023online | IM | online stator reconfiguration | Y | P | Y | N | N | N | N | - | - |
| Haq2024ripple | IM (9-ph) | ripple-free transition | Y | P | Y | N | N | N | N | - | - |
| Wu2024open | IM (18-ph) | fault-tolerant transition | Y | P | Y | N | N | N | N | - | - |
| **Conto2022hybrid (HESM, full text)** | HESM (NdFeB IPM + DC field coils) | rotor field coil reversal (half the coils) + stator two-inverter half-phase supply, 8 <-> 4 poles | Y (2 inverters, split phases) | P | Y (stator sign of inverter 2; no contactor) | N (0.5 kW) | N | N | N | - | - |
| Conto2022dual | HESM-type (reluctance-PM) | rotor pole change with stator | N | N | N | N | N | N | N | - | - |
| Bratke2022study | HESM with stator cage | pole changing (cage bars as phases) | Y (many bars) | P | Y | P (passenger cycles) | Y (drive-cycle energy) | N | N | - | - |
| Cinti2025impact | HESM | none (flux weakening via I_f + I_d) | N | N | N | N | N | N | N | - | - |
| Brown2022wound | WFSM/HESM | none | N | N | N | P | N | N | N | - | - |
| Libbos2022inverter | IM | 6/4/2-pole by 18-leg GaN inverter | Y (18 legs) | P | Y | N (890 VA) | Y (partial-load loss -45 %) | Y (GaN) | N | - | - |
| Libbos2020loss | IM | pole selection by torque and speed | Y | P | Y | N | Y (loss -1/3) | N | N | - | - |
| Matsuyama2021design | IM | 8-phase harmonic operation, 8 <-> 12 poles | Y | N | Y | P (EV) | N | N | N | - | - |
| Buyukdegirmenci2014evaluation | IM vs IPMSM | none | N | N | N | N (HEV) | Y | N | N | - | - |
| Torrent2018permanent | IM vs PMSM | none | N | N | N | Y (rail) | P | N | N | - | - |
| Yan2024power | e-axle gearbox | none | N | N | N | P (light-duty truck e-axle) | N (loss model) | N | N | - | - |
| Uerlich2022experimental | HCV e-axle (2-speed) | gearbox | N | N | N | Y (HCV axle) | P (efficiency map model) | N | N | - | - |
| EU2017regulation | HD truck axle / transmission defaults | none | N | N | N | Y | Y (VECTO) | N | N | - | - |
| Magill2015dynamic | IM (PPM model) | pole-phase modulation | Y | Y (independent inputs) | Y | N | N | N | N | - | - |
| Libbos2020modular | IM | variable pole, modular multiphase legs | Y | P | Y | N | N | Y (modular low-voltage legs) | N | N | Y (common DC bus) |
| Libbos2019variable | IM | variable pole, 18 legs | Y | P | Y | N | N | N | N | N | Y |
| Chaubal2024continuously | IM | continuously variable pole, 18 legs | Y | P | Y | N | P | N | N | N | Y |
| Libbos2025bumpless | IM | bumpless electronic pole change | Y | P | Y | N | N | N | N | N | Y |
| Maheshwari2025modulation | IM | high phase count, variable pole | Y | Y | Y | N | N | N | N | N | Y |
| Reddy2020multilayer | IM | multilayer fractional-slot PPM, 15 phases | Y | P | Y | Y (traction) | N | N | N | N | Y |
| Umesh2016dual | IM | dual-inverter PPM, 9 phases, 4/12 poles | Y | N | Y | N (5 hp) | N | N | N | N | Y (one DC link) |
| Reddy2018multilevel | IM | open-end-winding PPM, dual inverter | Y | N | Y | N | N | N | N | Y (outputs add) | P |
| Runde2019iscad | IM (stator cage) | ISCAD, one leg per bar | Y (many legs) | Y | P | Y (300 kW at 48 V) | P | Y (48 V) | N | N | Y (48 V bus, parallel) |
| Bachheibl2015control | IM (stator cage) | ISCAD control, up to 60 bars, 18-phase proof | Y | Y | Y | P | P | Y (48 V) | N | N | Y |
| Sarrazin2011cascaded | EV drive (cells) | none | N (3-ph) | N | N | P | P | Y (48 V cells) | N | Y | N (separate cell sources) |
| Tarisciotti2020modular | motor drive (MMC) | none | N | N | N | N | N | Y | N | Y (MMC arms) | P |
| Boxriker2017effects | PMSM | coil configuration switching, pole changing, phases | Y | N | N | N | N | N | Y (cost term) | N | Y |
| Boxriker2016expanding | PMSM | optimum phase number | Y | N | N | N | N | N | N | N | Y |
| Talebi2022asynchronously | WFSM | harmonic excitation (no pole change) | Y (9-ph) | N (common neutral) | N | P | N | N | N | N | Y |
| Seyedi2025comparison | WFSM | PPM vs modulated rotational harmonic excitation, 9-ph | Y | N | P | N | N | N | N | N | Y |
| Potter2021topology | WRSM | harmonic excitation | Y | N | N | N | N | N | N | N | Y |
| Potter2022experimental | WRSM | harmonic excitation, experimental | Y | N | N | N | N | N | N | N | Y |
| Potter2023harmonic | WRSM | harmonic-excited machine (thesis) | Y | N | N | N | N | N | N | N | Y |
| Sirewal2020analysis | WRSM | stator harmonic winding | N | N | N | N | N | N | N | N | Y |
| Bukhari2020dual | WRSM | dual-inverter open-winding brushless | Y (open winding) | P | N | N | N | N | N | N | N (two inverters, separate sources assumed) |
| Wu2023openphase | IM | pole transition under open phase | Y | Y | Y | N | N | N | N | N | Y |
| Norrga2013SPB | SPB origin | none | Y | Y | N | N | N | Y | Y | Y | N |
| Jin2017Modulation | SPB | none | Y | Y | N | N | N | P | Y | Y | N |
| Nikouie2017Stability | SPB | none | Y | Y | N | N | N | N | Y | Y | N |
| Nikouie2016operation | SPB | none (fault survival) | Y | Y | N | N | N | N | Y | Y | N |
| Jin2018Distributed | SPB | none | Y | Y | N | N | N | N | Y | Y | N |
| Verkroost2019Interleaving | 15-ph AFPMSM IMMD | none | Y | P | N | N | N | N | N | P | Y |
| Verkroost2021Ripple | 15-ph IMMD | none | Y | P | N | N | N | N | N | P | Y |
| Verkroost2024VoltageBalance | 15-ph AFPMSM, SPB | none | Y | Y | N | N | N | Y | Y | Y | N |
| Verkroost2024PowerDistribution | 15-ph AFPMSM, SPB | none (unequal power sharing) | Y | Y | N | N | N | Y | Y | Y | N |
| Verkroost2024Reconfiguration | 15-ph AFPMSM, SPB | none (online cell bypass) | Y | Y | N | N | N | Y | Y | Y | N |
| Bringezu2020SPB | SPB, 6/9/12-ph non-aligned | none | Y | Y | N | N | N | P | Y | Y | N |
| Rohner2024GaN | SPB, 7.5 kW IMD | none | Y | Y | N | N | N | Y | Y | Y | N |
| Zoric2017voltage | 9-ph IM | none | Y | Y (3 neutrals) | N | N | N | N | Y | Y | N |
| Zoric2018arbitrary | 9-ph IM gen | none (x-y power sharing) | Y | P | N | N | N | N | N | P | Y |
| Subotic2019active | multi-3-ph IM | none | Y | P | N | N | N | N | N | P | Y |
| Che2014SeriesConnected | 6-ph IM | none (DOF used for balance) | Y | Y | N | N | N | N | Y | Y | N |
| OpenEndWindingDrive | 6-ph OEW PMSM | none | Y | Y | N | N | N | Y | Y | Y | N |
| Ni2025SeriesDCLinkStability | multiphase | none | Y | Y | N | N | N | N | Y | Y | N |
| Wu2020ActiveBalancing | IMMD | none | Y | P | N | Y | N | N | Y | P | N |
| Wang2015GaNIMMD | IM IMMD | none | Y | P | N | N | N | Y | Y | P | N |
| Wang2025GaNIMMD | IMMD aircraft | none | Y | P | N | Y | N | N | Y | P | N |
| Ruseler2015InputSeries | OEW split-winding IM | none | Y | Y | N | N | N | N | Y | Y | N |
| Gjerde2014SeriesFault | wind generator | none | Y | Y | N | Y | N | N | Y | Y | N |
| CascadedHBridgefault | n-ph machine, CHB | none (post-bypass xy) | Y | Y | N | N | N | N | Y | Y (separate sources) | N |
| Cengelci2000MMMI | MV motor groups | none | Y | Y | N | Y | N | N | N | Y | Y |
| SPB1windturbine | wind generator | none | Y | Y | N | N | N | N | Y | Y | N |
| SPB2BLDC | BLDC | none | Y | Y | N | N | N | Y | Y | Y | N |
| Zhang2014SPBMachine | FSCW PM | none | Y | Y | N | N | N | N | Y | Y | N |
| Mohamed2022IntegratedDCLink | 15-coil AFM IMMD | reconfigurable phase configurations | Y | P | P | N | N | N | N | P | Y |

## Gaps SPB pole changing would fill

### Induction machine (IM)
1. **Contactorless pole changing at traction power and low-voltage devices.** All electronic pole-changing IM work (Osama1997modeling, AbdelKhalik2019nine, Yang2012electronic, Latif2021loss, Mallampalli2021six) is at lab or at most 48 V / 20 kW scale with full-voltage devices; none uses a stack of low-voltage GaN modules. SPB gives one isolated-neutral coil group per module with a modulation-set phase shift, which is the Osama coil-group scheme.
2. **Drive-cycle efficiency of pole changing in a heavy-truck class.** Bitsi2022design shows gains are mostly efficiency and depend on voltage/current limits (no extension below an 18 A limit in their 2-pole case), but only with maps, no cycle, no inverter loss, 20 kW. Nobody has combined pole-changing maps, a 40 t long-haul cycle and inverter loss (SPB loss model). Chang2019improving covers inverter cycle efficiency but with a fixed pole count.
3. **Replacing the gearbox or oversized inverter.** Truck work uses multi-speed gearboxes (Kampker2022design, Gozen2022transmission); Prakht2025traction cites a 125 kVA inverter for a 50 kW IM with CPSR 3.5. Whether SPB pole changing (CPSR above 4 reported by AbdelKhalik2019nine) removes both is open.

### Wound-rotor synchronous machine (WRSM / EESM) - revised after own-work (T02b)
Covered by Enes's own work (own-work, small scale): bipolar rotor excitation for a pole-changing EESM. P1 (Ayaz2026primary, IEEE TIE 2026) does it with a dual-input dual-output WPT, anti-parallel rectifiers and a self-driven MOSFET-diode switch (2.88 A, 118 W bench, 99 % rectifier efficiency, bipolar current and frequency-detuned magnitude, no rotor active converter). P2 (Ayaz2026optical, unpublished draft) does it optically and gives a 10 kW 4-pole/2-pole PC-WFSM FEA design (92.4 % at 3000 rpm 4-pole, 93.1 % at 6000 rpm 2-pole). Other bipolar exciters exist (Dey2024novel, Huang2024novel), and prototype-validated WF pole changing exists for a vernier machine (Baloch2020wound). Earlier statements that "no traction WRSM pole-changing study exists" and that "a bipolar exciter is an open item" are therefore corrected: the mechanism and a bipolar exciter exist; the traction-scale, system-level and SPB parts do not.

Still open beyond Enes's work:
1. **Scaling to a traction rotor.** P1 is a 118 W bench test with an emulated field; P2 is a 10 kW FEA design. A 350 kW truck rotor (field power in the kW range, 1.2 kV system) has not been designed or tested.
2. **Excitation from the SPB stator itself (P3).** Each isolated-neutral coil group of the SPB can carry an injected excitation component (carrier phase-shift / superimposed harmonic voltage), removing the WPT or optical hardware. Ayaz2023variable and Ayaz2023concurrent show it for a single inverter, unipolar, small scale; P1 names it as future work. Nothing is published for multi-star, bipolar, pole-changing machines.
3. **The stator side of the WRSM pole change.** P1 and P2 treat the rotor; the stator pole-count change (which phase/coil-group arrangement, contactors or SPB modulation) is not described in the text read. Peretti's HPD work (Wu2023pole, Olson2024enabling) gives the model for the IM; the synchronous equivalent with a locked rotor pattern is open.
4. **Pole-transition torque gap over a drive cycle.** P1 uses free-wheel to zero (tau_f = L_f/R_f) plus blanking, a no-torque interval scheduled like a gear shift; the gradual k-transition (P4) is only a simulation target. Minimum-torque-dip transitions exist for IM (Wu2025minimum, Haq2024ripple) but not for a WRSM, and no drive-cycle energy cost of transitions exists.
5. **What pole changing adds over I_f weakening** in a 40 t truck (Chen2025electromagnetic, Filippini2024design): unquantified.
6. **PMSM** remains the no-pole-change baseline except for memory-magnet and hybrid-rotor machines (Ostovic2002pole, Conto2023pole).

### Common to both
- No source combines multi-star isolated-neutral windings, low-voltage devices and traction-class pole changing. Thin coverage: bus and rail (only Rahman2015advances for rail; no bus-specific paper verified) and a numeric truck drive cycle with pole changing.

### Hybrid-excited synchronous machine (HESM), added by D03 (T02c)
Covered: Conto2022hybrid is the only hybrid-excited PM + field-coil machine found that changes poles on purpose. Mechanism (full text read): half the rotor field coils reverse (the other half are replaced by PMs), and the stator changes poles by feeding each phase's two halves from two inverters with equal or opposite currents. It was shown only as a sub-kW static FEA design (4.4 / 1.9 N m, 76 / 67 % efficiency against 89 % for an IPM). Bratke2022study is the only HESM pole-changing paper that computes drive-cycle energy, and it finds a benefit. Cinti2025impact shows HESM flux weakening by I_f.

Open for SPB + HESM:
1. **Scale and efficiency at traction power.** The 76 / 67 % efficiency of the only built-for-purpose machine is caused by the tiny size; no HESM pole-changing machine above 1 kW is published.
2. **Transition dynamics.** Conto2022hybrid does not simulate the pole change in time; the PM fixes part of the rotor flux during the change, so the transition behaviour (rotor flux share that the field must cancel or reinforce) is unknown.
3. **SPB supplies the stator side natively.** The two-inverter half-phase supply of Conto2022hybrid is a 2-module special case of SPB; N isolated-neutral modules give finer control, redundancy and low-voltage devices.
4. **Drive-cycle study for a truck**, with PM share vs field share as the design variable (the PM carries the base flux, the field reverses it): not published.

### Series-stacked and isolated-neutral coverage (added 2026-11-02, from novelty_H01..H09)
No new paper combines series-stacked cells with isolated-neutral coil groups and pole changing. Closest: Sarrazin2011cascaded and Tarisciotti2020modular (stacked/cascaded cells, no pole changing, no isolated coil groups), Libbos2020modular / Chaubal2024continuously (many legs and pole changing but one common DC bus, full-voltage or 48 V devices), and Runde2019iscad / Bachheibl2015control (48 V ISCAD, parallel bus, stator cage). Reddy2018multilevel adds outputs of dual inverters into a multilevel voltage with PPM but still at full-voltage devices. Columns for rows added before this date were filled "N" for series-stacked where no stack is used and "-" (not assessed) for the other two new columns.

### Correction after importing the SPB lineage (2026-11-02)
The earlier statement that no source combines series stacking with isolated neutrals is wrong at the topology level: Norrga2013SPB, Nikouie2017Stability, Verkroost2019-2024 (Ghent), Zoric2017voltage (9-phase, three isolated neutrals, cascaded VSIs), Che2014SeriesConnected and OpenEndWindingDrive all do. What remains not found is pole/phase mode change in such a stack, the mode-dependent power balance (H10), and the admissible mode set after cell bypass (H11). Online cell bypass in an SPB is published (Verkroost2024Reconfiguration).
