# Fabrication review files - release on hold

These files were exported from the integrated P6 PCB on 22 September 2026. They are for quotation and engineering review, not an instruction to manufacture.

Verified: zero final KiCad DRC violations, zero unconnected pads, 223 connected schematic pin assignments, and separate D_QL1 drain island joined through LK1. Four mechanical holes and the split-spreader envelope are integrated.

Before an order: approve the named four-layer stackup and 2 oz fine-pitch etching/stencil process; finish the formed-link and CWTUM closing-head fit; qualify support stiffness, insulating TIM compression and the cooling interface; select and qualify mating power connectors. The mechanical model is an envelope, not a machining drawing. Native ERC has not been run and the custom passive symbols limit its coverage.

Use the explicit PTH and NPTH files in separate-drills, with their SVG drill maps. The original combined MixedPlating drill file is retained only as a comparison export; do not submit both sets as separate drilling operations. The NPTH set must contain four 2.4 mm mounting holes and two 3.2 mm output-current access holes. Verify hole tolerances, layer order, copper polarity and solder-mask artwork against the PCB before release. The proposed surface finish is ENIG and is now recorded in the board/job metadata; supplier process acceptance is still required. The 3D model is not manufacturing authority.

See ../verification.json, ../final-drc.rpt, ../device-current-audit.json and ../../../docs/p6-mechanical-review.md. The report is ../../../output/pdf/epc2361-p6-report.pdf.
