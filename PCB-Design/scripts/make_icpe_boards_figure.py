"""
Board figure of the ICPE digest: (a) DPT board, top view, (b) load-test board, (c) Q3D loop model of the DPT board.

    python scripts/make_icpe_boards_figure.py   -> reports/paper/icpe/img/boards.png
Inputs: reports/slides/revb_pptx/img/r3d_dpt_top.png, r3d_load.png (scripts/render_3d.py) and q3d_loop_dpt.png
(scripts/render_q3d_model.py).
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
OUT = os.path.join(ROOT, "reports", "paper", "icpe", "img", "boards.png")
H, GAP, LAB = 560, 40, 70                          # panel height, gap between panels, label band (px)


def trim(im):
    """Crop the white border."""
    bg = Image.new(im.mode, im.size, (255, 255, 255) if im.mode == "RGB" else (255, 255, 255, 255))
    from PIL import ImageChops
    box = ImageChops.difference(im, bg).getbbox()
    return im.crop(box) if box else im


panels = []
for name in ("r3d_dpt_top.png", "r3d_load.png", "q3d_loop_dpt.png"):
    im = trim(Image.open(os.path.join(IMG, name)).convert("RGB"))
    panels.append(im.resize((round(im.width * H / im.height), H), Image.LANCZOS))
W = sum(p.width for p in panels) + GAP * (len(panels) - 1)
out = Image.new("RGB", (W, H + LAB), "white")
draw = ImageDraw.Draw(out)
try:
    font = ImageFont.truetype("times.ttf", 44)
except OSError:
    font = ImageFont.load_default()
x = 0
for k, p in enumerate(panels):
    out.paste(p, (x, 0))
    t = "(%s)" % "abc"[k]
    tw = draw.textlength(t, font=font)
    draw.text((x + (p.width - tw) / 2, H + 10), t, fill="black", font=font)
    x += p.width + GAP
out.save(OUT, dpi=(300, 300))
print("wrote", OUT, out.size)
