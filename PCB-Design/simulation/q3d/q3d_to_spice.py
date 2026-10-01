"""
Convert Q3D *_matrix.txt exports into LTspice subcircuits and a summary table.

    python simulation/q3d/q3d_to_spice.py

For every results/<design>_matrix.txt this writes results/<design>.lib with
one series R-L branch per copper net (source terminal -> sink terminal) and a
K statement for every mutual inductance (AC values at the Q3D frequency).
Connect the component models (MLCC bank, EPC2361, shunt) between the
terminals in LTspice, as with "Export Circuit" in the busbar model.
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")

# net -> (source terminal, sink terminal), as defined in q3d_dpt_cell.py
TERMINALS = {
    "DCP": ("CapP", "QH_D"),
    "AC": ("QH_S", "QL_D"),
    "SQL": ("QL_S", "SH_in"),
    "G": ("DrvOut", "Gate"),
    "KS": ("Kelvin", "DrvGnd"),
}


def sink_of(net, src):
    if net == "DCN":
        return "CapN"  # DCN source is SH_out (shunt design) or QL_S (no shunt)
    return TERMINALS[net][1]


def read_block(lines, title):
    """Return (names, matrix) of the first block whose header equals title."""
    for i, line in enumerate(lines):
        if line.strip() == title:
            names = lines[i + 1].split()
            rows = []
            for row in lines[i + 2:i + 2 + len(names)]:
                parts = row.split()
                rows.append([float(v) for v in parts[1:]])
            return names, rows
    raise ValueError("block %r not found" % title)


def convert(path):
    lines = open(path).read().splitlines()
    freq = next((l.split(":", 1)[1].strip() for l in lines if l.startswith("Frequency")), "?")
    names, lmat = read_block(lines, "AC Inductance Matrix")
    _, rmat = read_block(lines, "AC Resistance Matrix")
    design = os.path.basename(path)[:-len("_matrix.txt")]
    sub = re.sub(r"[^A-Za-z0-9_]", "_", design)
    pins = []
    out = ["* %s: Q3D AC partial inductance (nH) / resistance at %s" % (design, freq),
           "* Copper only. Add MLCC ESL, EPC2361 package and shunt between the terminals.",
           ""]
    branches = []
    for k, term in enumerate(names):
        net, src = term.split(":")
        snk = sink_of(net, src)
        pins += [src, snk]
        mid = "%s_m" % net
        out.append("R_%s %s %s %.6g" % (net, src, mid, rmat[k][k]))
        out.append("L_%s %s %s %.6gn" % (net, mid, snk, lmat[k][k]))
        branches.append("L_%s" % net)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            kab = lmat[a][b] / math.sqrt(lmat[a][a] * lmat[b][b])
            out.append("K_%s_%s %s %s %.6f" % (branches[a][2:], branches[b][2:],
                                               branches[a], branches[b], kab))
    loop = sum(sum(r) for r in lmat)
    out.insert(0, ".subckt %s %s" % (sub, " ".join(pins)))
    out.append(".ends %s" % sub)
    open(os.path.join(RES, design + ".lib"), "w").write("\n".join(out) + "\n")
    return design, loop, names, lmat


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(RES, "*_matrix.txt"))):
        design, loop, names, lmat = convert(path)
        selfs = ", ".join("%s %.3f" % (n.split(":")[0], lmat[i][i]) for i, n in enumerate(names))
        rows.append((design, loop, selfs))
    with open(os.path.join(RES, "summary.csv"), "w") as f:
        f.write("design,Lloop_nH,self_inductances_nH\n")
        for design, loop, selfs in rows:
            f.write('%s,%.4f,"%s"\n' % (design, loop, selfs))
    for design, loop, selfs in rows:
        print("%-32s Lloop = %.3f nH   (%s)" % (design, loop, selfs))


if __name__ == "__main__":
    main()
