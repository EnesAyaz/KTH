# Gap matrix (T02, 2026-10-29)

Legend: Y = yes, N = no, P = partly / indirectly, - = not applicable. "Traction rating" means a traction-class power is stated (>= ~50 kW) in the paper or in the source it is cited from. "Low-voltage devices" means a stack or module of low-voltage (<= ~100 V) devices or a 48 V system.
Machine type: IM, PMSM, WRSM (includes EESM), SM-gen = synchronous generator. Access level per paper is in `papers/<key>.md`; rows marked (s) rely on secondary numbers from Prakht2025review.

| Paper (bib key) | Machine type | Pole change mechanism | Multiphase? | Isolated neutrals? | Electronic pole change? | Traction rating? | Efficiency over cycle? | Low-voltage devices? |
|---|---|---|---|---|---|---|---|---|
| Silverman2022software | any 3-ph | none | N (3-ph) | N | N | N (2.5 kW sim) | N | Y |
| Chang2019improving | PMSM (car) | none | N | N | N | Y (car) | Y | Y (Si MOSFET stack) |
| Josefsson2012evaluation | car | none | N | N | N | Y (car) | Y | P |
| Siccardi2023integrated | PMSM | none | P (open winding) | P | N | N (1.63 kW) | N | Y |
| Zhao1995space | IM | n/a (VSD theory) | Y (dual 3-ph) | Y | N | N | N | N |
| Levi2007multiphase | IM | n/a | Y | P | N | N | N | N |
| Levi2016advances | multiphase | n/a (lists uses) | Y | P | P | P | N | N |
| Zhu2007electrical | IM/PM/SRM | none | N | N | N | P | P | N |
| Chau2008overview | PMSM | none | N | N | N | P | N | N |
| Soong2002field | IM/SynRM/IPM | none | N | N | N | N (2.2 kW) | N | N |
| Popescu2018electrical | IM/PMSM/WRSM | none | N | N | N | Y (car) | N | N |
| Kampker2022design | PMSM | gearbox (1/2-speed) | N | N | N | Y (41 t truck) | Y | N |
| Gozen2022transmission | e-axle | gearbox (2-4 speed) | N | N | N | Y (27 t truck) | Y | N |
| Rahman2015advances | PMSM | none | N | N | N | Y (rail, HEV) | N | N |
| Mademlis2020performance (s) | WRSM vs PMSM | none (I_f weakening) | N | N | N | Y (250 kW truck) | Y | N |
| Chen2025electromagnetic (s) | WRSM vs PMSM | none (I_f weakening) | N | N | N | Y (215 kW, 40 t class) | Y | N |
| Dmitrievskii2023comparative (s) | WRSM vs IM | none (I_f weakening) | Y (9-ph, per review) | P | N | Y (370 kW mining) | Y | N |
| Hussain2022wound | WRSM | none (I_f weakening) | N | N | N | Y (60 kW) | Y | N |
| Prakht2025traction | WRSM | none | N | N | N | P | N | N |
| Prakht2025review | WRSM | none (review) | P | N | N | Y | P | N |
| Krupp2015rotary | WRSM | exciter only | N | N | N | Y | N | N |
| Stella2024excitation | WRSM | exciter only | N | N | N | Y | N | P (800 V SiC) |
| Margner2010control | WRSM | none | N | N | N | Y (car) | P | N |
| Ran2024drive | WRSM vs IPM | none | N | N | N | Y | Y | N |
| Graffeo2020cylindrical | WRSM | none | N | N | N | Y | N | N |
| Baloch2019distributed | WRSM (vernier) | rotor field coil-group current reversal | N | N | N (field reversal) | N | N | N |
| Gerber2024evaluation | SM-gen | rotor field MMF shaping | N | N | N | N | N | N |
| Osama1997modeling | IM | stator coil-group reversal | Y | P | Y | N | N | N |
| AbdelKhalik2019nine | IM | stator, 9-ph PAM | Y (9) | N (6 terminals) | Y | P (EV) | N | N |
| Bitsi2019induction | IM | independent coils | Y | Y | Y | N | N | N |
| Bitsi2022design | IM | independent coils, pole-phase | Y | Y | Y | N (20 kW) | P (maps, no cycle) | P (150 V machine limit) |
| Mallampalli2021six | IM | stator, 6-ph | Y (6) | N | Y | N (1 kW) | N | N |
| Mallampalli2020starter | IM | stator 8/4-pole | P | N | Y | N (48 V SG) | P | Y (48 V) |
| Yang2012electronic | IM | stator, 9-ph | Y (9) | N | Y | N | N | N |
| Latif2021loss | IM | stator 4/2-pole | P | N | Y | N | P (loss-optimal) | N |
| Rohith2018pole | IM (2-ph) | stator 2/4-pole | P | N | Y | N | Y (WLTP-derived) | N |
| vanderGiet2007induction | IM | Dahlander (contactor) | N | N | N | N | N | N |
| Ostovic2002pole | PM memory | re-magnetisation | N | N | P (pulses) | N | N | N |
| Sakai2013permanent | PM memory | re-magnetisation | N | N | P (pulses) | N | P | N |
| Sakai2014permanent | PM memory | re-magnetisation | N | N | P (pulses) | N | P | N |
| Du2022dual | PMSM | harmonic + switched winding | N | N | N (switches) | N (15 N m) | N | P (250 V) |
| Wang2015design | PM memory | re-magnetisation | N | N | P (pulses) | N | N | N |
| **Ayaz2026primary (own-work, P1)** | WRSM/EESM | rotor field coil-group reversal (2/4-pole), bipolar WPT exciter, anti-parallel rectifiers + self-driven switch | N | N | P (rotor side electronic, no contactor; stator side not described) | N (118 W bench) | N | N |
| **Ayaz2026optical (own-work, P2, unpublished)** | WRSM | rotor coil-group reversal, 3-channel optical exciter | N (3-ph assumed) | N | P | P (10 kW, 4/2-pole FEA) | P (two operating points, FEA) | N |
| Ayaz2023variable (own-work) | EESM | none (unipolar exciter) | N | N | N | N | N | P (inverter harmonics reused) |
| Ayaz2023concurrent (own-work) | dc motor | none | N | N | N | N | N | P (GaN) |
| Ayaz2024evaluation (own-work) | PMSM-type | none | P (2L-6Ph) | N | N | Y (HDV) | Y | N |
| Ayaz2026dclink (own-work) | HDV | none | N | N | N | Y (250 kW, 1.2 kV) | P | N (SiC) |
| Bocker2025minimizing | PMSM | none | N | N | N | Y (long-haul) | Y | N |
| Baloch2020wound | WRSM (vernier) | rotor field-set reversal, prototype | N | N | N | N | N | N |
| Conto2023pole | hybrid reluctance-PM | rotor + stator polarity change | N | N | N | N | N | N |
| Conto2022hybrid | hybrid-excited PM | excitation windings change rotor poles, stator polarity change | N | N | N | N | N | N |
| Mingardi2017geometry | line-start PM | stator winding rearranged | N | N | N | N | N | N |
| Filippini2024design | EESM | none (I_f optimisation) | N | N | N | Y (truck cycle) | Y | N |
| Dey2024novel | EESM/HESM | bipolar exciter, rotary transformer, frequency-selected | N | N | N | N | N | N |
| Huang2024novel | PMSM | none | Y (6 stator windings) | P | N | N (0.725 N m) | N | N |
| Raj2022design | IM | 3-ph/6-pole <-> 9-ph/2-pole | Y | P | Y | P (EV) | N | N |
| Latif2023control | IM | 4/2-pole electronic | P | N | Y | P (traction) | N | N |
| Libbos2023winding | IM | variable-pole windings, 18 legs | Y | P | Y | P (EV) | P | N |
| Wu2023pole | IM (WICSC) | independent coils, HPD | Y | Y | Y | N | N | N |
| Olson2024enabling | IM | HPD modelling | Y | Y | Y | N | N | N |
| Wu2025minimum | IM | 9-ph, transition control | Y | P | Y | N | N | N |
| Lin2025optimal | IM | transition current distribution | Y | P | Y | N | P (loss min.) | N |
| Tilahune2026speed | IM (9-ph) | sensorless transition | Y | P | Y | N | N | N |
| Tilahune2023performance | IM | 3-ph/4-pole <-> 6-ph/2-pole (FEM) | Y | P | Y | P (traction) | N | N |
| Haq2023online | IM | online stator reconfiguration | Y | P | Y | N | N | N |
| Haq2024ripple | IM (9-ph) | ripple-free transition | Y | P | Y | N | N | N |
| Wu2024open | IM (18-ph) | fault-tolerant transition | Y | P | Y | N | N | N |

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
