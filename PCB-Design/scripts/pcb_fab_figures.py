"""Report figures for reports/pcb-fab from the layer plots (run scripts/plot_fab.ps1 first)."""
import os
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = os.path.join(ROOT, "hardware", "spb-bb-fab", "plots")
out = os.path.join(ROOT, "reports", "pcb-fab", "figures")
os.makedirs(out, exist_ok=True)
s = 600 / 25.4
names = [("L1_top", "L1 (top)"), ("L2", "L2"), ("L3", "L3"), ("L4_bottom", "L4 (bottom)")]
ims = {f: Image.open(os.path.join(d, f + ".png")).convert("RGB") for f, _ in names}


def crop(f, x0, y0, x1, y1, div):
    c = ims[f].crop((int(x0 * s), int(y0 * s), int(x1 * s), int(y1 * s)))
    return c.resize((c.width // div, c.height // div))


for fname, box, ext, size, div in (("fig_layers.png", (78.6, 75.3, 121.4, 161.5), (-21.4, 21.4, 61.5, -24.7), (7.2, 4.6), 3),
                                    ("fig_corridor.png", (92.5, 102.0, 107.5, 123.5), (-7.5, 7.5, 23.5, 2.0), (7.2, 3.3), 1)):
    fig, ax = plt.subplots(1, 4, figsize=size)
    for a, (f, t) in zip(ax, names):
        a.imshow(crop(f, *box, div), extent=ext)
        a.set_title(t, fontsize=8)
        a.tick_params(labelsize=6)
        a.set_xlabel("x [mm]", fontsize=7)
        if a is not ax[0]:
            a.set_yticklabels([])
    ax[0].set_ylabel("y [mm]", fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(out, fname), dpi=300)
    plt.close(fig)
# measurement landings (right cell): L1 and L3
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.9))
for a, (f, t) in zip(ax, (("L1_top", "L1: landings D, K, G, H"), ("L3", "L3: sense pairs"))):
    a.imshow(crop(f, 103.0, 98.0, 121.5, 118.0, 1), extent=(3.0, 21.5, 18.0, -2.0))
    a.set_title(t, fontsize=8)
    a.tick_params(labelsize=6)
    a.set_xlabel("x [mm]", fontsize=7)
ax[0].set_ylabel("y [mm]", fontsize=7)
for (x, y, s_) in ((13.4, 4.2, "D"), (15.5, 4.2, "K"), (17.3, 4.7, "G"), (19.6, 0.9, "H")):
    ax[0].annotate(s_, (x, y), color="k", fontsize=8, ha="center", weight="bold")
plt.tight_layout()
plt.savefig(os.path.join(out, "fig_landings.png"), dpi=300)
plt.close(fig)

# heatsink stack-up (section through a cell, not to scale in z)
import matplotlib.patches as mp
fig, ax = plt.subplots(figsize=(7.2, 2.6))
def box(x0, x1, z0, z1, c, lab=None):
    ax.add_patch(mp.Rectangle((x0, z0), x1 - x0, z1 - z0, fc=c, ec="k", lw=0.5))
    if lab:
        ax.text(x1 + 0.4, (z0 + z1) / 2, lab, fontsize=6.5, va="center")
box(-21, 21, -1.6, 0, "#3a7d44", None)
box(-12.5, -6.5, 0, 0.68, "#222222")
box(6.5, 12.5, 0, 0.68, "#222222", "EPC2361 (0.68 mm, top = source)")
box(-14.2, -4.8, 0, 1.25, "#c8a050")
box(-13.5, -5.5, 0.68, 1.08, "#8aa0b8")
box(5.5, 13.5, 0.68, 1.08, "#8aa0b8", "gap pad 0.5 mm -> 0.4 mm, insulating")
box(-13.5, -5.5, 1.08, 1.68, "#c0c6cc")
box(5.5, 13.5, 1.08, 1.68, "#c0c6cc", "pedestal 0.6 mm")
box(-21, 21, 1.68, 4.68, "#d4d8dc", "Al spreader 3 mm (M2.5 to the board)")
box(-20, 20, 4.68, 9.0, "#e8eaec", "LAM 4 K 50 12 (40 x 40 x 50 mm, 12 V fan)")
ax.text(-21, -2.4, "PCB 1.6 mm, 4 x 70 um", fontsize=6.5)
ax.text(-14.2, 1.45, "0805 (1.25 mm)", fontsize=6)
ax.set_xlim(-22, 40)
ax.set_ylim(-3, 9.5)
ax.set_xlabel("x [mm]", fontsize=7)
ax.set_ylabel("z [mm]", fontsize=7)
ax.tick_params(labelsize=6)
plt.tight_layout()
plt.savefig(os.path.join(out, "fig_heatsink.png"), dpi=300)
plt.close(fig)
print("ok")

