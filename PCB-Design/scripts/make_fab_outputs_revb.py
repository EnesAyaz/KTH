"""
Fabrication outputs of the final Rev B boards and the PCB busbar from the KiCad sources:

    python scripts/make_fab_outputs_revb.py
-> hardware/<board>/fab/ for spb-bb-revb-dpt, spb-bb-revb-load, spb-busbar: Gerbers + job file, Excellon drill +
   map, pick-and-place CSV, STEP (origin = leg centre / centre leg), assembly PDFs, schematic PDF (leg boards), BOM CSV
   (placed parts from parts.json + the mechanical items below), and a zip of the Gerber/drill set for the fab house.
"""
import collections
import csv
import glob
import json
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
ORIGIN = {"spb-bb-revb-dpt": "150x100mm", "spb-bb-revb-load": "150x100mm", "spb-busbar": "160x80mm"}
NOTE = {
    "spb-bb-revb-dpt": "4 layers, 1.6 mm FR4, 2 oz (70 um) on all layers, L1-L2 and L3-L4 prepreg 0.1 mm, ENIG; "
                       "filled + capped via-in-pad (SHLD pads); double-pulse board (UFCS shunts, no heatsink)",
    "spb-bb-revb-load": "4 layers, 1.6 mm FR4, 2 oz (70 um) on all layers, L1-L2 and L3-L4 prepreg 0.1 mm, ENIG; "
                        "BLIND vias L1-L2 (0.25 mm drill) filled + capped in the LS source pads; load-test board",
    "spb-busbar": "4 layers, 1.6 mm FR4, 2 oz on all layers (JLC3313 stack-up), ENIG, bolt pads without mask",
}
MECH = {
    "spb-bb-revb-dpt": [
        (2, "J1-J2", "M4 x 8 screw + washer into REDCUBE (to the DC source / busbar)", "-", "steel, A2"),
        (1, "J22", "M6 x 16 bolt + nut + 2 washers, AC bolt pad", "-", "steel, A2"),
        (1, "J22", "AC bar 12 x 5 mm Cu, M6 hole, length to the load inductor", "-", "Cu-ETP, tin plated"),
        (4, "H1-H4", "M2.5 standoff + screw (board mounting)", "-", "nylon / insulated"),
        (4, "RS1-RS4", "PMK UFCS-R001 hand-soldered at the blade (short IN land), SMA cable to the scope", "-",
         "PMK UFCS-R001"),
    ],
    "spb-bb-revb-load": [
        (1, "HS1", "Fan heatsink 40 x 40 x 50 mm, 12 V fan", "-", "Fischer Elektronik LAM 4 K 50 12 (0.65 K/W), "
                                                                 "Farnell 4708974"),
        (1, "HS1", "Heat spreader Al 6061, 89.5 x 12.8 x 3 mm, 4 pedestals 5.6 x 7.7 x 0.6 mm over the cells, "
                   "3 x M2.5 (H5-H7)", "-", "machined"),
        (4, "HS1", "Insulating gap pad over each cell, 5.6 x 7.7 mm, 0.5 mm, >= 5 W/mK", "-",
         "Bergquist TGP 5000 0.020 in, cut to size, or equivalent"),
        (3, "H5-H7", "M2.5 x 10 screw + insulating shoulder washer (spreader)", "-", "nylon or steel + washer"),
        (4, "H1-H4", "M2.5 standoff + screw (H3/H4: nylon M2.5 x 6.5 mm onto the busbar)", "-", "nylon"),
        (2, "J1-J2", "M4 x 8 screw + washer from below through the busbar into the REDCUBE", "-", "steel, A2"),
        (1, "J22", "M6 x 16 bolt + nut + 2 washers, AC bolt pad", "-", "steel, A2"),
        (1, "J22", "AC bar 12 x 5 mm Cu through a LEM HO 250-S", "-", "Cu-ETP + LEM HO 250-S"),
    ],
    "spb-busbar": [
        (6, "J1-J6", "M4 x 8 screw + washer into the leg REDCUBE terminals", "-", "steel, A2"),
        (6, "H1-H6", "nylon standoff M2.5 x 6.5 mm (leg H3/H4)", "-", "nylon"),
        (4, "H7-H10", "M3 insulating standoff to the frame (8 mm Cu keep-out, 1200 V)", "-", "PA66 / ceramic"),
        (2, "J7-J8", "M6 ring lug + Cu braid to the level above / below, M6 bolt + nut", "-", "Cu, tin plated"),
    ],
}


def run(*args):
    r = subprocess.run([CLI] + list(args), capture_output=True, text=True)
    if r.returncode:
        sys.exit("kicad-cli %s failed:\n%s%s" % (args[:3], r.stdout, r.stderr))


for name in ("spb-bb-revb-dpt", "spb-bb-revb-load", "spb-busbar"):
    D = os.path.join(ROOT, "hardware", name)
    FAB = os.path.join(D, "fab")
    GB = os.path.join(FAB, "gerber")
    os.makedirs(GB, exist_ok=True)
    PCB = os.path.join(D, name + ".kicad_pcb")
    SCH = os.path.join(D, name + ".kicad_sch")
    out = lambda n: os.path.join(FAB, n)                       # noqa: E731
    run("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "-o", GB + os.sep, PCB)
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--generate-map", "--map-format",
        "pdf", "-o", GB + os.sep, PCB)
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--use-drill-file-origin",
        "-o", out(name + "-pos.csv"), PCB)
    run("pcb", "export", "pdf", "--layers", "F.Fab,F.SilkS,Edge.Cuts", "-o", out(name + "-assembly-top.pdf"), PCB)
    run("pcb", "export", "pdf", "--layers", "B.Fab,B.SilkS,Edge.Cuts", "--mirror", "-o",
        out(name + "-assembly-bottom.pdf"), PCB)
    run("pcb", "export", "step", "--subst-models", "-f", "--user-origin", ORIGIN[name], "-o", out(name + ".step"), PCB)
    if os.path.exists(SCH):
        run("sch", "export", "pdf", "-o", out(name + "-schematic.pdf"), SCH)
    with zipfile.ZipFile(out(name + "-gerber.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(os.path.join(GB, "*"))):
            if not f.endswith(".pdf"):
                z.write(f, os.path.basename(f))
    parts = json.load(open(os.path.join(D, "parts.json")))
    groups = collections.OrderedDict()
    for p in parts:
        if p["footprint"].startswith(("MountingHole", "HS_", "BUS_", "AC_BOLT")):
            continue
        groups.setdefault((p["mpn"], p["footprint"], p["value"].startswith("DNP")), [p["value"], []])[1].append(p["ref"])
    with open(out(name + "-bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# " + NOTE[name]])
        w.writerow(["Qty", "References", "Value", "Footprint", "Manufacturer part / note", "Fit"])
        for (mpn, fp, dnp), (val, refs) in groups.items():
            w.writerow([len(refs), " ".join(sorted(refs)), val, fp, mpn, "DNP" if dnp else "fit"])
        w.writerow([])
        w.writerow(["Mechanical (not placed by the assembler)"])
        for row in MECH[name]:
            w.writerow(row)
    print("%s: BOM %d lines, %d placed parts -> %s" % (name, len(groups), sum(len(v[1]) for v in groups.values()),
                                                         FAB))
