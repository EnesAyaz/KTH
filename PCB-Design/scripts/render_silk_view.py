"""
Fabrication-like view of one side of a board for checking the silkscreen: green solder mask, copper under the mask a
little lighter, exposed pads (mask openings) gold, silkscreen white, drilled holes black (vias, plated and
non-plated holes), the board outline. Built from KiCad's own per-layer plots, so it shows exactly the Gerber
content; the bottom side is mirrored as seen from below.

    python scripts/render_silk_view.py [board]   ->  hardware/<board>/plots/<board>_silk_top.png, _silk_bottom.png
Needs kicad-cli, pdftoppm (MiKTeX / poppler) and the KiCad python for the hole list.
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-revb-dpt"
PCB = os.path.join(ROOT, "hardware", NAME, NAME + ".kicad_pcb")
OUT = os.path.join(ROOT, "hardware", NAME, "plots")
CLI = r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
KPY = r"C:\Program Files\KiCad\7.0\bin\python.exe"
DPI = 500
TMP = tempfile.mkdtemp()

HOLES = """
import pcbnew, json, sys
b = pcbnew.LoadBoard(sys.argv[1]); M = pcbnew.ToMM; out = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        out.append([M(t.GetPosition().x), M(t.GetPosition().y), M(t.GetDrillValue()) / 2])
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetDrillSize().x > 0:
            out.append([M(p.GetPosition().x), M(p.GetPosition().y), M(max(p.GetDrillSize().x, p.GetDrillSize().y)) / 2])
bb = b.GetBoardEdgesBoundingBox()
json.dump({"holes": out, "bbox": [M(bb.GetLeft()), M(bb.GetTop()), M(bb.GetRight()), M(bb.GetBottom())]},
          open(sys.argv[2], "w"))
"""


def plot(layer, mirror):
    pdf = os.path.join(TMP, layer.replace(".", "_") + ("_m" if mirror else "") + ".pdf")
    args = [CLI, "pcb", "export", "pdf", "--black-and-white", "--drill-shape-opt", "0", "--layers", layer, "-o", pdf]
    if mirror:
        args.append("--mirror")
    subprocess.run(args + [PCB], check=True, capture_output=True)
    png = pdf[:-4]
    subprocess.run(["pdftoppm", "-r", str(DPI), "-gray", "-png", "-singlefile", pdf, png], check=True)
    return np.array(Image.open(png + ".png").convert("L")) < 128        # True where the layer has something


def side(prefix, mirror, data):
    edge = plot("Edge.Cuts", mirror)
    ys, xs = np.nonzero(edge)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    cu, mask, silk = (plot(prefix + l, mirror)[y0:y1 + 1, x0:x1 + 1] for l in (".Cu", ".Mask", ".SilkS"))
    edge = edge[y0:y1 + 1, x0:x1 + 1]
    img = np.zeros(cu.shape + (3,), np.uint8)
    img[:] = (22, 84, 45)                                  # solder mask over bare laminate
    img[cu] = (40, 120, 62)                                # copper under the mask
    img[mask] = (205, 170, 70)                             # exposed copper (mask opening): ENIG
    img[silk] = (245, 245, 245)                            # silkscreen
    img[edge] = (0, 0, 0)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    bx0, by0, bx1, by1 = data["bbox"]
    sx = im.size[0] / (bx1 - bx0)
    sy = im.size[1] / (by1 - by0)
    for x, y, r in data["holes"]:
        px = ((bx1 - x) if mirror else (x - bx0)) * sx
        py = (y - by0) * sy
        d.ellipse((px - r * sx, py - r * sy, px + r * sx, py + r * sy), fill=(12, 12, 12))
    return im


hp = os.path.join(TMP, "holes.json")
subprocess.run([KPY, "-c", HOLES, PCB, hp], check=True)
data = json.load(open(hp))
os.makedirs(OUT, exist_ok=True)
for prefix, mirror, tag in (("F", False, "top"), ("B", True, "bottom")):
    im = side(prefix, mirror, data)
    path = os.path.join(OUT, "%s_silk_%s.png" % (NAME, tag))
    im.save(path)
    print("wrote", path, im.size)
