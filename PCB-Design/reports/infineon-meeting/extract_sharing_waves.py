"""
Extract the LTspice waveforms shown in the deck (two-parallel sharing cases and the Rev B Q3D leg boards) and inline them. / turn-off waveforms of the two-parallel EPC2361 LTspice runs and inline them in index.html.

    python reports/infineon-meeting/extract_sharing_waves.py

Sources (read only):
  simulation/sharing/paper_run/Sharing_paper.raw              6 stepped cases, LG 2 nH, RG 2 ohm
  simulation/sharing/gate_10_20_2026-11-05/sharing_10_20.raw  step 2 = gate loops 10 / 20 nH
Energies are taken from the LTspice .meas results (100 ns windows), not recomputed here.
"""
import json
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
T1, T2 = 8.5e-6, 9.5e-6          # gate off (turn-off of QL) and gate on (turn-on of QL)
WIN = (-2e-9, 60e-9)          # 2 nH cases use 40 ns; the slower 10/20 nH case uses 60 ns
DT = 0.25e-9


def read_raw(path):
    data = open(path, "rb").read()
    marker = "Binary:\n".encode("utf-16-le")
    end = data.index(marker) + len(marker)
    header = data[:end].decode("utf-16-le")
    nvar = int(re.search(r"No. Variables:\s*(\d+)", header).group(1))
    npts = int(re.search(r"No. Points:\s*(\d+)", header).group(1))
    names = [n.lower() for n in re.findall(r"^\t\d+\t(\S+)\t", header, re.M)]
    dt = np.dtype([("t", "<f8")] + [("v%d" % i, "<f4") for i in range(1, nvar)])
    rec = np.frombuffer(data, dt, count=npts, offset=end)
    arr = np.column_stack([np.abs(rec["t"])] + [rec["v%d" % i].astype(float) for i in range(1, nvar)])
    off = re.search(r"Offset:\s*(\S+)", header)
    cuts = [0] + [k for k in range(1, npts) if arr[k, 0] < arr[k - 1, 0]] + [npts]
    arr[:, 0] += float(off.group(1)) if off else 0.0   # runs saved from T1-200n store time relative to Offset
    return {n: i for i, n in enumerate(names)}, [arr[a:b] for a, b in zip(cuts[:-1], cuts[1:])]


def edge(col, a, tc, t_end=40e-9):
    t = a[:, 0]
    tq = tc + np.arange(WIN[0], t_end + DT / 2, DT)
    g = lambda k: np.interp(tq, t, a[:, col[k]])
    i1, i2, il = g("i(ld1)"), g("i(ld2)"), g("i(lload)")
    v1, v2 = g("v(d1)") - g("v(s1)"), g("v(d2)") - g("v(s2)")
    g1, g2 = g("v(g1)") - g("v(s1)"), g("v(g2)") - g("v(s2)")
    r1 = lambda x: [round(float(v), 1) for v in x]
    r2 = lambda x: [round(float(v), 2) for v in x]
    return {"i1": r1(i1), "i2": r1(i2), "il": r1(il), "v1": r1(v1), "v2": r1(v2), "g1": r2(g1), "g2": r2(g2)}


def meas(log, name):
    txt = open(log, encoding="utf-8", errors="ignore").read()
    blk = re.search(r"Measurement: %s\n.*?\n((?:\s+\d+\t.*\n)+)" % name, txt)
    return [float(r.split("\t")[1]) for r in blk.group(1).strip().splitlines()]


def main():
    out = {"t0": WIN[0] * 1e9, "dt": DT * 1e9, "cases": []}
    pr = os.path.join(ROOT, "simulation", "sharing", "paper_run")
    col, steps = read_raw(os.path.join(pr, "Sharing_paper.raw"))
    log = os.path.join(pr, "Sharing_paper.log")
    E = {k: meas(log, k) for k in ("eon1", "eon2", "eoff1", "eoff2")}
    for s, a in enumerate(steps):
        out["cases"].append({"src": "paper_run step %d" % s,
                             "eon": [round(E["eon1"][s] * 1e6, 1), round(E["eon2"][s] * 1e6, 1)],
                             "eoff": [round(E["eoff1"][s] * 1e6, 1), round(E["eoff2"][s] * 1e6, 1)],
                             "on": edge(col, a, T2), "off": edge(col, a, T1)})
    gd = os.path.join(ROOT, "simulation", "sharing", "gate_10_20_2026-11-05")
    col, steps = read_raw(os.path.join(gd, "sharing_10_20.raw"))
    res = json.load(open(os.path.join(gd, "results.json")))["cases"][2]
    out["cases"].append({"src": "gate_10_20 step 2",
                         "eon": [round(res["eon1_uJ"], 1), round(res["eon2_uJ"], 1)],
                         "eoff": [round(res["eoff1_uJ"], 1), round(res["eoff2_uJ"], 1)],
                         "on": edge(col, steps[2], T2, WIN[1]), "off": edge(col, steps[2], T1, WIN[1])})
    js = "const WAVES=" + json.dumps(out, separators=(",", ":")) + ";"
    html = os.path.join(HERE, "index.html")
    s = open(html, encoding="utf-8").read()
    s, n = re.subn(r"/\*WAVES-BEGIN\*/.*?/\*WAVES-END\*/", lambda m: "/*WAVES-BEGIN*/" + js + "/*WAVES-END*/", s, flags=re.S)
    assert n == 1, "marker not found"
    open(html, "w", encoding="utf-8").write(s)
    for c in out["cases"]:
        print(c["src"], "Eon", c["eon"], "Eoff", c["eoff"], "pk on", max(c["on"]["i1"]), max(c["on"]["i2"]))
    print("inlined %d kB" % (len(js) // 1024))
    revb()


def revb():
    """Rev B leg boards with the full Q3D copper (simulation/bb_spice/REVB_Q3D_*.raw), four cells."""
    t1 = 0.5e-6 + 1.0667e-05
    t2 = t1 + 1e-6
    sp = os.path.join(ROOT, "simulation", "bb_spice")
    q = json.load(open(os.path.join(ROOT, "reports", "slides", "data", "q3d_spice_numbers.json")))
    out = {"t0": -2.0, "dt": DT * 1e9, "boards": {}}
    for key in ("dpt", "dpt_rg2.5", "dpt_lumpgate", "load", "load_rg3"):
        f = "REVB_Q3D_%s.raw" % key
        col, steps = read_raw(os.path.join(sp, f))
        a = steps[0]
        t = a[:, 0]
        b = {"loop": round(q[key]["loop_nH"], 3), "rgon": q[key]["RGON"],
             "eon": [round(c["Eon_uJ"], 1) for c in q[key]["cells"]],
             "eoff": [round(c["Eoff_uJ"], 1) for c in q[key]["cells"]],
             "vhpk": [round(c["VHpk"], 1) for c in q[key]["cells"]],
             "vlpk": [round(c["Vpk"], 1) for c in q[key]["cells"]]}
        for ed, tc in (("on", t2), ("off", t1)):
            tq = tc + np.arange(-2e-9, 45e-9 + DT / 2, DT)
            g = lambda n: np.interp(tq, t, a[:, col[n]])
            r1 = lambda x: [round(float(v), 1) for v in x]
            r2 = lambda x: [round(float(v), 2) for v in x]
            b[ed] = {"i": [r1(g("i(vil%d)" % k)) for k in range(1, 5)],
                     "vl": [r1(g("v(dl%d)" % k) - g("v(ql_s_%d)" % k)) for k in range(1, 5)],
                     "vh": [r1(g("v(dh%d)" % k) - g("v(qh_s_%d)" % k)) for k in range(1, 5)],
                     "gl": [r2(g("v(gl%d)" % k) - g("v(ql_s_%d)" % k)) for k in range(1, 5)],
                     "gh": [r2(g("v(gh%d)" % k) - g("v(qh_s_%d)" % k)) for k in range(1, 5)],
                     "il": r1(np.abs(g("i(lload)")))}
        out["boards"][key] = b
        print("revb", key, "loop", b["loop"], "Eon", b["eon"], "VHpk", b["vhpk"], "pk i on", [max(x) for x in b["on"]["i"]])
    js = "const REVB=" + json.dumps(out, separators=(",", ":")) + ";"
    html = os.path.join(HERE, "index.html")
    s = open(html, encoding="utf-8").read()
    s, n = re.subn(r"/\*REVB-BEGIN\*/.*?/\*REVB-END\*/", lambda m: "/*REVB-BEGIN*/" + js + "/*REVB-END*/", s, flags=re.S)
    assert n == 1, "REVB marker not found"
    open(html, "w", encoding="utf-8").write(s)
    print("inlined REVB %d kB" % (len(js) // 1024))


if __name__ == "__main__":
    main()
