# LMG1210 model acquisition and LTspice status

PCB work is paused at P8 placement at the user's request. The PCB heartbeat is paused.

## Official model
- TI product page: https://www.ti.com/product/LMG1210
- Unencrypted PSpice download: https://www.ti.com/lit/zip/snom677
- Retrieved 2026-09-23; original archive and extracted library preserved under models/ti-lmg1210.
- Library header: model Final 2.2, 2019-03-08; intended simulator PSpice 16.2.
- Features stated by TI: PWM/independent mode, dead-time programming, LDO, propagation delay and UVLO.

## Actual LTspice check
The unchanged library reports behavioral-expression syntax problems. A separate experimental adaptation normalizes nested braces in behavioral VALUE expressions and removes an inline PSpice marker. Original source is preserved. Reproducible adaptation: scripts/adapt_lmg1210.py.

The adapted standalone driver test completes, but HO and LO maxima are only approximately 0.61 V for the current test circuit. This is NOT a passing driver-function test. Supply/startup, pin mapping and model translation must be diagnosed before connecting the power stage. LTspice also limits internal diode emission coefficient N=0.01 to 0.1; this is a simulator behavior difference, not a validated equivalent model. Do not use these preliminary results to assess hardware operation or losses.

The smoke test has ideal HB supply, grounded HS, 1 nF capacitive output loads, and independent inputs. It is not the 75 V half bridge and does not test bootstrap operation.

A community LTspice example is available on TI's support forum, but it has not been downloaded/validated:
https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1004807/lmg1210-lmg1210-working-ltspice-model-with-no-errors

## Intended system tests after model validation
1. Driver alone: regulated output supply, approximately 5 V gate swing, correct IIM logic and propagation delay; then bootstrap startup and floating HS operation.
2. Four EPC2361 devices (two per arm), 75 V DC, independent nonoverlapping HI/LI, individual gate resistors, local DC-link capacitors.
3. Inductive double-pulse test targeting approximately 51.9 A total peak, observing both low-side currents, VDS, VGS and gate overlap.
4. 50/100 kHz switching cases; sweep assumed power/gate inductance, capacitor ESR/ESL and device mismatch. These are sensitivity assumptions, not extracted P8 parasitics.

EPC official library lists EPC2361 model version 1.00 dated 2024-03-07:
https://epc-co.com/epc/design-support/device-models/pspicemodels
No complete-system run has yet been made. A successful SPICE run will not qualify PCB thermal capability or real-world switching overshoot by itself.
