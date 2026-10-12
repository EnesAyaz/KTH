"""
Pad nets of a board for the schematic generators and check_sch_vs_pcb.py.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\dump_pad_nets.py [spb-bb-fab | spb-bb-revb]
      -> hardware/<board>/pad_nets.json
"""
import json
import os
import sys

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-fab"
b = pcbnew.LoadBoard(os.path.join(ROOT, "hardware", name, name + ".kicad_pcb"))
out = []
for fp in sorted(b.GetFootprints(), key=lambda f: (f.GetReference()[0],
                                                     int("".join(c for c in f.GetReference() if c.isdigit()) or 0))):
    pads = {}
    for p in fp.Pads():
        if p.GetNumber():
            pads.setdefault(p.GetNumber(), p.GetNetname())
    out.append((fp.GetReference(), fp.GetValue(), pads))
json.dump(out, open(os.path.join(ROOT, "hardware", name, "pad_nets.json"), "w"), indent=0)
print(name, len(out), "footprints")
