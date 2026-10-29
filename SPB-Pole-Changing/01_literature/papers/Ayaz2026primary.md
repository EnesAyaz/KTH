# Ayaz2026primary

**Tags: own-work**

**Primary-Side Control of Bipolar Field Excitation System for Pole-Changing Electrically Excited Synchronous Machines** (2026), IEEE Transactions on Industrial Electronics. DOI: https://doi.org/10.1109/tie.2026.3658721

Access: abstract + local manuscript draft read (Field Excitation/manuscript.pdf, same title and authors; published version TIE 73(8) pp. 12539-12544 not read).

- **Claim:** own-work. Bipolar field excitation for pole-changing EESMs with no rotor-side active converter and no gate-signal link across the gap.
- **Method:** Dual-input dual-output series-series WPT; two Tx/Rx coil sets, each feeding a diode rectifier; the two rectifier outputs are connected anti-parallel on the field winding; a MOSFET in anti-series with a diode is self-driven from the rectifier output (resistive divider + zener + gate resistor) and blocks the inactive path. Polarity = which transmitter is energised; magnitude = WPT frequency detuning (97 to 105 kHz). Bench test with an inductive load emulating the field winding.
- **Machine / inverter:** EESM rotor with four field coil groups L_F1..L_F4 (Fig. 1 of the draft): 2-pole and 4-pole rotor patterns differ by the current direction in selected groups. Stator-side connection is NOT described in the paper; the letter treats the stator as pole-changing and focuses on the exciter. Exciter: two coil sets, anti-parallel rectifiers.
- **Power / voltage / speed numbers:** Prototype: 72 V input, 14.2 ohm / 600 uH emulated field, bipolar +/-2.88 A (118 W), rectifier efficiency 99 % at full current (87 % at 0.61 A); Rx resonance 95 kHz, operating 95-110 kHz. Pole-change sequence: field current free-wheels to zero (tau_f = L_f/R_f) then a blanking interval, scheduled like a gear shift.
- **Relevance to SPB:** Own prior art for the WRSM leg of D01: bipolar rotor excitation is solved at small scale. Open for SPB: traction-scale rotor, and replacing the WPT link by excitation harvested from stator harmonics of the SPB inverter (letter's own future work).
- **Limitations:** Bench only (118 W, emulated load, no machine); no pole-change torque data; scale-up not done.
