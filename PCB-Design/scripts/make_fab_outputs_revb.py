"""
Fabrication outputs of the final Rev B boards and the PCB busbar from the KiCad sources:

    python scripts/make_fab_outputs_revb.py [board ...]        (default: all three)
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
                       "filled + capped via-in-pad (list in gerber/*-fab-notes.txt: shunt SHLD and bypass-capacitor pads); double-pulse board (UFCS shunts, no heatsink); IPC class 2; "
                       "solder mask over all copper and ALL vias tented (the 1200 V control/power barrier relies on it)",
    "spb-bb-revb-load": "4 layers, 1.6 mm FR4, 2 oz (70 um) on all layers, L1-L2 and L3-L4 prepreg 0.1 mm, ENIG; "
                        "BLIND vias L1-L2 (0.25 mm drill) filled + capped in the LS source pads; load-test board; IPC class 2; "
                        "solder mask over all copper and ALL vias tented (the 1200 V control/power barrier relies on it)",
    "spb-busbar": "4 layers, 1.6 mm FR4, 2 oz on all layers (JLC3313 stack-up), ENIG, bolt pads without mask",
}
MECH = {
    "spb-bb-revb-dpt": [
        (2, "J1-J2", "M4 x 8 screw + washer into REDCUBE (to the DC source / busbar)", "-", "steel, A2"),
        (1, "{AC}", "M6 x 16 bolt + nut + 2 washers, AC bolt pad", "-", "steel, A2"),
        (1, "{AC}", "AC bar 12 x 5 mm Cu, M6 hole, length to the load inductor", "-", "Cu-ETP, tin plated"),
        (4, "H1-H4", "M2.5 standoff + screw (board mounting)", "-", "nylon / insulated"),
        (2, "J5, J14", "Control cable: 2 x 5 IDC socket + ribbon (each signal next to its own return)", "-",
         "2.54 mm IDC, e.g. Wurth 61201021621"),
    ],
    "spb-bb-revb-load": [
        (1, "HS1", "Fan heatsink 40 x 40 x 50 mm, 12 V fan", "-", "Fischer Elektronik LAM 4 K 50 12 (0.65 K/W), "
                                                                 "Farnell 4708974"),
        (1, "HS1", "Fan supply: 12 V from the bench supply (no fan header on the board: 1200 V barrier)", "-", "-"),
        (2, "J5, J14", "Control cable: 2 x 5 IDC socket + ribbon (each signal next to its own return)", "-",
         "2.54 mm IDC, e.g. Wurth 61201021621"),
        (1, "HS1", "Heat spreader Al 6061, 89.5 x 12.8 x 3 mm, 4 pedestals 5.6 x 7.7 x 0.6 mm over the cells, "
                   "3 x M2.5 (H5-H7)", "-", "machined"),
        (4, "HS1", "Insulating gap pad over each cell, 5.6 x 7.7 mm, 0.5 mm, >= 5 W/mK", "-",
         "Bergquist TGP 5000 0.020 in, cut to size, or equivalent"),
        (3, "H5-H7", "M2.5 x 10 screw + insulating shoulder washer (spreader)", "-", "nylon or steel + washer"),
        (4, "H1-H4", "M2.5 standoff + screw (H3/H4: nylon M2.5 x 6.5 mm onto the busbar)", "-", "nylon"),
        (2, "J1-J2", "M4 x 8 screw + washer from below through the busbar into the REDCUBE", "-", "steel, A2"),
        (1, "{AC}", "M6 x 16 bolt + nut + 2 washers, AC bolt pad", "-", "steel, A2"),
        (1, "{AC}", "AC bar 12 x 5 mm Cu through a LEM HO 250-S", "-", "Cu-ETP + LEM HO 250-S"),
    ],
    "spb-busbar": [
        (6, "J1-J6", "M4 x 8 screw + washer into the leg REDCUBE terminals", "-", "steel, A2"),
        (6, "H1-H6", "nylon standoff M2.5 x 6.5 mm (leg H3/H4)", "-", "nylon"),
        (4, "H7-H10", "M3 insulating standoff to the frame (8 mm Cu keep-out, 1200 V)", "-", "PA66 / ceramic"),
        (2, "J7-J8", "M6 ring lug + Cu braid to the level above / below, M6 bolt + nut", "-", "Cu, tin plated"),
    ],
}


# fab notes / drawing that travel inside the Gerber zip (fabrication review F1/F2)
STACK = [("L1 F.Cu", "copper", "70 um (2 oz) finished", "signal + power, ENIG"),
         ("", "prepreg", "0.10 mm", "FR4, er ~4.2 (sets the L1-L2 loop spacing: keep)"),
         ("L2 In1.Cu", "copper", "70 um", "DC- return plane"),
         ("", "core", "~1.1 mm (fab adjusts for 1.60 mm total)", "FR4, Tg >= 150 C"),
         ("L3 In2.Cu", "copper", "70 um", "DC+ / AC / gate"),
         ("", "prepreg", "0.10 mm", "FR4 (sets the L3-L4 spacing: keep)"),
         ("L4 B.Cu", "copper", "70 um (2 oz) finished", "signal + power, ENIG")]
RULES_TXT = ["Minimum track / space: 0.20 / 0.20 mm (functional clearance between domains 0.20 mm at 75 V)",
             "Minimum via: 0.45 mm pad, 0.25 mm finished drill, annular ring >= 0.10 mm",
             "Hole-to-hole 0.25 mm, copper to board edge 0.30 mm, solder-mask web >= 0.10 mm",
             "1200 V control/power barrier: 4.0 mm outer / 3.0 mm inner copper keep-out (do not reduce)",
             "Solder mask green both sides, white silk both sides, ENIG finish, IPC-6012 class 2, electrical test 100 %",
             "ALL vias tented both sides (the barrier relies on it), EXCEPT the via-in-pad list below: IPC-4761 type VII "
             "(filled with non-conductive epoxy + copper capped, planarised)",
             "Drill files: PTH and NPTH separate (Excellon, mm, absolute origin = drill origin)"]


def fab_notes(name, D, GB):
    vip = os.path.join(D, "fab", "via_in_pad.csv")
    rows = list(csv.reader(open(vip)))[1:] if os.path.exists(vip) else []
    L = ["FABRICATION NOTES - %s (generated by scripts/make_fab_outputs_revb.py)" % name, "",
         "Board: " + NOTE[name], "", "STACK-UP (4 layers, 1.60 mm +-10 %, top to bottom)"]
    L += ["  %-10s %-8s %-38s %s" % r for r in STACK]
    L += ["", "RULES / PROCESS"] + ["  - " + r for r in RULES_TXT]
    L += ["", "VIA-IN-PAD (filled + capped, type VII): %d vias in %d pads" % (len(rows), len(set(r[5] for r in rows)))]
    L += ["  %-8s %-8s %-6s %-6s %-8s %s" % ("x mm", "y mm", "drill", "dia", "net", "pad")]
    L += ["  %-8s %-8s %-6s %-6s %-8s %s" % tuple(r) for r in rows]
    txt = "\n".join(L) + "\n"
    with open(os.path.join(GB, name + "-fab-notes.txt"), "w") as f:
        f.write(txt)
    return len(rows)


def run(*args):
    r = subprocess.run([CLI] + list(args), capture_output=True, text=True)
    if r.returncode:
        sys.exit("kicad-cli %s failed:\n%s%s" % (args[:3], r.stdout, r.stderr))


for name in sys.argv[1:] or ("spb-bb-revb-dpt", "spb-bb-revb-load", "spb-busbar"):
    D = os.path.join(ROOT, "hardware", name)
    FAB = os.path.join(D, "fab")
    GB = os.path.join(FAB, "gerber")
    os.makedirs(GB, exist_ok=True)
    PCB = os.path.join(D, name + ".kicad_pcb")
    SCH = os.path.join(D, name + ".kicad_sch")
    out = lambda n: os.path.join(FAB, n)                       # noqa: E731
    run("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask", "-o", GB + os.sep, PCB)
    for f in glob.glob(os.path.join(GB, "*.drl")) + glob.glob(os.path.join(GB, "*drl_map.pdf")):
        os.remove(f)                                           # stale combined drill files from before the split
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--excellon-separate-th",
        "--generate-map", "--map-format", "pdf", "-o", GB + os.sep, PCB)
    n_vip = fab_notes(name, D, GB) if name in NOTE else 0
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--use-drill-file-origin",
        "-o", out(name + "-pos.csv"), PCB)
    with open(out(name + "-pos.csv")) as f:                    # lab-fitted parts are not in the assembler's file
        pos = [r for r in f if not r.startswith('"RS')]
    with open(out(name + "-pos.csv"), "w") as f:
        f.writelines(pos)
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
        groups.setdefault((p["mpn"], p["footprint"], p["value"], p["value"].startswith("DNP")),
                          [p["value"], []])[1].append(p["ref"])
    with open(out(name + "-bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# " + NOTE[name]])
        w.writerow(["Qty", "References", "Value", "Footprint", "Manufacturer part / note", "Fit"])
        for (mpn, fp, _v, dnp), (val, refs) in groups.items():
            lab = all(r.startswith("RS") for r in refs)
            w.writerow([len(refs), " ".join(sorted(refs, key=lambda r: (r.rstrip("0123456789"), int("0" + r.lstrip(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"))))), val, fp, mpn,
                "NOT by the assembler: hand-soldered in the lab at the blade (short IN land), SMA cable to the scope"
                if lab else ("DNP" if dnp else "fit")])
        w.writerow([])
        w.writerow(["Mechanical (not placed by the assembler)"])
        ac = [p["ref"] for p in parts if p["value"] == "AC"]          # AC bolt reference from the board itself
        for row in MECH[name]:
            w.writerow([str(c).replace("{AC}", ac[0] if ac else "AC bolt") for c in row])
    tp = os.path.join(FAB, "testpoints.csv")
    print("%s: BOM %d lines, %d placed parts, %d via-in-pad, test-point list %s -> %s"
          % (name, len(groups), sum(len(v[1]) for v in groups.values()), n_vip,
             "yes" if os.path.exists(tp) else "MISSING", FAB))
