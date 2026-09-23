# Capacitors for the EPC2361 one-pair revision P1

Research checked 2026-09-21. Scope: 75 V maximum bus, 50 kHz nominal / 100 kHz maximum switching. These are prototype candidates, not a qualified capacitor bank.

## Recommended starting point

Use TDK **C2012X7S2A105K125AB**, 1 uF / 100 V / X7S / 0805, for a distributed near-FET bank. It offers a manufacturer simple-model inductance of **0.480 nH per component**. The existing TDK **C3225X7R2A225K230AB**, 2.2 uF / 100 V / X7R / 1210, remains a useful larger-capacitance alternative with **0.600 nH** model inductance. Neither is a reverse-geometry part; the recommendation is a low-inductance assembled bank of conventional MLCCs.

| Candidate | Nominal rating | Body L x W x T | Manufacturer simple-model L1 | Model R1 |
|---|---|---|---|---|
| C2012X7S2A105K125AB | 1 uF, +/-10%, 100 V, X7S | 2.00 x 1.25 x 1.25 mm | 0.480 nH | 6.0 mOhm |
| C3225X7R2A225K230AB | 2.2 uF, +/-10%, 100 V, X7R | 3.20 x 2.50 x 2.30 mm | 0.600 nH | 2.7 mOhm |

Both were listed in production. Values above are typical equivalent-circuit parameters, not guaranteed worst-case ESL, mounted loop inductance, or constant ESR across the switching spectrum. X7S permits +/-22% temperature change; X7R +/-15%. The nominal capacitance is not the capacitance available at 75 V.

Sources: [0805 product](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7S2A105K125AB), [1210 product](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R2A225K230AB), [TDK C2012 model table, p. 5](https://product.tdk.com/system/files/dam/technicalsupport/tvcl/pdf/capacitor_mlcc_com_midvoltage_c2012_ecm.pdf), [TDK C3225 model table](https://product.tdk.com/system/files/dam/technicalsupport/tvcl/pdf/capacitor_mlcc_com_midvoltage_c3225_ecm.pdf).

## Parallel-bank arithmetic and placement

For equal, uncoupled branches, capacitor-only inductance is L1/N. Eight 0805 components therefore give 0.060 nH; twelve give 0.040 nH. Four 1210 components give 0.150 nH. These numbers deliberately exclude shared copper, mounting, vias, mutual coupling and unequal current division. They are not a board inductance claim and the banks are not compared at equal effective capacitance.

Make the top-side row the principal fast bank, directly adjacent to the high-side drain, with its negative pads transitioning to the first inner DC-minus return. Put additional bottom-side parts beneath the capacitor region, not beneath the FET cold-plate contact corridor. Bottom parts need short paired rail transitions; a full-thickness board connection can make them less effective at the fastest edge than the top bank. Do not count all top and bottom parts as equally effective without extraction.

Keep individual connections broad and short, use multiple tightly located return vias, and remove shared narrow rail necks. Adding capacitor count cannot remove shared inductance. Do not add mixed values indiscriminately: assess impedance peaks with the external bulk capacitor and supply inductance.

## DC bias and ripple qualification still required

TDK links DC-bias LTspice models, precision SPICE models, S-parameters and ripple-temperature curves on both product pages. The numeric 75 V bias data and ripple curves were not successfully retrieved in this session; a direct model download returned HTTP access denied. Therefore **no numeric effective capacitance at 75 V or allowable RMS current is claimed**. The simple-model nominal capacitance must not be substituted for a bias model.

Before freezing the quantity, obtain C(V,T,age), frequency-dependent ESR and ripple-temperature data from TDK, then calculate current in each branch from the complete inverter/DC-link network. The 220 A RMS output is not the RMS current in an individual capacitor. Evaluate heating using the harmonic sum P = sum(I_rms,k^2 * ESR(f_k,T)), with actual current distribution. Validate on the populated board and include enclosure/cold-plate temperature. The 100 V rating must cover DC bus plus capacitor-terminal ripple/transients; FET Vds overshoot is a separate waveform.

## Reverse-geometry investigation

KYOCERA AVX LICC standard parts list ratings only through 25 V. Automotive KAL lists up to 50 V. They cannot be connected directly across this 75 V bus. No suitable 100 V reverse-geometry candidate was verified, so none is placed in this design. Series strings would introduce balancing and impedance complications and are not selected here.

Sources: [AVX LICC datasheet](https://datasheets.kyocera-avx.com/LICC.pdf), [AVX KAL range](https://www.kyocera-avx.com/products/ceramic-capacitors/low-inductance/aec-q200-low-inductance-capacitors/).

AVX L2F/L3F feedthrough families do offer 100 V options, but are intended for filtering/conditioning; a feedthrough part must not be selected to carry the cell power current without a suitable current rating and verified connection model. They are not included in this power-bank proposal. [Manufacturer family page](https://www.kyocera-avx.com/products/ceramic-capacitors/feedthru-smd/l2fl3f-series/).

Murata explains that reverse geometry reduces the internal path length and widens the path, but also explicitly distinguishes component ESL from board/via inductance. [Murata low-ESL mounting discussion](https://article.murata.com/en-us/article/methods-of-using-low-esl-capacitors).
