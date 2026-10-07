"""
Plot drain-current sharing for the six cases of Sharing_2xEPC2361.asc.

    python simulation/sharing/plot_sharing.py   -> simulation/sharing/Sharing_2xEPC2361.png
"""
import os
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "Sharing_2xEPC2361.raw")
CASES = ["0 baseline (symmetric, Kelvin)", "1 power loop: LD2 +0.3 nH", "2 gate loop: LG2 2 -> 8 nH",
         "3 no Kelvin: LS = common-source L", "4 no Kelvin + LS2 +0.2 nH", "5 Vth2 +0.3 V"]
# timing defaults: TSTART 0.5u, TON1 = 5u*120/75 = 8u, TOFF 1u
T1 = 0.5e-6 + 5e-6 * 120 / 75
T2 = T1 + 1e-6


def read_raw(path):
    data = open(path, "rb").read()
    marker = "Binary:\n".encode("utf-16-le")
    end = data.index(marker) + len(marker)
    header = data[:end].decode("utf-16-le")
    nvar = int(re.search(r"No. Variables:\s*(\d+)", header).group(1))
    npts = int(re.search(r"No. Points:\s*(\d+)", header).group(1))
    names = re.findall(r"^\t\d+\t(\S+)\t", header, re.M)
    dt = np.dtype([("t", "<f8")] + [("v%d" % i, "<f4") for i in range(1, nvar)])
    rec = np.frombuffer(data, dt, count=npts, offset=end)
    arr = np.column_stack([np.abs(rec["t"])] + [rec["v%d" % i] for i in range(1, nvar)])
    cuts = [0] + [k for k in range(1, npts) if arr[k, 0] < arr[k - 1, 0]] + [npts]
    return {n.lower(): i for i, n in enumerate(names)}, [arr[a:b] for a, b in zip(cuts[:-1], cuts[1:])]


def main():
    col, steps = read_raw(RAW)
    fig, axes = plt.subplots(len(steps), 2, figsize=(11, 2.1 * len(steps)), sharex="col")
    for s, a in enumerate(steps):
        t = a[:, 0]
        for j, (tc, name) in enumerate(((T2, "turn-on"), (T1, "turn-off"))):
            m = (t > tc - 5e-9) & (t < tc + 40e-9)
            ax = axes[s, j]
            ax.plot((t[m] - tc) * 1e9, a[m, col["i(ld1)"]], color="C0", label="QL1 drain current")
            ax.plot((t[m] - tc) * 1e9, a[m, col["i(ld2)"]], color="C1", label="QL2 drain current")
            ax.grid(alpha=0.3)
            ax.set_ylabel("A")
            if s == 0:
                ax.set_title("QL %s" % name)
            ax.text(0.99, 0.95, CASES[s], transform=ax.transAxes, ha="right", va="top", fontsize=8,
                    bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"))
    axes[0, 0].legend(fontsize=7, loc="lower right")
    for j in range(2):
        axes[-1, j].set_xlabel("time from gate command [ns]")
    fig.suptitle("Two parallel EPC2361, 75 V / 120 A double pulse: current sharing per case")
    fig.tight_layout()
    out = os.path.join(HERE, "Sharing_2xEPC2361.png")
    fig.savefig(out, dpi=120)
    print(out)


if __name__ == "__main__":
    main()
