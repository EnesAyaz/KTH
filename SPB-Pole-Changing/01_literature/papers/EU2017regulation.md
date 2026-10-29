# EU2017regulation

**Commission Regulation (EU) 2017/2400 (Annex VI Appendix 7-8, Annex VII Appendix 3)** (2017), OJ L 349, 29.12.2017. No DOI (see refs.bib url)

Access: text read from legislation.gov.uk as-adopted mirror (EUR-Lex returned an empty bot-challenge response, not bypassed).

- **Claim:** VECTO certification: standard (fallback) torque-loss values for components without a certified loss map.
- **Method:** Annex VII Appendix 3 (axle) and Annex VI Appendices 7-8 (transmission).
- **Machine / inverter:** HD truck axle (SR, HR, tandem), manual/AMT/automatic transmission, angle drive.
- **Power / voltage / speed numbers:** Axle standard loss (Annex VII App. 3): wheel-side T_loss,std = T_d0 + T_out/eta - T_out, with T_d0 = T_0 + T_1 * i_axle. Table 1: single reduction axle (SR) eta 0.98, T0 = 70 N m, T1 = 20 N m; single-reduction tandem axle / single portal (SRT/SP) eta 0.96, T0 = 80, T1 = 20; hub reduction (HR) eta 0.97, T0 = 70, T1 = 20; hub reduction tandem (HRT) eta 0.95, T0 = 90, T1 = 20. Transmission standard loss (Annex VI App. 8): T_l,in = (T_d0 + T_add0) + (T_d1000 + T_add1000) x n_in/1000 rpm + (f_T + f_T_add) x T_in, as printed; f_T = 1 - eta = 0.01 for the direct gear and 0.04 for indirect gears; f_T_add = 0.04 for an angle drive; drag torque T_dx = T_d0 = T_d1000 = 10 N m x T_max,in/2000 N m = 0.005 T_max,in for tooth-clutch transmissions (SMT, AMT, DCT) and 0.015 T_max,in for transmissions with friction shift clutches; angle drive T_addx = 0.005 T_max,in. Calculated (certified method) gear-mesh efficiencies eta_m, App. 7 (3.1.1.2): external-external 0.986, external-internal 0.993, angle drive (bevel) 0.97, constant.
- **Relevance to SPB:** These are the regulator's default numbers for an uncertified e-axle: a fixed-ratio single reduction e-axle would be 0.98 with 70 + 20 i N m drag at the wheel; a helical gear mesh 0.986 per mesh.
- **Limitations:** Defined for ICE trucks with up to ~1 kN m-class drive axles; drag values scale with T_max and axle ratio, not with oil or speed; T_d1000 is read as printed, VECTO may combine terms differently; no e-axle specific values.
