# NCP51820 gate-driver review

## Result

NCP51820 is a stronger functional match than LMG1210 for this half bridge because it has independent HIN and LIN inputs, separate source/sink outputs for both gates, an enable input, and built-in shoot-through prevention. It accepts a 9-17 V VDD supply and internally regulates approximately 5.2 V low-side and high-side gate supplies. The 75 V bus is far below its 650 V switch-node rating.

The current EPC2361 power stage has no dedicated source-Kelvin pin. NCP51820's application note explicitly addresses that case: keep each gate return short and separate from high-current source copper. Its PGND/SGND arrangement must be checked against our shared-DC- reference. Do not insert an individual source shunt without rechecking this return; a shared PGND/SGND connection can bypass it.

At the present prototype target of two EPC2361s per switch and 100 kHz maximum, the driver's 1 A source / 2 A sink peak ratings are adequate as a starting point, but the final gate resistor and thermal check must use the EPC2361 gate charge at the actual 5 V drive voltage. Independent gate resistors remain required for current sharing and ringing control.

## SPICE availability

Onsemi's current public model listing identifies an **NCP51820 SIMPLIS model**, not an LTspice or unencrypted PSpice model. I found no official NCP51820 LTspice model download. The official datasheet and layout note are available at:

- https://www.onsemi.com/download/data-sheet/pdf/ncp51820-d.pdf
- https://www.onsemi.com/pub/Collateral/AND9932-D.PDF

Therefore do not substitute the LMG1210 model or invent a behavioral NCP51820 model and call it device-accurate. For the first LTspice system run, use a transparent behavioral driver wrapper with the NCP51820 pin behavior: separate HIN/LIN, EN, VDD=12 V, VDDL/VDDH=5.2 V, finite source/sink resistance, propagation delay and dead-time. Replace it with an official model if Onsemi supplies one or use SIMPLIS for the vendor model.

## Recommendation

Use NCP51820 as the next driver candidate for the hardware schematic, subject to its 4 x 4 mm QFN15 footprint, bootstrap component placement, and PGND/SGND return review. Keep LMG1210 as the simulation baseline only until the NCP51820 behavioral model is validated. The NCP51820 is suitable for the electrical voltage, frequency and input-control requirements; its missing LTspice model is the current simulation limitation.
