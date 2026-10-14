"""
3D picture of the Rev B leg board from the KiCad models (no 3D viewer CLI in KiCad 7, no VTK in the venv).

Step 1, KiCad python: dump every footprint's 3D model (resolved path), position, orientation, side, plus the pads
    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\render_3d_revb.py dump
Step 2, venv python: read the VRML meshes (IndexedFaceSet, 0.1 inch) and draw them with matplotlib
    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\render_3d_revb.py
  -> reports/slides/revb_pptx/img/revb_3d_iso.png (with heatsink), revb_3d_noheatsink.png, revb_3d_bottom.png
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRD = os.path.join(ROOT, "hardware", "spb-bb-revb")
DUMP = os.path.join(BRD, "plots", "models3d.json")
IMG = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
KI3D = "C:/Program Files/KiCad/7.0/share/kicad/3dmodels"
T = 1.6


def dump():
    import pcbnew
    b = pcbnew.LoadBoard(os.path.join(BRD, "spb-bb-revb.kicad_pcb"))
    parts, pads = [], []
    for f in b.GetFootprints():
        ms = []
        for m in f.Models():
            p = m.m_Filename
            for var in ("${KICAD6_3DMODEL_DIR}", "${KICAD7_3DMODEL_DIR}"):
                p = p.replace(var, KI3D)
            p = p.replace("${KIPRJMOD}", BRD.replace("\\", "/"))
            ms.append(dict(path=os.path.normpath(p), off=[m.m_Offset.x, m.m_Offset.y, m.m_Offset.z],
                           rot=[m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z]))
        pos = f.GetPosition()
        parts.append(dict(ref=f.GetReference(), x=pcbnew.ToMM(pos.x), y=pcbnew.ToMM(pos.y),
                          rot=f.GetOrientationDegrees(), bottom=f.IsFlipped(), models=ms))
        for q in f.Pads():
            bb = q.GetBoundingBox()
            for lay, z in ((pcbnew.F_Cu, 0.0), (pcbnew.B_Cu, -T)):
                if q.IsOnLayer(lay):
                    pads.append([pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()),
                                 pcbnew.ToMM(bb.GetBottom()), z])
    e = b.GetBoardEdgesBoundingBox()
    out = dict(edge=[pcbnew.ToMM(e.GetLeft()), pcbnew.ToMM(e.GetTop()), pcbnew.ToMM(e.GetRight()),
                     pcbnew.ToMM(e.GetBottom())], parts=parts, pads=pads)
    os.makedirs(os.path.dirname(DUMP), exist_ok=True)
    json.dump(out, open(DUMP, "w"))
    print("dumped", len(parts), "footprints", len(pads), "pads ->", DUMP)


_cache = {}


def read_wrl(path):
    """[(rgb, [[(x, y, z), ...] face, ...])] in mm, model y up."""
    if path in _cache:
        return _cache[path]
    if not os.path.exists(path):
        print("  missing model", path)
        _cache[path] = []
        return []
    txt = open(path, errors="ignore").read()
    mats = {}
    for m in re.finditer(r"DEF\s+(\S+)\s+Material\s*\{([^}]*)\}", txt):
        c = re.search(r"diffuseColor\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", m.group(2))
        if c:
            mats[m.group(1)] = tuple(float(v) for v in c.groups())
    shapes = []
    for blk in re.split(r"\bShape\s*\{", txt)[1:]:
        c = re.search(r"diffuseColor\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", blk)
        if c:
            rgb = tuple(float(v) for v in c.groups())
        else:
            u = re.search(r"material\s+USE\s+(\S+)", blk)
            rgb = mats.get(u.group(1), (0.5, 0.5, 0.5)) if u else (0.5, 0.5, 0.5)
        pm = re.search(r"point\s*\[([^\]]*)\]", blk)
        im = re.search(r"coordIndex\s*\[([^\]]*)\]", blk)
        if not pm or not im:
            continue
        v = [float(s) for s in re.split(r"[\s,]+", pm.group(1).strip()) if s]
        pts = [(v[i] * 2.54, v[i + 1] * 2.54, v[i + 2] * 2.54) for i in range(0, len(v) - 2, 3)]
        faces, cur = [], []
        for s in re.split(r"[\s,]+", im.group(1).strip()):
            if not s:
                continue
            k = int(s)
            if k < 0:
                if len(cur) >= 3:
                    faces.append([pts[j] for j in cur])
                cur = []
            else:
                cur.append(k)
        if len(cur) >= 3:
            faces.append([pts[j] for j in cur])
        shapes.append((rgb, faces))
    _cache[path] = shapes
    return shapes


def rot3(p, rx, ry, rz):
    x, y, z = p
    for ang, ax in ((rx, 0), (ry, 1), (rz, 2)):
        if not ang:
            continue
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        if ax == 0:
            y, z = y * c - z * s, y * s + z * c
        elif ax == 1:
            x, z = x * c + z * s, -x * s + z * c
        else:
            x, y = x * c - y * s, x * s + y * c
    return x, y, z


def render():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import numpy as np

    D = json.load(open(DUMP))
    x0, y0, x1, y1 = D["edge"]

    def scene(skip_hs, skip_bar=False):
        polys, cols = [], []

        def box(a, b, c, d, z0, z1, rgb):
            P = [(a, -b, z0), (c, -b, z0), (c, -d, z0), (a, -d, z0), (a, -b, z1), (c, -b, z1), (c, -d, z1), (a, -d, z1)]
            for f in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                polys.append([P[i] for i in f])
                cols.append(rgb)
        box(x0, y0, x1, y1, -T, 0.0, (0.10, 0.36, 0.20))                     # FR4, solder mask green
        for a, b, c, d, z in D["pads"]:
            zz = 0.02 if z == 0 else -T - 0.02
            polys.append([(a, -b, zz), (c, -b, zz), (c, -d, zz), (a, -d, zz)])
            cols.append((0.85, 0.72, 0.40))
        for p in D["parts"]:
            if skip_hs and p["ref"].startswith("HS"):
                continue
            for m in p["models"]:
                if skip_bar and "AC_BOLT" in m["path"]:
                    continue
                for rgb, faces in read_wrl(m["path"]):
                    for f in faces:
                        q = []
                        for v in f:
                            v = rot3(v, *m["rot"])
                            v = (v[0] + m["off"][0], v[1] + m["off"][1], v[2] + m["off"][2])
                            if p["bottom"]:                      # KiCad 3D canvas: 180 deg about y, then about z
                                v = (v[0], -v[1], -v[2])
                            v = rot3(v, 0, 0, p["rot"])
                            q.append((v[0] + p["x"], v[1] - p["y"], v[2] + (-T if p["bottom"] else 0.0)))
                        polys.append(q)
                        cols.append(rgb)
        return polys, cols

    def tile(polys, cols, step=2.0):
        """matplotlib sorts whole polygons by their mean depth: big faces (board, bar, heatsink) would hide the
        small parts, so quads longer than `step` are cut into a grid of small quads."""
        P, C = [], []
        for q, c in zip(polys, cols):
            if len(q) != 4:
                P.append(q)
                C.append(c)
                continue
            a, b, _, d = (np.array(v, float) for v in q)
            n1 = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
            n2 = max(1, int(np.ceil(np.linalg.norm(d - a) / step)))
            if n1 * n2 == 1:
                P.append(q)
                C.append(c)
                continue
            u, w = (b - a) / n1, (d - a) / n2
            for i in range(n1):
                for j in range(n2):
                    o = a + i * u + j * w
                    P.append([tuple(o), tuple(o + u), tuple(o + u + w), tuple(o + w)])
                    C.append(c)
        return P, C

    def light(polys, cols):
        L = np.array([-0.35, -0.5, 0.8])
        L = L / np.linalg.norm(L)
        out = []
        for q, c in zip(polys, cols):
            a = np.array(q)
            n = np.cross(a[1] - a[0], a[2] - a[0])
            nn = np.linalg.norm(n)
            k = 0.55 + 0.45 * abs(n @ L) / nn if nn > 1e-12 else 0.8
            out.append(tuple(min(1, ci * k) for ci in c))
        return out

    def draw(name, elev, azim, skip_hs, zlim, title, skip_bar=False):
        polys, cols = tile(*scene(skip_hs, skip_bar))
        fig = plt.figure(figsize=(12, 9), dpi=200)
        ax = fig.add_subplot(111, projection="3d")
        fc = light(polys, cols)
        pc = Poly3DCollection(polys, facecolors=fc, edgecolors=fc, linewidths=0.25)
        ax.add_collection3d(pc)
        cx, cy = (x0 + x1) / 2, -(y0 + y1) / 2
        r = 50.0
        ax.set_xlim(cx - r, cx + r)
        ax.set_ylim(cy - r, cy + r)
        ax.set_zlim(*zlim)
        ax.set_box_aspect((1, 1, (zlim[1] - zlim[0]) / (2 * r)))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        fig.subplots_adjust(0, 0, 1, 1)
        out = os.path.join(IMG, name)
        fig.savefig(out, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(out)

    os.makedirs(IMG, exist_ok=True)
    draw("revb_3d_noheatsink.png", 38, -62, True, (-12, 24),
         "Rev B leg, top side without heatsink: 8 x EPC2361, 4 x PMK UFCS shunts, 20 x 2220 bank, 2 x 2EDF7275K")
    draw("revb_3d_iso.png", 28, -58, False, (-12, 50),
         "Rev B leg with LAM 4 heatsink (tube along x) on the Al spreader, M6 AC bolt + 12 x 5 mm Cu bar")
    draw("revb_3d_bottom.png", -40, -62, True, (-24, 12),
         "Rev B leg, bottom side: REDCUBE DC terminals, 4 bypass 0805 per cell, U.FL probes", skip_bar=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dump":
        dump()
    else:
        render()
