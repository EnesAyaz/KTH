# Yan2024power

**Power Loss Evaluation of an E-Axle Gearbox Considering the Influence of Gear Oil Factors** (2024), Lubricants. DOI: https://doi.org/10.3390/lubricants12010011

Access: abstract + full text read (MDPI open access).

- **Claim:** Systematic power-loss model of an E-axle gearbox (gears, bearings, seals, auxiliary), tested on a light-duty truck E-axle with four gear oils: no-load loss dominates.
- **Method:** Component models: Ohlendorf meshing loss P = P_in H_V mu_mZ with mu_mZ = 0.048 (F_bt/b / v_Sigma,C rho_redC)^0.2 ... X_L (X_L = 0.86 for mineral oil, 0.66 for PAO); Changenet churning C_ch = 0.5 rho omega^2 R_p^3 S_m C_m with C_m = 0.373 Re^-0.3 Fr^-0.25 (h_p/R_p)^1.5 (p_b/R_p)^-0.124 (V_p/V_o)^-0.576 (as transcribed); Ohlendorf windage P_w,p; SKF bearing model Eqs. 7-14; Freudenberg seal P_VD = 7.69e-6 d_sh^2 n (d_sh in mm, n in rpm; units not stated in the text, W assumed). Test: 12 speeds 1000-12 000 rpm, input torque 20-60 N m, oil temperature 50 and 80 C.
- **Machine / inverter:** Single-reduction light-duty truck e-axle gearbox, motor speeds up to 12 000 rpm (typical e-motor 12 000 rpm to wheel 300 rpm).
- **Power / voltage / speed numbers:** No-load loss is almost always more than 80 % of total gearbox loss in the tests (load 20-60 N m); churning is the largest single component (>40 % at the shown case); best oil raised efficiency up to 1.04 % over the worst; model error below 8 % for all evaluated cases.
- **Relevance to SPB:** Directly usable: three formulas for the analyst to implement the gear mesh, churning, bearing and seal losses of the SPB truck e-axle gearbox.
- **Limitations:** Light-duty truck, low torque (20-60 N m input); coefficients to be calibrated to the actual geometry and oil; formula transcription from PDF text is partly garbled.
