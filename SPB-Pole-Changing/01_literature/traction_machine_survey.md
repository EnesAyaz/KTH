# Traction machine survey (T02c, A) - is the induction machine used in heavy-truck traction?

Date 2026-10-29. Rule: "unknown" means I did not find the machine type in a source I opened; it is not a guess. Sources are OEM pages, papers (bib key) or trade press. Search-result summaries of OEM pages are marked (via search) when I did not open the page myself.

## 1. Product table

| Vehicle / product | Segment | Machine type | Power | Source |
|---|---|---|---|---|
| Scania battery-electric truck | heavy truck | PMSM (Scania: "permanent magnet synchronous machine") | three machines, 230-450 kW continuous; spec sheets ~230 kW continuous / ~295 kW peak, 1300 / 2200 N m | https://www.scania.com/my/en/home/electrification/e-mobility-hub/how-it-works-scanias-electric-truck-in-eight-steps.html (opened); spec sheets via search |
| DAF XD / XF Electric (PACCAR EX-D1, EX-D2) | heavy truck | PM ("permanent magnet e-motors", DAF XD page, via search); the XF page I opened gives no type | 170-350 kW (EX-D1 170/220/270 kW; EX-D2 270/310/350 kW) | https://www.daf.global/en-us/trucks/new-generation-daf-xf-electric (opened, power only); XD page via search |
| Volvo FH / FM / FMX Electric | heavy truck | unknown (3 motors, I-Shift gearbox; type not stated) | 490 kW combined | https://www.electrive.net/2021/06/29/volvo-nennt-technische-daten-zu-e-trio-fh-fm-und-fmx/ (opened) |
| Mercedes-Benz eActros 600 | heavy truck | unknown (two-motor 800 V e-axle, 4-speed) | 400 kW continuous, 600 kW peak (one table: 650 kW) | https://www.commercialmotor.com/news/article/Mercedes-Benz-unveils-the-eActros-600-battery-electric-truck (via search) |
| MAN eTGX | heavy truck | "permanently excited synchronous motor" (trade show report, secondary) | 330 kW, 1150 N m (eCD400 variant 400 kW listing not authoritative) | https://www.automotiveworld.com/news/man-displays-electric-and-diesel-trucks-at-rtx-scotland/ (via search) |
| Tesla Semi (production) | heavy truck | unknown (not confirmed in sources found) | three motors, up to 800 kW | https://www.electrive.com/es/2026/02/10/tesla-semi-officially-boasts-800-kw-power-output/ (via search) |
| Nikola Tre BEV (FPT e-axle) | heavy truck | unknown | two off-axis motors, 420 kW each, 840 kW peak | https://www.fptindustrial.com/en/Pages/FPT-INDUSTRIAL-AND-NIKOLA-TOGETHER-AT-CES-2022 (via search) |
| ZF AxTrax AVE electric portal axle (also city-bus axle AVE 130) | truck / bus e-axle | unknown (type not stated) | two motors, 125 kW each | https://press.zf.com/press/en/media/media_13525.html (opened) |
| Allison eGen Power 100D | medium/heavy truck e-axle | unknown | two motors, ~200 kW continuous each (400 kW), ~550 kW peak | https://www.trucknews.com/road-today/allison-unveils-egen-power-electric-axles/ (via search) |
| Dana TM4 SUMO HD | truck / bus / off-highway motor-inverter | PM (Dana describes its SUMO family as permanent-magnet) | up to 475 kW peak, 260 kW continuous, 3400 rpm (top model); older sheet 350 kW peak | https://www.dana.com/globalassets/resource-library/off-highway/brochures/dana-tm4-sumo-family.pdf (via search) |
| Dana Spicer Electrified e-Axle | truck e-axle | PM (TM4 SUMO HP, trade report) | 139 kW continuous, 193 kW peak | https://www.powerprogress.com/news/dana-expands-tm4-sumo-hp-motor-inverter-series/8009995.article (via search, weak) |
| Bosch eAxle (commercial vehicles) | truck e-axle | unknown | up to 300 kW (18-49 t rigid e-axle) | https://www.just-auto.com/news/bosch-e-axle-for-new-hydrogen-electric-truck (via search) |
| Liebherr T 284 | mining truck | induction (AC induction wheel motors, Litronic Plus AC drive) | motor kW not found (engine 3000 kW) | https://manualmachine.com/liebherr/t284/1585312-user-manual (via search) |
| Komatsu 930E-5 | mining truck | AC electric drive; motor type not stated in what I found | engine 2014 kW | https://www.komatsu.com/en-br/products/equipment/trucks/electric-drive-mining-trucks/930e-5 (via search) |
| Mining dump trucks (general) | mining | "induction motors remain the most popular type for hybrid and all-electric mining dump trucks" | 90 t truck study: 370 kW rated, CPSR 1:10 | Dmitrievskii2023comparative (abstract) |
| Alstom TGV-A (1988-92) and CAF Class 100 | rail (high speed) | WRSM (wound rotor, 6 poles, slip rings); IM rejected then because of thyristor commutation | 8 x 1100 kW continuous, 3982 rpm max | Prakht2025review |
| Alstom Sybic BB 26000 locomotive (1988-98) | rail (loco) | WRSM, dual three-phase winding shifted 30 degrees, 8 poles | 2 x 2800 kW, 1930 rpm | Prakht2025review |
| Eurostar (1994) | rail (high speed) | induction | 1020 kW per motor | Torrent2018permanent |
| AGV (2004) | rail (high speed) | PMSM | 760 kW per motor | Torrent2018permanent |
| Spanish AVE classes 102-112 | rail (high speed) | induction (study proposes PMSM, higher efficiency) | 8 motors, train 8000 kW | Torrent2018permanent |
| Later Alstom trains | rail | "cheaper IMs" after new inverter generation | unknown | Prakht2025review |
| Tesla Model 3, Audi Q4 e-tron (newer) | car | switched from induction to synchronous (PM) | unknown | Prakht2025traction |
| Renault ZOE, BMW iX3 / i7, Rolls-Royce Spectre, Valeo/Mahle, ZF I2SM | car | WRSM | 100 kW to 550 kW total | Prakht2025review |
| City / transit buses (BYD, Yutong, Solaris ...) | bus | unknown (no verified source found); market-research vendor claims PMSM 78 % of all EV traction motors in 2024 (not bus-specific, weak) | unknown | https://www.meticulousresearch.com/pressrelease/579/electric-vehicle-traction-motor-market-2031 (via search) |

## 2. Reading of the table
- Every heavy-truck product where I could read the machine type uses a **permanent-magnet synchronous machine** (Scania, DAF/PACCAR, MAN, Dana). For Volvo, Mercedes, Tesla Semi, Nikola, ZF, Allison and Bosch the type is **unknown** in my sources; none of the sources I opened states an induction machine for an on-road electric truck.
- The induction machine is documented in **mining trucks** (Liebherr T 284; Dmitrievskii2023comparative) and **rail** (Eurostar, AVE 102-112, and 'consequent Alstom trains'), and in older passenger cars. Prakht2025review states "heavy-duty traction has been reliant on induction motors", which is the only direct statement about IM in heavy traction, and it refers to rail and off-highway.
- Gaps: no OEM page I opened names the machine in the Volvo, Mercedes, Tesla, Nikola or ZF e-axles; the evidence for PM there is absent, not negative. Buses: nothing verified.

## 3. Published efficiency evidence, IM vs PMSM vs EESM

| Evidence | Scale | Finding | Key |
|---|---|---|---|
| IM vs IPMSM over drive cycles, same vector drive | passenger HEV | IPMSM higher efficiency for most conditions; with optimal-flux loss minimisation the IM becomes comparable | Buyukdegirmenci2014evaluation |
| PMSM vs IM in high-speed train traction motors | rail, ~MW | PMSM rotor structures: nominal efficiency 0.965-0.9725 pu, above the IM; PMSM recommended | Torrent2018permanent |
| WRSM vs IPMSM, 40 t long-haul truck | 215 kW, 3000-8000 rpm | 40 t LONGRUN truck, 2 machines. Cruise point (80 km/h) EESM 92.46 % vs IPMSM 87.61 %, PF 0.96 vs 0.45; start-up point 94.10 vs 96.30 %; 200 kW point 94.19 vs 95.85 %; weighted total 92.65 % vs 88.54 % (+4.11 percentage points). Full text read | Chen2025electromagnetic |
| EESM vs PMSM, heavy truck | 250 kW, up to 10 000 rpm | Full text read: 40 t, 2x250 kW, 800 V; at 8064-8080 rpm / 51-55 kW EESM 97.34 % vs PMSM 86.6 %; at 5040 rpm / 200 kW 97.26 % vs 97.17 %; CHTC-TT cycle machine energy loss -57 %, inverter loss -66.8 %; gearbox efficiency assumed constant 0.94 | Mademlis2020performance |
| WRSM vs IM, mining truck | 370 kW, CPSR 10 | WRSM losses 9-24 % lower, phase current 1.3-1.5x lower; IPMSM efficiency only 86 % at max speed vs 95.6 % WRSM (secondary) | Dmitrievskii2023comparative via Prakht2025review |
| IM disadvantages in traction | general | large rotor losses and heating, heavier (about 50 % heavier than IPMSM/WRSM in one 270 kW study), inverter 125 kVA for 50 kW at CPSR 3.5-4 (utilisation 0.4) | Prakht2025traction, Prakht2025review |
| Variable-pole IM, 18 legs | 890 VA lab | combined machine+inverter loss -45 % at partial load and high speed vs 3-leg fixed-pole IM; loss -1/3 on average from pole selection | Libbos2022inverter, Libbos2020loss |
| Variable phase-pole IM | KTH | losses in partial load -45 % (cited); claims fixed IM can be on par with IPM over a full driving cycle (cites Buyukdegirmenci) | Olson2024enabling |
| EESM 510 kW, 800 V truck design | 510 kW peak | efficiency close to 97 % most of the time over CHTC-TT with optimal rotor current (machine only) | Filippini2024design |
| Allison eGen Power motor claim (marketing) | 225-450 kW | large torque-speed area at 97 % efficiency; more than 65 % of the map at 95 % or better; machine type not stated | https://allisontransmission.bynder.com/m/61872699f107894a/original/eGen-Power-Brochure.pdf (opened) |
| IM peak efficiency at truck scale | - | No published peak or cruise efficiency for a 300-350 kW traction IM found | - |

Where the IM loses, per the sources: rotor copper loss (Prakht2025traction: "large losses and heating in the rotor"), magnetising current at light load (the reason loss-minimising flux control closes the gap, Buyukdegirmenci2014evaluation, and pole changing cuts partial-load loss by up to 45 %, Libbos2022inverter), and the wide-CPSR kVA penalty (inverter utilisation 0.4).

## 4. The analyst's 97.05 % IM cruise efficiency at 300-350 kW
**Not supported by what I found; it is optimistic against the literature.** (a) I found no published 300-350 kW traction IM efficiency map. (b) The nearest quantitative data: rail PMSMs reach 96.5-97.25 pu nominal efficiency and are above the IM (Torrent2018permanent), so a 97.05 % IM figure would put the IM at or above the PMSM peak. (c) Buyukdegirmenci2014evaluation finds the IPMSM higher for most drive-cycle conditions, with the IM only comparable when flux is optimised. (d) Truck-class cruise efficiencies for machines in the 215-250 kW class are 87.6 % (IPMSM) and 92.5 % (EESM) in Chen2025electromagnetic (full text), and 86.6 % vs 97.3 % in Mademlis2020performance; a 510 kW EESM design reaches about 97 % most of the cycle (Filippini2024design); Allison advertises 97 % over a large part of its motor map (type not stated), and for the 10 kW WRSM draft 92.4-93.1 % (own-work Ayaz2026optical). If 97.05 % is a peak machine efficiency of a 300 kW class machine at its best point it is plausible only as a peak; as a cruise value (light load, high speed) it contradicts the literature, where cruise efficiency is where the IM loses (rotor loss plus magnetising current). Recommend the analyst separate peak from cruise and state whether inverter loss is included.
