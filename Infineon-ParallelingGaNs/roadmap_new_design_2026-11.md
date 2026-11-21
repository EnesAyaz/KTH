# SPB building block: what changes after the Infineon meeting, and a roadmap for the new design

KTH, 2026-11-21. Inputs: our Infineon deck v32 (`PCB-Design/reports/infineon-meeting/`) and Infineon's written answers after the meeting.
Infineon's material is still on its way: IGD012K10S2, IGD01xK15S2 and IGD02xK20S2 datasheets, IGLC65R020D2 and IGLC65R014D2 datasheets, the IEEE paper and Altium project for the 16x paralleled 120 V GaN board, and the GaN 101 slides.
Part numbers below are taken from their list. Ratings marked *(verify)* still have to be checked against the datasheets.

---

## 1. Why we saw four big problems and Infineon saw small ones

The short answer: **every problem in the deck came from simulations of a board we haven't measured yet.** Each one was run at a worst-case setting, with one knob changed at a time, and with EPC2361 limits treated as if they were limits of GaN in general. Infineon answered from measured hardware (16 GaN in parallel), from standard derating practice, and with the gate drive treated as one system. Most of the gap comes from how we asked, not from the physics.

| # | What we said | What Infineon said | Why we disagreed |
|---|---|---|---|
| 1 | **Driver:** two EPC2361 need 12.2 A of sink current against an 8 A rating, so one channel per pair, 96 drivers and 192 supplies. We asked for ≥ 22 A. | The total pull-down loop resistance sets the sink current, not the IC. Find a "sweet spot" negative V<sub>GS,off</sub>. They suggested the 2EDF7268G. | **(a)** The 12.2 A and 22 A figures assume a **0 Ω turn-off resistor**. That is a corner case, not a requirement. Our own formula shows how quickly the current falls with a small R<sub>off</sub> (table below). **(b)** The formula ignores gate-loop inductance, so the real peak is lower. **(c)** The deck itself found that a stronger pull-down barely helps the bump (0.05 Ω still gives 1.07 V), because the gate loop (τ ≈ 2.6 ns) can't keep up with C<sub>GD</sub>·dv/dt. A strong sink was never our fix for the bump. The negative bias was, and with a negative bias the sink only has to *hold* the gate off. **(d)** We treated the 8 A peak as a hard limit. In most driver datasheets the peak current is a characteristic value set by the output-stage resistance, not an absolute maximum *(verify for 2EDF7275K)*. |
| 2 | **Gate bump:** at 0 V off the 1 V bump is above V<sub>th,min</sub> = 0.8 V. A negative bias pushes the turn-off spike towards −4 V (−4.9 V on version 1). | Use a low-inductance gate loop, a strong pull-down, **a ceramic capacitor right at the G–S terminals**, and −1 to −3 V off. Their integrated Schottky removes the dead-time penalty. | **(a)** The tight window (V<sub>th,min</sub> 0.8 V, −4 V limit, and third-quadrant drop ≈ V<sub>th</sub> + abs(V<sub>off</sub>)) belongs to the **EPC2361**. 100–200 V CoolGaN has a monolithic anti-parallel Schottky, so a deeper V<sub>off</sub> costs no dead-time loss *(verify V<sub>GS</sub> min/transient rating)*. **(b)** We never tried a G–S capacitor. It lowers the C<sub>GD</sub>/(C<sub>GS</sub>+C<sub>GD</sub>) divider and gives the displacement current a local path that bypasses the gate-loop inductance. **(c)** The −4.9 V comes from **one AC bolt** (common-source and AC-path coupling), which is a layout fault. It isn't a property of the device. |
| 3 | **Paralleling:** a 2 vs 8 nH gate-loop mismatch splits E<sub>on</sub> 4 : 1. A 0.3 V V<sub>th</sub> spread splits it about 2 : 1. We asked for bins (matched sets). | Temperature coefficients balance the devices: V<sub>th</sub> rises with T and g<sub>m</sub> falls with T, so binning isn't needed. Follow the paper for gate-loop symmetry. | **(a)** Our LTspice runs are **isothermal single pulses**. They can't show the electrothermal feedback that evens out the steady-state Tj. **(b)** The 4 : 1 case is a layout mismatch the star gate already removes (0.7 % loop spread). **(c)** Switching is only 5.0 W of the 18 W per leg; conduction (12.5 W) dominates, and R<sub>DS(on)</sub>'s positive temperature coefficient balances it. A 2 : 1 E<sub>on</sub> split moves about 0.4 W between two devices, which is roughly 0.4 W × R<sub>th</sub> ≈ 1 K for a typical R<sub>th,j-hs</sub>, before any feedback, at Tj = 69 °C. **(d)** The 0.3 V figure is a datasheet min–max spread, not the spread inside one reel. |
| 4 | **Voltage margin:** 75 V cells on 100 V parts, with a 90 V design limit for spikes. | Derate the **maximum DC voltage** to 80 %. Keep switching spikes below the **rated** V<sub>DS</sub>. No further margin. | We stacked two margins: 75 % on DC and a spike limit 10 V below the rating. With 100 V as the spike limit, **n = 3 per switch may pass**; the deck says it only failed the 90 V limit. Lower R<sub>g</sub> (2.5 Ω, faster) also becomes possible. **But note:** the 80 % applies to the *maximum* cell voltage. In the SPB that is (max battery or link voltage)/N **plus the cell-to-cell imbalance**. Infineon didn't know about that SPB-specific margin, and we haven't quantified it. |

### Turn-off peak current: the 22 A ask was a corner case

I<sub>pk</sub> = (5 V − V<sub>off</sub>) / (R<sub>pd</sub> + (R<sub>G,int</sub> + R<sub>off,ext</sub>)/n), with R<sub>pd</sub> = 0.35 Ω (2EDF7275K typ.) and R<sub>G,int</sub> = 0.4 Ω (EPC2361). This is a resistive upper bound; gate-loop L lowers it.

| n per channel | V<sub>off</sub> | R<sub>off,ext</sub> per transistor | I<sub>pk</sub> |
|---|---|---|---|
| 2 | −1.7 V | 0 Ω | 12.2 A (deck) |
| 4 | −1.7 V | 0 Ω | 14.9 A |
| 4 | −1.7 V | 1.0 Ω | 9.6 A |
| 4 | −1.7 V | 1.5 Ω | 8.1 A |
| 4 | −3 V | 1.5 Ω | 9.7 A |

So **one channel per switch of four** is close to an 8 A driver once R<sub>off</sub> is about 1–1.5 Ω. That would halve the system to 48 driver ICs and 96 isolated supplies. The open point is E<sub>off</sub>. For EPC2361 we found turn-off becomes channel-controlled above R<sub>g,off</sub> ≈ 1.5 Ω, so this must be re-checked with the CoolGaN model, at the chosen V<sub>off</sub>, and with the G–S capacitor fitted.

### What Infineon's answers don't remove (these are ours)

- **Isolation and supply count:** each cell sits up to 1200 V above ground with CMTI between cells, and there are 192 (or 96) isolated supplies. Infineon commented only on sink current. The 2EDF7268G must be checked for isolation class, CMTI and split-output support *(verify)*.
- **The shared AC take-off:** one bolt gives a ±15 % split, which is our layout. The two-bolt redraw and the Infineon 16x layout are the fixes.
- **Cell voltage balancing in the SPB:** this sets the real derating point (see row 4).
- **Measured data:** nothing we say about bump, sharing or spikes is measured yet. Version 1 has to supply that.

---

## 2. Roadmap

Main idea: **finish and measure the EPC2361 version 1 as the baseline, then design Rev C around CoolGaN using Infineon's system recipe.** Don't drop version 1. Without it we can't tell which of the four problems were real.

### Phase 0: absorb and re-baseline (now → mid Dec 2026)
1. **Read the IEEE paper and the Altium project.** Extract their gate-loop symmetry rules, the G–S capacitor value and position, the power-loop structure, and how one driver feeds 16 devices.
2. **Datasheet table: EPC2361 vs IGD012K10S2 vs IGD01xK15S2 vs IGD02xK20S2.** Compare R<sub>DS(on)</sub> typ/max, C<sub>oss,tr</sub>, τ = R·C<sub>oss,tr</sub>, Q<sub>G</sub>, V<sub>th</sub> min/typ/max and its temperature coefficient, V<sub>GS</sub> rating (DC and transient, negative side), reverse conduction, package and Kelvin pin, and R<sub>th</sub>. Add the parts to the device-FoM chart.
3. **Redo the design limits with Infineon's rule:** V<sub>DC,max,cell</sub> ≤ 0.8·V<sub>DS,rated</sub> and spikes ≤ V<sub>DS,rated</sub>. First define V<sub>link,max</sub> and the worst cell imbalance. Then re-run step 4 of the procedure (devices per switch) with the 100 V spike limit, to check whether n = 3 now passes.
4. **Voltage-class sweep with the new rule:** 100 V → 80 V cells (N = 15–16), 150 V → 120 V cells (N = 10), 200 V → 160 V cells (N = 8). Run the analytical loss model with the real Infineon R and C<sub>oss</sub>.
5. **Ask Infineon for:** SPICE models with temperature dependence, 3D or STEP footprints for Q3D, 100 V samples (available now), and a slot for the 150/200 V samples (H1 2027).

### Phase 1: version 1 (EPC2361) as a measured baseline (Dec 2026 → Feb 2027)
6. **Before ordering**, if the fab order isn't placed yet: add a **DNP 0402 G–S capacitor footprint at each EPC2361** (gate to Kelvin, at the pads). Then Infineon's recipe can be tested on our own board. Finish the two-bolt redraw and extract it in Q3D.
7. **DPT from 20 to 80 V** with a shunt per branch, plus V<sub>GS</sub> and V<sub>DS</sub> on U.FL. Sweep:
   - V<sub>off</sub> by changing the isolated supply voltage (the 5.1 V Zener fixes the +5.1 V side): 0 / −1 / −1.65 / −2.5 V. Watch the −4 V EPC limit.
   - C<sub>GS,ext</sub>: none / small / large.
   - R<sub>g,on</sub> 3.5 → 2.5 Ω.
   - Measure the bump against dv/dt, the negative undershoot, E<sub>on</sub>/E<sub>off</sub>, and the per-branch current split.
8. **Thermal sharing:** use an IR camera or Tj estimates per device in continuous operation, to check Infineon's self-balancing claim on our board.
9. **Calibrate the simulations** against the measurements, and add electrothermal (Tj-dependent) models to the paralleling study.

### Phase 2: Rev C design with 100 V CoolGaN (Jan → Apr 2027)
10. **Gate drive by Infineon's recipe:** shortest gate loop, G–S capacitor, sweet-spot V<sub>off</sub> (sweep −1 to −3 V in LTspice using the Q3D copper). Choose R<sub>off</sub> from the table above.
11. **Driver decision:** 2EDF7268G vs 2EDF7275K. Test whether **one channel per switch** (n = 4, an H-tree or two-level star like their 16x board) is acceptable on E<sub>off</sub> and the bump. Gate: if yes, use 48 drivers and 96 supplies.
12. **Devices per switch** again with the IGD012K10S2 numbers and the new voltage limits.
13. **Infineon design review** of the schematic and layout. They offered one; use the **January visit**.
14. **Rev C DPT board:** same bench, same shunts, same probes as version 1, so the joint EPC vs CoolGaN comparison is direct.

### Phase 3: voltage-class decision (H1 2027, when 150/200 V samples arrive)
15. DPT the 150 V and 200 V parts on a footprint-adapted Rev C. Decide 100 V × 16 cells, 150 V × 10, or 200 V × 8 from measured loss and part count.
16. The 650 V IGLC65R014D2 / R020D2 serves only as a reference point for the voltage-class chart (N = 2–3). The SPB case rests on low-voltage cells.

### Phase 4: leg, load and system (H2 2027)
17. Load board with the chosen device: back-to-back continuous test, thermal checks, and cell isolation and CMTI tests at 1200 V.
18. Papers. The building-block procedure needs updates in the voltage-class step (80 % rule and cell imbalance), the layout/driver step (G–S capacitor, negative bias, channel count) and the n-parallel step (100 V spike limit).

### Decision gates

| Gate | When | Question | Data |
|---|---|---|---|
| G1 | mid Dec 2026 | Does n = 3 pass with the 100 V spike limit? What V<sub>link,max</sub> and cell imbalance apply? | Phase 0, steps 3–4 |
| G2 | Feb 2027 | Does a G–S capacitor plus −2 V off remove the bump without the undershoot crossing the limit, on real hardware? | Phase 1, step 7 |
| G3 | Mar 2027 | One driver channel per switch (48 drivers) or per pair (96)? | Phase 2, steps 10–11 |
| G4 | mid 2027 | 100, 150 or 200 V class? | Phase 3 |

---

## 3. Open questions for the January visit
- What is the transient negative V<sub>GS</sub> rating of IGD012K10S2, and what is the recommended V<sub>off</sub> sweet spot for 4 in parallel?
- What G–S capacitor value and type do they use (C<sub>GS,ext</sub> relative to C<sub>iss</sub>), and where exactly is it placed?
- 2EDF7268G: isolation class, CMTI, split outputs. Is it suitable for 1200 V above ground?
- V<sub>th</sub> temperature coefficient and the spread inside one reel for the 100 V part.
- Model availability: temperature-dependent SPICE and package parasitics.
