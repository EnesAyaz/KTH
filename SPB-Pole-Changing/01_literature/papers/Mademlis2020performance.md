# Mademlis2020performance

**Performance Evaluation of Electrically Excited Synchronous Machine compared to PMSM for High-Power Traction Drives** (2020), 2020 International Conference on Electrical Machines (ICEM). DOI: https://doi.org/10.1109/icem49940.2020.9270852

Access: abstract + full text read (IEEE PDF supplied by Enes).

- **Claim:** EESM vs PMSM for heavy-duty truck drives: adjustable flux moves the best-efficiency region to usual operating points and raises power factor.
- **Method:** FEM and Matlab whole-drivetrain simulation, truck case study.
- **Machine / inverter:** EESM vs PMSM, stator inverter.
- **Power / voltage / speed numbers:** SUPERSEDED by the full-text addition below. Earlier Secondary, via Prakht2025review: 250 kW max, 800 N m max, 10 000 rpm max, rated speed 5041 rpm, stack OD 300 mm, length 360 mm; EESM phase current 3.67x lower than IPMSM at max speed.
- **Full-text addition (corrects abstract-level and secondary numbers):** Truck: 40 t, 2 motors (each 250 kW peak, 800 N m, 10 000 rpm max, EESM and PMSM designs with 48 slots, stack not stated here), DC link 800 V, 1.2 kV SiC modules (CAB450M12XM3, 450 A), gear ratio 19, transmission efficiency 0.94, wheel radius 0.5 m, Cd 0.53, Cr 0.0051, tires 295/75 R22.5, 100 km/h max. Requirements: start-up peak torque 5 min on 12 % slope; high power 400 kW for 20 min on 6 % slope at 50 km/h; best-efficiency point 100 kW at 80 km/h. Peak torque held to 3000 rpm. Operating point table: 5040-5041 rpm, 200/207 kW: efficiency PMSM 97.17 %, EESM 97.26 %; 8064-8080 rpm, 51-55 kW: PMSM 86.6 % (current 320 A, PF 0.261) vs EESM 97.34 % (87 A, PF 0.951). Over the CHTC-TT cycle: machine energy losses of the EESM are 57 % lower and inverter losses 66.8 % lower than PMSM. CPSR: 10 000/3000 = 3.33 relative to the peak-torque base speed; 10 000/5041 = 1.98 relative to the 200 kW point. The 1.6 value in the review's table cannot be reproduced from this paper.
- **Relevance to SPB:** Truck-class numbers for the WRSM leg of D01; weakening by I_f.
- **Limitations:** Full text now read; the earlier second-hand numbers (via Prakht2025review) are corrected in the full-text addition. Simulation plus prototype tests; truck model only.
- **SPB note (from full text):** The same 40 t / 800 V / ratio 19 / 0.94 gear-efficiency truck is used by Filippini2024design; the 0.94 constant gearbox efficiency is the number the analyst's detailed axle model must beat or justify.
