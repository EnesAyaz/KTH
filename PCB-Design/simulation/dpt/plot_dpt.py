"""
Plot the double-pulse waveforms from DPT_PL_A.raw (LTspice binary, stepped).

    python simulation/dpt/plot_dpt.py      -> simulation/dpt/DPT_PL_A.png
"""
import os
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "DPT_PL_A.raw")


def read_raw(path):
    """LTspice binary transient raw: time float64, other traces float32. Returns names, list of step arrays."""
    data = open(path, "rb").read()
    marker = "Binary:\n".encode("utf-16-le")
    hdr_end = data.index(marker) + len(marker)
    header = data[:hdr_end].decode("utf-16-le")
    nvar = int(re.search(r"No. Variables:\s*(\d+)", header).group(1))
    npts = int(re.search(r"No. Points:\s*(\d+)", header).group(1))
    names = re.findall(r"^\t\d+\t(\S+)\t", header, re.M)
    dt = np.dtype([("time", "<f8")] + [("v%d" % i, "<f4") for i in range(1, nvar)])
    rec = np.frombuffer(data, dt, count=npts, offset=hdr_end)
    arr = np.empty((npts, nvar))
    arr[:, 0] = np.abs(rec["time"])          # LTspice flags some points with negative time
    for i in range(1, nvar):
        arr[:, i] = rec["v%d" % i]
    starts = [0] + [k for k in range(1, npts) if arr[k, 0] < arr[k - 1, 0]] + [npts]
    return names, [arr[a:b] for a, b in zip(starts[:-1], starts[1:])]


def main():
    names, steps = read_raw(RAW)
    col = {n.lower(): i for i, n in enumerate(names)}

    def sig(a, n):
        return a[:, col[n.lower()]]

    # timing from the netlist defaults: TSTART=1u, TON1=20u*120/75, TOFF=2u
    t1 = 1e-6 + 20e-6 * 120 / 75
    t2 = t1 + 2e-6
    labels = ["star gate routing (2.1 / 2.1 nH)", "direct routing (2.0 / 7.7 nH)"]
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex="col")
    for col_i, (tc, title) in enumerate(((t1, "QL turn-off (end of pulse 1)"), (t2, "QL turn-on (pulse 2)"))):
        for s, a in enumerate(steps):
            t = a[:, 0]
            m = (t > tc - 10e-9) & (t < tc + 60e-9)
            tn = (t[m] - tc) * 1e9
            ls = "-" if s == 0 else "--"
            ax = axes[0, col_i]
            ax.plot(tn, sig(a, "V(qld1)")[m] - sig(a, "V(qls1)")[m], ls, color="C0", label="QL1 VDS, " + labels[s])
            ax.plot(tn, sig(a, "V(qhd1)")[m] - sig(a, "V(qhs1)")[m], ls, color="C3", label="QH1 VDS, " + labels[s])
            ax = axes[1, col_i]
            ax.plot(tn, sig(a, "I(Vidl1)")[m], ls, color="C0", label="QL1 ID, " + labels[s])
            ax.plot(tn, sig(a, "I(Vidl2)")[m], ls, color="C1", label="QL2 ID, " + labels[s])
            ax = axes[2, col_i]
            ax.plot(tn, sig(a, "V(gl1x)")[m] - sig(a, "V(qls1)")[m], ls, color="C0", label="QL1 VGS, " + labels[s])
            ax.plot(tn, sig(a, "V(gl2x)")[m] - sig(a, "V(qls2)")[m], ls, color="C1", label="QL2 VGS, " + labels[s])
            ax.plot(tn, sig(a, "V(gh1x)")[m] - sig(a, "V(qhs1)")[m], ls, color="C3", label="QH1 VGS, " + labels[s])
        axes[0, col_i].set_title(title)
        axes[0, col_i].axhline(100, color="k", lw=0.8, ls=":")
        axes[0, col_i].axhline(90, color="grey", lw=0.8, ls=":")
        axes[2, col_i].axhline(0.8, color="grey", lw=0.8, ls=":")
        axes[2, col_i].set_xlabel("time from switching command [ns]")
    axes[0, 0].set_ylabel("VDS [V]  (dotted: 90 V limit, 100 V rating)")
    axes[1, 0].set_ylabel("drain current [A]")
    axes[2, 0].set_ylabel("VGS at die [V]  (dotted: 0.8 V min Vth)")
    for ax in axes.flat:
        ax.grid(alpha=0.3)
    axes[0, 1].legend(fontsize=7, loc="upper right")
    axes[1, 1].legend(fontsize=7, loc="upper right")
    axes[2, 1].legend(fontsize=7, loc="center right")
    fig.suptitle("DPT, 75 V / 117 A, 2 x EPC2361 per switch, Q3D PL_A loop, LT8418-like driver, Rg_on 2 ohm")
    fig.tight_layout()
    out = os.path.join(HERE, "DPT_PL_A.png")
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == "__main__":
    main()
