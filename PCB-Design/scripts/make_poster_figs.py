"""Print-resolution figures for the A0 poster (reports/poster/spb_project_poster_A0.svg, edited by hand in Inkscape).

    python scripts/make_poster_figs.py  -> reports/poster/img/poster_*.png

Every raster is made for its box on the poster at >= 300 dpi:
  fig03 / fig13 / fig16   review figures, rendered from the vector PDFs (Review-Paper-SPB/Figures/Exported)
  q3d_full_load           Ansys Q3D model, legend cropped off (the legend is SVG text on the poster)
  loop_cells              commutation loop per cell, fonts sized for A0 (data: reports/slides/data/final_numbers.json)
"""
import json, os, subprocess, tempfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KTH = os.path.dirname(ROOT)
REV = os.path.join(KTH, "Review-Paper-SPB", "Figures", "Exported")
SLI = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
OUT = os.path.join(ROOT, "reports", "poster", "img")
DPI = 300


def autocrop(im, pad=4):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im.convert("RGB"), bg).point(lambda v: 255 if v > 12 else 0).getbbox()
    l, t, r, b = box
    return im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.size[0]), min(b + pad, im.size[1])))


def from_pdf(name, width_mm):
    """Render a review figure for a box width_mm wide at DPI (from the vector PDF)."""
    pdf = os.path.join(REV, name + ".pdf")
    w_pt = float(subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
                 .split("Page size:")[1].split()[0])
    res = int(DPI * width_mm / (w_pt / 72 * 25.4) * 1.15) + 1      # 15 % margin for the white border
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", str(res), "-png", "-singlefile", pdf, os.path.join(d, "p")], check=True)
        im = autocrop(Image.open(os.path.join(d, "p.png")).convert("RGB"))
    im.save(os.path.join(OUT, "poster_%s.png" % name), optimize=True)
    print(name, im.size, "%.0f dpi" % (im.size[0] / (width_mm / 25.4)))


os.makedirs(OUT, exist_ok=True)
from_pdf("fig03", 217)
from_pdf("fig13", 184)
from_pdf("fig16", 294)

# Q3D model: drop the legend (top right), keep the model
im = Image.open(os.path.join(SLI, "q3d_full_load.png")).convert("RGB")
im.paste((255, 255, 255), (1780, 0, im.size[0], 380))
im = autocrop(im)
im.save(os.path.join(OUT, "poster_q3d_model.png"), optimize=True)
print("q3d", im.size)

# loop per cell, drawn at the poster box size (132 x 67 mm) so the fonts print at 14-16 pt (body text is ~19 pt)
FQ = json.load(open(os.path.join(ROOT, "reports", "slides", "data", "final_numbers.json")))
plt.rcParams.update({"font.size": 16, "font.family": "Segoe UI", "axes.grid": True, "grid.alpha": 0.3})
fig, ax = plt.subplots(figsize=(132 / 25.4, 67 / 25.4), dpi=DPI)
xs = np.arange(4)
for k, (b, lab, col) in enumerate((("dpt", "DPT board", "#C84632"), ("load", "load board", "#1954A6"))):
    v = [FQ[b]["loop"]["all_switching"]["cell%d" % c] for c in range(1, 5)]
    ax.bar(xs + (k - 0.5) * 0.4, v, 0.38, color=col, label=lab)
    for x_, y_ in zip(xs + (k - 0.5) * 0.4, v):
        ax.text(x_, y_ + 0.015, "%.2f" % y_, ha="center", va="bottom", fontsize=13)
ax.axhline(0.5, color="#2CA02C", ls="--", lw=1.4)
ax.text(4.5, 0.52, "0.5 nH\ndesign", color="#2CA02C", ha="right", va="bottom", fontsize=13, linespacing=1.0)
ax.set_xticks(xs)
ax.set_xticklabels(["cell %d" % c for c in range(1, 5)])
ax.set_ylabel("nH per cell")
ax.set_xlim(-0.55, 4.5)
ax.set_ylim(0, 1.0)
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
ax.grid(axis="x", visible=False)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=14, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.06),
          handlelength=1.2, columnspacing=1.2)
fig.tight_layout(pad=0.3)
fig.savefig(os.path.join(OUT, "poster_loop_cells.png"))
plt.close(fig)
print("loop_cells", Image.open(os.path.join(OUT, "poster_loop_cells.png")).size)
