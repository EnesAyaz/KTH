"""
Read Q3D per-pass solution files (*.sd in <project>.aedtresults) and write a matrix file in the ExportMatrixData
layout used by revb_post.py, so that results are available before (or without) the end of a long adaptive solve.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\sd2matrix.py [ac_pass]
      -> results/BB_PL_REVB_matrix.txt, BB_PL_REVB_terminals.txt (ac_pass: SOL..._MACL<k>; default: latest)

Terminal IDs: Q3D numbers the source terminals in the order they were assigned (bb_q3d_revb.py assigns sources first,
in the order of revb_geometry.json), starting after the nets; the ID offset is taken from the smallest ID.
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
RD = glob.glob(os.path.join(RES, "bb_q3d_revb.aedtresults", "*.results"))[0]
G = json.load(open(os.path.join(RES, "revb_geometry.json")))
sources = [t for t in G["terminals"] if t[0] == "Source"]
sinks = {t[2]: t[1] for t in G["terminals"] if t[0] == "Sink"}


def read_sd(path):
    txt = open(path).read()
    ids = [int(v) for v in re.search(r"Names\(([^)]*)\)", txt).group(1).split(",")]
    rows = re.findall(r"\$begin 'r\d+'(.*?)\$end", txt, re.S)
    M = np.array([[float(v) for v in re.findall(r"c\(([-\d.e+]+)\)", r)] for r in rows])
    return ids, M


def pick(kind, k=None):
    pats = sorted(glob.glob(os.path.join(RD, "*_SOL*_%s*.sd" % kind)), key=os.path.getmtime)
    if k is not None:
        pats = [p for p in pats if re.search(r"_%s%d_" % (kind, k), p)] or pats
    return pats[-1]


ac_pass = int(sys.argv[1]) if len(sys.argv) > 1 else None
files = {"AC Inductance Matrix": pick("MACL", ac_pass), "AC Resistance Matrix": pick("MADCR", ac_pass),
         "DC Inductance Matrix": pick("MDCL"), "DC Resistance Matrix": pick("MDCR")}
out = ["# from Q3D solution files: " + ", ".join(os.path.basename(f) for f in files.values())]
names = None
for title, f in files.items():
    ids, M = read_sd(f)
    off = min(ids)
    nm = ["%s:%s" % (sources[i - off][2], sources[i - off][1]) for i in ids]
    names = nm
    scale = 1e9 if "Inductance" in title else 1.0
    out += ["", title, " ".join(nm)]
    out += ["%s %s" % (n, " ".join("%.6g" % (v * scale) for v in row)) for n, row in zip(nm, M)]
open(os.path.join(RES, "BB_PL_REVB_matrix.txt"), "w").write("\n".join(out) + "\n")
with open(os.path.join(RES, "BB_PL_REVB_terminals.txt"), "w") as fo:
    for net, sink in sorted(sinks.items()):
        fo.write("%s %s %s\n" % (net, sink, " ".join(s[1] for s in sources if s[2] == net)))
print("written from", [os.path.basename(f) for f in files.values()])
