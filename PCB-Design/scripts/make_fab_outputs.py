"""
Regenerate every fabrication output of the SPB building block from the KiCad sources.

    python scripts/make_fab_outputs.py

-> hardware/spb-bb-fab/fab/: Gerbers + job file, Excellon drill, pick-and-place CSV, STEP, assembly PDFs,
   schematic PDF, BOM CSV (from parts.json, written by make_kicad_bb_fab.py) and the spreader drawing.
"""
import collections
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "hardware", "spb-bb-fab")
FAB = os.path.join(D, "fab")
PCB = os.path.join(D, "spb-bb-fab.kicad_pcb")
SCH = os.path.join(D, "spb-bb-fab.kicad_sch")
CLI = r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"

MECH = [
    (1, "HS1", "Fan heatsink 40x40x50 mm, 12 V fan", "-", "Fischer Elektronik LAM 4 K 50 12 (0.65 K/W), Farnell 4708974"),
    (1, "HS1", "Heat spreader, Al 6061-T6, 42 x 14 x 3 mm, 2 pedestals 0.6 mm, 4 ears M2.5", "-",
     "machined, drawing spb-bb-fab-spreader-drawing.pdf"),
    (2, "HS1", "Insulating gap pad over each cell, 8 x 10 mm, 0.5 mm, >= 5 W/mK", "-",
     "Bergquist TGP 5000 (Gap Pad 5000S35) 0.020 in, cut to size, or equivalent"),
    (1, "HS1", "Thermal compound spreader to heatsink", "-", "non-conductive silicone paste"),
    (4, "H5-H8", "M2.5 x 10 screw + insulating shoulder washer (heatsink)", "-", "nylon or steel with insulating washer"),
    (4, "H1-H4", "M2.5 standoff + screw (board mounting)", "-", "insulated"),
    (2, "J1-J2", "M4 screw for REDCUBE DC terminals", "-", "Wuerth WP-THRBU M4"),
    (2, "J3-J4", "M4 screw for REDCUBE AC terminals", "-", "Wuerth WP-THRBU M4"),
]


def run(*args):
    r = subprocess.run([CLI] + list(args), capture_output=True, text=True)
    if r.returncode:
        sys.exit("kicad-cli %s failed:\n%s%s" % (args[:3], r.stdout, r.stderr))


def out(name):
    return os.path.join(FAB, name)


os.makedirs(FAB, exist_ok=True)
run("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "-o", FAB + os.sep, PCB)
run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--generate-map", "--map-format",
    "pdf", "-o", FAB + os.sep, PCB)
run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
    "-o", out("spb-bb-fab-pos.csv"), PCB)
run("pcb", "export", "pdf", "--layers", "F.Fab,F.SilkS,Edge.Cuts", "-o", out("spb-bb-fab-assembly-top.pdf"), PCB)
run("pcb", "export", "pdf", "--layers", "B.Fab,B.SilkS,Edge.Cuts", "--mirror", "-o",
    out("spb-bb-fab-assembly-bottom.pdf"), PCB)
run("pcb", "export", "step", "--subst-models", "-f", "-o", out("spb-bb-fab.step"), PCB)
run("sch", "export", "pdf", "-o", out("spb-bb-fab-schematic-revA.pdf"), SCH)

parts = json.load(open(os.path.join(D, "parts.json")))
groups = collections.OrderedDict()
for p in parts:
    if p["footprint"].startswith(("MountingHole", "Probe_", "HS_")):
        continue
    groups.setdefault((p["mpn"], p["footprint"]), [p["value"], []])[1].append(p["ref"])
with open(out("spb-bb-fab-bom.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Qty", "References", "Value", "Footprint", "Manufacturer part / note"])
    for (mpn, fp), (val, refs) in groups.items():
        w.writerow([len(refs), " ".join(refs), val, fp, mpn])
    w.writerow([])
    w.writerow(["Mechanical / thermal (not placed by the assembler)"])
    for row in MECH:
        w.writerow(row)
print("BOM: %d lines, %d placed parts" % (len(groups), sum(len(v[1]) for v in groups.values())))
subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_spreader_drawing.py")], check=True)
print("fab outputs written to", FAB)
