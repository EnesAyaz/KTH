"""
3D render of a KiCad board from the JSON written by kicad_dump.py, using the footprints' KiCad VRML 3D models.

    python scripts/render_board.py [board_3d.json] [out_prefix]

Board body, solder-masked copper of F.Cu, exposed pads, vias and component bodies (KiCad .wrl models, units of
0.1 inch) are drawn with simple Lambert shading in matplotlib. Writes <out_prefix>_iso.png/.pdf and _top.png.
"""
import json
import math
import os
import re
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "hardware", "spb-building-block", "spb-building-block_3d.json")
PRE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "hardware", "spb-building-block", "render")
LIGHT = np.array([-0.35, -0.55, 0.76])
LIGHT /= np.linalg.norm(LIGHT)
_cache = {}


# ------------------------------------------------------------------ VRML (subset used by KiCad models)
def _block(s, i):
    """s[i] == '{' -> index after the matching '}'."""
    depth = 0
    for k in range(i, len(s)):
        if s[k] == "{":
            depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0:
                return k + 1
    return len(s)


def _nums(txt):
    return np.array([float(v) for v in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", txt)])


def load_wrl(path):
    """-> list of (triangles Nx3x3 in mm, rgb). Supports Shape/IndexedFaceSet, Box, Transform.translation, DEF/USE."""
    if path in _cache:
        return _cache[path]
    txt = re.sub(r"#[^\n]*", "", open(path, encoding="latin-1").read())
    mats = {m.group(1): _nums(m.group(2))[:3] for m in
            re.finditer(r"DEF\s+(\S+)\s+Material\s*\{[^}]*?diffuseColor\s+([-\d.eE+\s]+)", txt)}
    out = []

    def shapes(seg, offset):
        for m in re.finditer(r"\bShape\s*\{", seg):
            body = seg[m.end() - 1:_block(seg, m.end() - 1)]
            col = np.array([0.6, 0.6, 0.6])
            mm_ = re.search(r"material\s+USE\s+(\S+)", body)
            if mm_ and mm_.group(1) in mats:
                col = mats[mm_.group(1)]
            else:
                dc = re.search(r"diffuseColor\s+([-\d.eE+\s]+)", body)
                if dc:
                    col = _nums(dc.group(1))[:3]
            box = re.search(r"Box\s*\{\s*size\s+([-\d.eE+\s]+)\}", body)
            if box:
                sx, sy, sz = _nums(box.group(1)) / 2
                c = np.array([[x, y, z] for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)]) + offset
                quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
                tris = [c[[a, b, cc]] for a, b, cc, d in quads] + [c[[a, cc, d]] for a, b, cc, d in quads]
                out.append((np.array(tris) * 2.54, col))
                continue
            pt = re.search(r"point\s*\[([^\]]*)\]", body)
            ci = re.search(r"coordIndex\s*\[([^\]]*)\]", body)
            if not (pt and ci):
                continue
            P = _nums(pt.group(1)).reshape(-1, 3) + offset
            idx = _nums(ci.group(1)).astype(int)
            tris, poly = [], []
            for v in idx:
                if v < 0:
                    for k in range(1, len(poly) - 1):
                        tris.append(P[[poly[0], poly[k], poly[k + 1]]])
                    poly = []
                else:
                    poly.append(v)
            if tris:
                out.append((np.array(tris) * 2.54, col))
    for m in re.finditer(r"\bTransform\s*\{", txt):
        body = txt[m.end() - 1:_block(txt, m.end() - 1)]
        tr = re.search(r"translation\s+([-\d.eE+\s]+)", body)
        shapes(body, _nums(tr.group(1))[:3] if tr else np.zeros(3))
    if not out:
        shapes(txt, np.zeros(3))
    _cache[path] = out
    return out


# ------------------------------------------------------------------ scene
def rect_poly(x0, x1, y0, y1, z):
    return np.array([[x0, -y0, z], [x1, -y0, z], [x1, -y1, z], [x0, -y1, z]])


def rot_pad(x, y, w, h, deg, z):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append([x + c * dx + s * dy, -(y - s * dx + c * dy), z])
    return np.array(pts)


def circle(x, y, r, z, n=14):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.c_[x + r * np.cos(a), -y + r * np.sin(a), np.full(n, z)]


def build(d):
    T = d["thickness"]
    polys, cols = [], []
    edge = [s for s in d["shapes"] if s["layer"] == "Edge.Cuts"][0]
    x0, x1, y0, y1 = edge["x0"], edge["x1"], edge["y0"], edge["y1"]
    mask, cu, pad_col = np.array([0.08, 0.33, 0.16]), np.array([0.12, 0.45, 0.22]), np.array([0.86, 0.74, 0.45])
    # board body (top, bottom, sides)
    top, bot = rect_poly(x0, x1, y0, y1, T), rect_poly(x0, x1, y0, y1, 0)
    polys += [top, bot]
    cols += [mask, mask * 0.6]
    for k in range(4):
        a, b = top[k], top[(k + 1) % 4]
        polys.append(np.array([a, b, [b[0], b[1], 0], [a[0], a[1], 0]]))
        cols.append(np.array([0.75, 0.70, 0.45]))
    for s in d["shapes"]:
        if s["layer"] == "F.Cu":
            polys.append(rect_poly(max(s["x0"], x0), min(s["x1"], x1), max(s["y0"], y0), min(s["y1"], y1), T + 0.012))
            cols.append(cu)
    for p in d["pads"]:
        if p["bottom"]:
            continue
        z = T + 0.03
        polys.append(circle(p["x"], p["y"], p["w"] / 2, z) if p["shape"] == "circle" else rot_pad(p["x"], p["y"], p["w"], p["h"], p["rot"], z))
        cols.append(pad_col)
    for v in d["vias"]:
        polys.append(circle(v["x"], v["y"], v["d"] / 2, T + 0.02, 10))
        cols.append(np.array([0.10, 0.38, 0.19]))
        polys.append(circle(v["x"], v["y"], v["drill"] / 2, T + 0.025, 8))
        cols.append(np.array([0.05, 0.05, 0.05]))
    flat = [(p, c, False, -1) for p, c in zip(polys, cols)]
    for pi, part in enumerate(d["parts"]):
        th = math.radians(part["rot"])
        R = np.array([[math.cos(th), -math.sin(th), 0], [math.sin(th), math.cos(th), 0], [0, 0, 1]])
        if part["bottom"]:                       # bottom-side parts: model mirrored below the board (z -> -z)
            R = R @ np.diag([1.0, -1.0, -1.0])
        for m in part["models"]:
            if not os.path.exists(m["file"]):
                continue
            for tris, col in load_wrl(m["file"]):
                t = tris @ R.T + np.array([part["x"], -part["y"], 0.0 if part["bottom"] else T])
                for tri in t:
                    flat.append((tri, np.clip(col, 0, 1), True, pi))
    return flat, (x0, x1, y0, y1, T)


def shade(poly, col, lit, obj=None):
    if not lit:
        return np.r_[col, 1.0]
    n = np.cross(poly[1] - poly[0], poly[2] - poly[0])
    nn = np.linalg.norm(n)
    k = 0.55 + 0.45 * abs(n @ LIGHT) / nn if nn > 0 else 0.8
    return np.r_[np.clip(col * k, 0, 1), 1.0]


def render(flat, lim, elev, azim, path, title=None, zoom=1.0):
    x0, x1, y0, y1, T = lim
    fig = plt.figure(figsize=(8, 6.4))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    # painter's order: sort by depth along the view direction
    e, a = math.radians(elev), math.radians(azim)
    view = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    # board layers first (everything on the board lies above them), then component bodies object by object
    # (far to near), triangles inside one body far to near
    obj_depth = {}
    for p, c, l, o in flat:
        if o >= 0:
            obj_depth.setdefault(o, []).append(float(np.mean(p, axis=0) @ view))
    obj_depth = {o: float(np.mean(v)) for o, v in obj_depth.items()}
    key = [(0 if o < 0 else 1, obj_depth.get(o, 0.0), float(np.mean(p, axis=0) @ view)) for p, c, l, o in flat]
    order = sorted(range(len(flat)), key=lambda i: key[i])
    # one collection for the board layers and one per component body, drawn in this order (matplotlib sorts
    # polygons only inside a collection)
    groups = {}
    for i in order:
        groups.setdefault(flat[i][3], []).append(i)
    keys = [-1] + sorted([k for k in groups if k >= 0], key=lambda k: obj_depth[k])
    for z, k in enumerate(keys):
        idx = groups.get(k, [])
        if not idx:
            continue
        pc = Poly3DCollection([flat[i][0] for i in idx], facecolors=[shade(*flat[i]) for i in idx],
                              edgecolors="none", linewidths=0, zorder=z)
        ax.add_collection3d(pc)
    cx, cy = (x0 + x1) / 2, -(y0 + y1) / 2
    r = max(x1 - x0, y1 - y0) / 2 / zoom
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r, cy + r)
    ax.set_zlim(-r / 2, r / 2)
    ax.set_box_aspect((1, 1, 0.5))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=10)
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main():
    d = json.load(open(SRC))
    flat, lim = build(d)
    print("faces:", len(flat))
    render(flat, lim, 38, -62, PRE + "_iso.png")
    render(flat, lim, 38, -62, PRE + "_iso.pdf")
    render(flat, lim, 90, -90, PRE + "_top.png")
    render(flat, lim, -38, -62, PRE + "_bottom.png")
    print("written", PRE + "_iso.png/.pdf", PRE + "_top.png", PRE + "_bottom.png")


if __name__ == "__main__":
    main()
