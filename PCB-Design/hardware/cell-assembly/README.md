# SPB cell assembly (Autodesk Fusion)

One SPB cell (submodule, 75 V): three leg boards under one long liquid cold plate, laminated DC busbar, phase
leads and the cell aux/control board. Concept level, for packaging, cooling and busbar studies. Not for manufacture.

## Run

1. Export the leg board, if it changed:
   `kicad-cli pcb export step --subst-models --force -o hardware/spb-building-block/spb-building-block.step hardware/spb-building-block/spb-building-block.kicad_pcb`
   (set `KICAD7_3DMODEL_DIR` to the KiCad 3D model folder first). The board itself comes from `scripts/make_kicad_bb.py`.
2. In Fusion: **Utilities > Add-Ins > Scripts and Add-Ins > Scripts > "+"**, select the folder `SPB_Cell_Assembly`, then **Run**.
   The script opens a new design (direct modelling) and builds the assembly in about a minute.

## Contents (components in the browser)

| Component | What it is |
|---|---|
| Leg boards | KiCad STEP of the leg board, three instances at a 36 mm pitch (x = axial direction) |
| Transistors and drivers | EPC2361 and 2EDF7275K as boxes (their KiCad models are VRML only, so they are not in the STEP) |
| Cold plate | Al plate, 8 mm, at z = 6 mm above the board bottom. U-shaped channel (8 x 3 mm) under the FETs and back under the MLCC bank. Inlet and outlet at one end. Pedestals over each FET pair and each bank, each tipped with an AlN tile (0.63 mm) and a 0.3 mm TIM pad |
| Insulated standoffs | PEEK spacers and M2.5 PEEK screws at the four corner holes of every leg |
| Laminated DC busbar | Bottom side, under the DC terminal zone. DC+ copper (1.5 mm) on the terminal faces, 0.25 mm insulation film, DC- copper (1.5 mm) with raised bosses through clearance holes to the DC- terminals. M4 screws, and series tabs at both ends (to SM k-1 and SM k+1) |
| Phase leads | 8 x 2 mm copper bars from each AC terminal. Each drops to its own depth, then jogs to a common lane and runs axially to the end winding |
| Cell aux and control board | 75 V to 12 V buck, three isolated 6 V supplies for the high-side drivers, MCU, fibre transceiver, and FFC cables to each leg (J4) |
| Motor housing segment | Insulation sheet and a flat stand-in for the stator jacket |

All dimensions are in the `P` dictionary at the top of `SPB_Cell_Assembly.py`.

## Open points

- Channel cross-section and flow: check with Icepak or CFD. The cell loss is about 38 W.
- Busbar thickness and stack-up: extract in Q3D. The busbar inductance replaces the 20 nH assumption in the LTspice model.
- Creepage and clearance to the grounded plate and the housing: AlN overhang, busbar and lead insulation.
