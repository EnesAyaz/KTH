"""
Figures formatted for the IEEE conference paper (reports/paper/figures):
  kicad_3d.png, q3d_model.png, icepak_model.png   cropped 3D pictures from KiCad (render_board.py), Q3D and Icepak
  copper_rf.pdf                                   Q3D branch resistance vs frequency (single column)
  thermal_row.pdf                                 Icepak temperature maps, top vs top+bottom cooling (two columns)

    python scripts/paper_figs.py
"""
import os
import sys

import matplotlib
import numpy as np
from PIL import Image, ImageChops

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "paper", "figures")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
plt.rcParams.update({"font.size": 8, "axes.grid": True, "grid.alpha": 0.3, "legend.fontsize": 6.5})


def crop(src, dst, pad=12, cut_logo=False, ignore_red=False):
    im = Image.open(src).convert("RGB")
    if ignore_red:                              # drop the red wireframe of the Icepak air region
        a = np.array(im).astype(int)
        red = (a[:, :, 0] > 150) & (a[:, :, 1] < 120) & (a[:, :, 2] < 120)
        a[red] = 255
        im = Image.fromarray(a.astype("uint8"))
    if cut_logo:                                # remove the Ansys logo in the top-right corner
        w, h = im.size
        im.paste((255, 255, 255), (int(0.85 * w), 0, w, int(0.08 * h)))
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.size[0]), min(box[3] + pad, im.size[1])))
    im.save(dst)
    print("cropped", dst, im.size)


crop(os.path.join(ROOT, "hardware", "spb-building-block", "render_iso.png"), os.path.join(OUT, "kicad_3d.png"))
crop(os.path.join(ROOT, "simulation", "bb_q3d", "results", "images", "q3d_power_loop_xray.png"), os.path.join(OUT, "q3d_model.png"), cut_logo=True)
crop(os.path.join(ROOT, "simulation", "bb_icepak", "results", "icepak_temperature_iso.png"), os.path.join(OUT, "icepak_model.png"), cut_logo=True, ignore_red=True)

# ---------------- Q3D resistance vs frequency (single column) ----------------
import bb_copper_hf as cu  # noqa: E402

names, br, rl, src = cu.load_rl()
fr = np.logspace(2, 8, 200)
fig, ax = plt.subplots(figsize=(3.45, 2.3))
lab = {"DCP:QH_D_L": "dc+ to QH drain", "DCN:QL_S_L": "dc$-$ to QL source", "AC:QH_S_L": "ac to QH source",
       "DCP:CapPL": "dc+ to local MLCCs", "DCP:CapB1P": "dc+ to bank row 1"}
for k_, l_ in lab.items():
    k = names.index(k_)
    r0 = rl(0)[0][k, k]
    ax.semilogx(fr, [rl(x)[0][k, k] / r0 for x in fr], label=l_)
ax.axvline(50e3, color="k", ls=":", lw=0.8)
ax.text(55e3, 6, "50 kHz", fontsize=6.5)
ax.set_xlabel("frequency [Hz]")
ax.set_ylabel("$R(f)/R_{dc}$ (Q3D sweep)")
ax.set_ylim(0.9, 40)
ax.set_yscale("log")
ax.legend(loc="upper left")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "copper_rf.pdf"))
plt.close(fig)

# ---------------- thermal maps in one row ----------------
import plot_icepak as pi  # noqa: E402

RES = os.path.join(ROOT, "simulation", "bb_icepak", "results")
fig, axes = plt.subplots(1, 4, figsize=(7.16, 2.0))
panels = [("devices", "", "(a) top cooling, device layer"), ("board", "", "(b) top cooling, board"),
          ("devices", "_both", "(c) top + bottom, device layer"), ("board", "_both", "(d) top + bottom, board")]
vmax = {t: max(np.nanmax(pi.load(os.path.join(RES, "grid_%s%s.fld" % (t, s)))[2]) for s in ("", "_both"))
        for t in ("devices", "board")}
for ax, (tag, suf, title) in zip(axes, panels):
    xs, ys, T = pi.load(os.path.join(RES, "grid_%s%s.fld" % (tag, suf)))
    im = ax.imshow(T, origin="lower", extent=(xs[0], xs[-1], ys[0], ys[-1]), cmap="inferno", vmin=60, vmax=105, aspect="equal")
    pi.outlines(ax)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=6.5)
    ax.set_xticks([-10, 0, 10])
    ax.set_yticks([-10, 0, 10])
    ax.tick_params(labelsize=6)
    ax.grid(False)
cb = fig.colorbar(im, ax=axes, fraction=0.015, pad=0.01)
cb.set_label("T [$^\\circ$C]", fontsize=7)
cb.ax.tick_params(labelsize=6)
fig.savefig(os.path.join(OUT, "thermal_row.pdf"), bbox_inches="tight")
plt.close(fig)
print("done")
