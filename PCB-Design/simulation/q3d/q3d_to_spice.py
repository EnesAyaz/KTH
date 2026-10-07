"""
Q3D matrix exports -> LTspice subcircuits, inductance-matrix CSVs, effective loop inductance.

    python simulation/q3d/q3d_to_spice.py

For every results/<tag>_matrix.txt (+ <tag>_terminals.txt from q3d_dpt_cell.py):
  results/<tag>.lib        .subckt with one R-L branch per Q3D source (source -> net sink)
                           and K statements for every mutual inductance (AC, 100 MHz)
  results/<tag>_L.csv      AC partial inductance matrix (nH), rows/cols = net:source
  results/<tag>_test.cir   LTspice AC test: QH and MLCC banks shorted, 1 A into the QL port
  results/summary.csv      effective loop L at the QL switch, copper only and with MLCC ESL

The effective loop is solved by nodal analysis of the coupled branches, so it is
correct for parallel banks (scenario C) where summing the matrix is not.
"""
import glob
import math
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
F = 100e6                 # Q3D adaptive / matrix frequency
ESL_BANK = 0.48e-9 / 6    # 6 x TDK C2012X7S2A105K125AB, simple-model ESL in parallel


def read_block(lines, title):
    for i, line in enumerate(lines):
        if line.strip() == title:
            names = lines[i + 1].split()
            rows = [[float(v) for v in r.split()[1:]] for r in lines[i + 2:i + 2 + len(names)]]
            return names, np.array(rows)
    raise ValueError("block %r not found" % title)


def read_terminals(tag):
    sinks = {}
    for line in open(os.path.join(RES, tag + "_terminals.txt")):
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        sinks[parts[0]] = parts[1]
    return sinks


def bank_pairs(terms):
    """MLCC banks = (CapXP, CapXN) terminal pairs present in the design."""
    pairs = []
    for t in terms:
        m = re.match(r"Cap(\w*)P$", t)
        if m and "Cap%sN" % m.group(1) in terms:
            pairs.append(("Cap%sP" % m.group(1), "Cap%sN" % m.group(1)))
    return pairs


def loop_inductance(branches, lmat, rmat, shorts, port):
    """branches: [(node_from, node_to)], shorts: [(a, b, L_series)], port: (p, n).
    Returns complex input impedance at the port at F."""
    w = 2 * math.pi * F
    nodes = sorted({n for b in branches for n in b} | {n for s in shorts for n in s[:2]} | set(port))
    gnd = port[1]
    idx = {n: i for i, n in enumerate([n for n in nodes if n != gnd])}
    nv, nb, ns = len(idx), len(branches), len(shorts)
    N = nv + nb + ns
    A = np.zeros((N, N), complex)
    rhs = np.zeros(N, complex)
    Z = rmat + 1j * w * lmat

    def kcl(node, col, sign):
        if node in idx:
            A[idx[node], col] += sign

    for k, (a, b) in enumerate(branches):
        col = nv + k
        kcl(a, col, 1.0)
        kcl(b, col, -1.0)
        if a in idx:
            A[col, idx[a]] += 1.0
        if b in idx:
            A[col, idx[b]] -= 1.0
        A[col, nv:nv + nb] -= Z[k]
    for m, (a, b, ls) in enumerate(shorts):
        col = nv + nb + m
        kcl(a, col, 1.0)
        kcl(b, col, -1.0)
        if a in idx:
            A[col, idx[a]] += 1.0
        if b in idx:
            A[col, idx[b]] -= 1.0
        A[col, col] -= 1j * w * ls
    rhs[idx[port[0]]] = 1.0          # 1 A injected into the port + node
    x = np.linalg.solve(A, rhs)
    return x[idx[port[0]]]


def convert(tag):
    lines = open(os.path.join(RES, tag + "_matrix.txt")).read().splitlines()
    names, lmat_nh = read_block(lines, "AC Inductance Matrix")
    _, rmat = read_block(lines, "AC Resistance Matrix")
    sinks = read_terminals(tag)
    lmat = lmat_nh * 1e-9
    branches = [(n.split(":")[1], sinks[n.split(":")[0]]) for n in names]
    terms = sorted({t for b in branches for t in b})
    banks = bank_pairs(terms)
    sub = re.sub(r"[^A-Za-z0-9_]", "_", tag)

    # ---- LTspice subcircuit
    out = [".subckt %s %s" % (sub, " ".join(terms)),
           "* %s: Q3D AC partial R/L of the copper at 100 MHz (components are not included)" % tag,
           "* branches run from each Q3D source terminal to its net's sink terminal"]
    lnames = []
    for k, (n, (a, b)) in enumerate(zip(names, branches)):
        ln = "L%d_%s" % (k + 1, n.replace(":", "_"))
        out.append("R%d %s m%d %.6g" % (k + 1, a, k + 1, rmat[k, k]))
        out.append("%s m%d %s %.6gn" % (ln, k + 1, b, lmat_nh[k, k]))
        lnames.append(ln)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            kij = lmat_nh[i, j] / math.sqrt(lmat_nh[i, i] * lmat_nh[j, j])
            if abs(kij) > 1e-6:
                out.append("K%d_%d %s %s %.6f" % (i + 1, j + 1, lnames[i], lnames[j], kij))
    out.append(".ends %s" % sub)
    open(os.path.join(RES, tag + ".lib"), "w").write("\n".join(out) + "\n")

    # ---- inductance matrix CSV
    with open(os.path.join(RES, tag + "_L.csv"), "w") as f:
        f.write("L_nH," + ",".join(names) + "\n")
        for n, row in zip(names, lmat_nh):
            f.write(n + "," + ",".join("%.6f" % v for v in row) + "\n")

    # ---- effective loop at the QL switch: QH shorted, banks shorted (ideal / with ESL)
    port = ("QL_D", "QL_S")
    zero = np.zeros_like(rmat)
    res = {}
    for label, esl in (("copper", 0.0), ("with_esl", ESL_BANK)):
        shorts = [("QH_D", "QH_S", 0.0)] + [(p, n, esl) for p, n in banks]
        zin = loop_inductance(branches, lmat, zero, shorts, port)
        res[label] = zin.imag / (2 * math.pi * F) * 1e9
    zin_r = loop_inductance(branches, lmat, rmat, [("QH_D", "QH_S", 0.0)] + [(p, n, 0.0) for p, n in banks], port)
    res["R_mohm"] = zin_r.real * 1e3

    # ---- LTspice verification netlist
    pins = " ".join(terms)
    cir = ["* %s: LTspice check of the effective loop inductance (copper only)" % tag,
           ".include %s.lib" % tag,
           "X1 %s %s" % (pins, sub),
           "Vqh QH_D QH_S 0"]
    for p, n in banks:
        cir.append("V%s %s %s 0" % (p, p, n))
    cir += ["I1 QL_S QL_D AC 1", "Rref QL_S 0 1G",
            ".options meascplxfmt=cartesian",
            ".ac lin 1 100Meg 100Meg",
            ".meas AC Lloop_nH FIND im(V(QL_D,QL_S))/(2*pi*frequency)*1e9 AT 100Meg",
            ".end"]
    open(os.path.join(RES, tag + "_test.cir"), "w").write("\n".join(cir) + "\n")
    return tag, res, len(banks)


def main():
    rows = [convert(os.path.basename(p)[:-len("_matrix.txt")])
            for p in sorted(glob.glob(os.path.join(RES, "*_matrix.txt")))
            if os.path.exists(p.replace("_matrix.txt", "_terminals.txt"))]
    with open(os.path.join(RES, "summary.csv"), "w") as f:
        f.write("design,banks,Lloop_copper_nH,Lloop_with_MLCC_ESL_nH,Rloop_100MHz_mohm\n")
        for tag, r, nb in rows:
            f.write("%s,%d,%.4f,%.4f,%.3f\n" % (tag, nb, r["copper"], r["with_esl"], r["R_mohm"]))
            print("%-24s banks=%d  Lloop copper %.3f nH, with MLCC ESL %.3f nH, R %.2f mOhm"
                  % (tag, nb, r["copper"], r["with_esl"], r["R_mohm"]))


if __name__ == "__main__":
    main()
