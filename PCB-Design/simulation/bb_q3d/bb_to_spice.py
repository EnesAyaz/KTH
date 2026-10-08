"""
Building-block Q3D exports -> LTspice subcircuits + summary.

    python simulation/bb_q3d/bb_to_spice.py

For results/<tag>_matrix.txt + <tag>_terminals.txt:
  results/<tag>.lib     .subckt <tag> <all terminals, sorted>: one R-L branch per Q3D source
                        (source -> net sink) and K lines for all mutual inductances (AC, 100 MHz)
  results/<tag>_L.csv   AC inductance matrix (nH)
  results/summary.json  effective loops / DC resistances used by the report
"""
import json
import math
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
F = 100e6
ESL = {"CapPL": 0.08e-9, "CapPR": 0.08e-9,                      # 6 x 0805, 0.48 nH each
       "CapB1P": 0.5e-9 / 8, "CapB2P": 0.5e-9 / 8, "CapB3P": 0.5e-9 / 8}   # 8 x 1210 per row, ~0.5 nH each


def block(lines, title):
    for i, line in enumerate(lines):
        if line.strip() == title:
            names = lines[i + 1].split()
            return names, np.array([[float(v) for v in r.split()[1:]] for r in lines[i + 2:i + 2 + len(names)]])
    raise ValueError(title)


def load(tag):
    lines = open(os.path.join(RES, tag + "_matrix.txt")).read().splitlines()
    names, L = block(lines, "AC Inductance Matrix")
    _, R = block(lines, "AC Resistance Matrix")
    _, Rdc = block(lines, "DC Resistance Matrix")
    sinks = {}
    for line in open(os.path.join(RES, tag + "_terminals.txt")):
        if line.strip() and not line.startswith("#"):
            p = line.split()
            sinks[p[0]] = p[1]
    branches = [(n.split(":")[1], sinks[n.split(":")[0]]) for n in names]
    return names, L, R, Rdc, branches


def solve(branches, L, R, shorts, inject, gnd):
    """Nodal analysis: coupled branches (Z = R + jwL), shorts (a, b, Lser), current injections {node: A}."""
    w = 2 * math.pi * F
    nodes = sorted({n for b in branches for n in b} | {n for s in shorts for n in s[:2]} | set(inject) | {gnd})
    idx = {n: i for i, n in enumerate([n for n in nodes if n != gnd])}
    nv, nb, ns = len(idx), len(branches), len(shorts)
    A = np.zeros((nv + nb + ns,) * 2, complex)
    rhs = np.zeros(nv + nb + ns, complex)
    Z = R + 1j * w * L
    for k, (a, b, *_) in enumerate(list(branches) + [s[:2] for s in shorts]):
        col = nv + k
        for node, sgn in ((a, 1.0), (b, -1.0)):
            if node in idx:
                A[idx[node], col] += sgn
                A[col, idx[node]] += sgn
        if k < nb:
            A[col, nv:nv + nb] -= Z[k]
        else:
            A[col, col] -= 1j * w * shorts[k - nb][2]
    for node, cur in inject.items():
        if node in idx:
            rhs[idx[node]] += cur
    x = np.linalg.solve(A, rhs)
    return {n: (x[i] if n != gnd else 0.0) for n, i in list(idx.items()) + [(gnd, None)]}


def write_lib(tag, names, L, R, branches):
    terms = sorted({t for b in branches for t in b})
    out = [".subckt %s %s" % (tag, " ".join(terms)),
           "* %s: Q3D copper partial R/L at 100 MHz; branches from each source terminal to its net sink" % tag]
    ln = []
    for k, (n, (a, b)) in enumerate(zip(names, branches)):
        out.append("R%d %s m%d %.6g" % (k + 1, a, k + 1, R[k, k]))
        out.append("L%d m%d %s %.6gn" % (k + 1, k + 1, b, L[k, k] * 1e9))
        ln.append("L%d" % (k + 1))
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            kij = L[i, j] / math.sqrt(L[i, i] * L[j, j])
            if abs(kij) > 1e-4:
                out.append("K%d_%d %s %s %.5f" % (i + 1, j + 1, ln[i], ln[j], kij))
    out.append(".ends %s" % tag)
    open(os.path.join(RES, tag + ".lib"), "w").write("\n".join(out) + "\n")
    with open(os.path.join(RES, tag + "_L.csv"), "w") as f:
        f.write("L_nH," + ",".join(names) + "\n")
        for n, row in zip(names, L):
            f.write(n + "," + ",".join("%.5f" % (v * 1e9) for v in row) + "\n")
    return terms


def main():
    summary = {}
    w = 2 * math.pi * F
    for tag in ("BB_PL", "BB_PL_2oz"):
        if not os.path.exists(os.path.join(RES, tag + "_matrix.txt")):
            continue
        names, L, R, Rdc, br = load(tag)
        L = L * 1e-9
        summary[tag + "_terminals"] = write_lib(tag, names, L, R, br)
        caps = [("CapPL", "CapNL"), ("CapPR", "CapNR"), ("CapB1P", "CapB1N"), ("CapB2P", "CapB2N"), ("CapB3P", "CapB3N")]
        res = {}
        for label, use in (("local_only", caps[:2]), ("local_and_bank", caps)):
            for esl_on in (False, True):
                shorts = [("QH_D_L", "QH_S_L", 0.0), ("QH_D_R", "QH_S_R", 0.0)] + \
                         [(p, n, ESL[p] if esl_on else 0.0) for p, n in use]
                # both low-side FETs switch together: 1 A into each QL port
                inj = {"QL_D_L": 1.0, "QL_S_L": -1.0, "QL_D_R": 1.0, "QL_S_R": -1.0}
                v = solve(br, L, np.zeros_like(R), shorts, inj, "QL_S_L")
                vl = v["QL_D_L"] - v["QL_S_L"]
                vr = v["QL_D_R"] - v["QL_S_R"]
                key = "%s_%s" % (label, "esl" if esl_on else "copper")
                res[key] = dict(L_cell_L_nH=(vl / w).imag * 1e9, L_cell_R_nH=(vr / w).imag * 1e9)
        summary[tag + "_loop"] = res
        # DC resistances of the load-current paths (two cells in parallel)
        rd = {n: Rdc[i, i] for i, n in enumerate(names)}
        R_hi = (rd["DCP:QH_D_L"] + rd["AC:QH_S_L"]) / 2
        R_lo = (rd["AC:QL_D_L"] + rd["DCN:QL_S_L"]) / 2
        summary[tag + "_Rdc"] = dict(per_branch=rd, R_high_path=R_hi, R_low_path=R_lo, names=names, matrix=Rdc.tolist())
        summary[tag + "_selfL_nH"] = {n: L[i, i] * 1e9 for i, n in enumerate(names)}
    if os.path.exists(os.path.join(RES, "BB_GL_matrix.txt")):
        names, L, R, Rdc, br = load("BB_GL")
        L = L * 1e-9
        summary["BB_GL_terminals"] = write_lib("BB_GL", names, L, R, br)
        # gate loop of each branch alone (other gate open) and with both driven
        res = {}
        for side in ("L", "R"):
            inj = {"Gate_%s" % side: -1.0, "Kelvin_%s" % side: 1.0}
            shorts = [("DrvOut", "DrvGnd", 0.0)]
            v = solve(br, L, np.zeros_like(R), shorts, inj, "DrvGnd")
            res["L_gate_%s_nH" % side] = ((v["Kelvin_%s" % side] - v["Gate_%s" % side]) / w).imag * 1e9
        inj = {"Gate_L": -1.0, "Kelvin_L": 1.0, "Gate_R": -1.0, "Kelvin_R": 1.0}
        v = solve(br, L, np.zeros_like(R), [("DrvOut", "DrvGnd", 0.0)], inj, "DrvGnd")
        res["L_gate_both_driven_nH"] = ((v["Kelvin_L"] - v["Gate_L"]) / w).imag * 1e9
        summary["BB_GL_loop"] = res
    with open(os.path.join(RES, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if "terminals" not in k and k != "BB_PL_Rdc"}, indent=1))
    if "BB_PL_Rdc" in summary:
        print("R_high_path %.3f mOhm, R_low_path %.3f mOhm" % (summary["BB_PL_Rdc"]["R_high_path"] * 1e3,
                                                               summary["BB_PL_Rdc"]["R_low_path"] * 1e3))


if __name__ == "__main__":
    main()
