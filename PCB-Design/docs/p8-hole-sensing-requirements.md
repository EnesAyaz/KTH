# Hole-threaded low-side current sensing - supersedes raised-link approach

User correction: use PCB holes to thread two Rogowski coils around existing flat current paths, one for QL1 and one for QL2. Avoid raised conductors because minimum power-loop inductance is the priority. P7's raised LK1/LK2 arrangement is therefore not the accepted final design. Preserve it only as a previous study; do not manufacture it.

## Required electrical topology

Keep both low-side sources and local gate-source references in their compact arrangement. Investigate a flat drain-current path for each device between the shared AC copper and that device's drain pads. Each Rogowski winding must link all of the selected device's drain current exactly once, without linking the other device branch or an equal opposite return current. Voltage taps stay at the device drain/source pads. Do not substitute output-current holes or sum-current measurement.

P5/P7 geometry has continuous L2 DC-minus copper under the local top-side power conductors; the low-side device centre spacing is 18 mm. A winding threaded through the PCB surrounds conductors on every layer inside its aperture. Holes alone therefore do not prove device-current sensing: the enclosed L2 return, L3 collector, B.Cu AC paths, gate returns and vias must be evaluated. Simply placing holes either side of a top trace can enclose its opposing return and cancel much of the signal.

Drilling does not need to interrupt the measured top trace, but drilling/clearances may interrupt nearby planes. Where the opposite return would otherwise be enclosed, it must pass outside the sensed aperture. This changes the magnetic geometry, so zero added loop inductance cannot be promised. Minimize and quantify that change rather than assuming it is negligible. Prefer copper-preserving positions; do not cut a large return-plane slot solely to make a probe fit without comparing the resulting loop.

## Confirmed sensor envelope

PEM CWTUM dimensions, March 2024 issue 03: winding diameter 1.6 mm with +0.1/-0 tolerance; standard circumference 80 mm with +3/-0 tolerance; minimum bend radius 10 mm. The drawing also includes a larger closing-head assembly, so winding diameter alone cannot set the threading-hole size. Final holes must account for the part actually passed through them, insertion clearance and permitted bend radius.

For comparison only, a circular 80 mm centreline has diameter 25.46 mm. That is not a universal minimum hole spacing: a supported noncircular routing must be checked against the 10 mm local bend-radius constraint. Two nearby drilled holes are not, on their own, evidence that this particular coil can be installed. The two channels must be checked simultaneously, including underside access, the board fixture and top-side cooling.

## Next-layout acceptance

1. Restore flat current conductors and remove both raised-link components from the proposed final revision.
2. Define the complete oriented surface enclosed by each installed coil and identify every copper current path crossing it on all four layers.
3. Show that the first coil senses QL1 current and the second QL2 current, without a parallel measured-current bypass or enclosed opposite power return.
4. Use matching geometries and compare their complete loops with the compact unsensed baseline. Any estimate must include plane detours, holes/vias and mutual coupling.
5. Check both windings, their actual free ends/closing heads and the 10 mm bend limit against a 3D installation path before assigning released drill coordinates.
6. Update the schematic, mechanical drawing, report and fabrication status together. Do not relabel old P7 Gerbers or its raised-link model as a hole-based design.

This document records the corrected design requirement and feasibility constraints. It is not a completed P8 PCB or a drilling release. No speculative holes have been added to the production copper.

Source: https://www.pemuk.com/uploads/files/dimension-drawings/CWTUM-Dimensions.pdf?v=1716722231 and the actual P5/P7 copper-zone definitions in scripts/build_p7_board.py.
