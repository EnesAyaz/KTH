"""
3D renders of the final Rev B boards and of their assembly, from the KiCad 3D models (scripts/dump_3d.py) with
pyvista / VTK (z-buffered, off-screen). Render venv (pyvista, vtk, cadquery-ocp): %LOCALAPPDATA%\\kth3d

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\dump_3d.py
    %LOCALAPPDATA%\\kth3d\\Scripts\\python.exe scripts\\render_3d.py
      -> reports/slides/revb_pptx/img/r3d_*.png

Assembly of one 75 V level (= one three-phase submodule), leg-local mm (x across the legs, y down as in KiCad, z up):
  PCB busbar top face (L1) at z = 0; the three load-test leg boards (pitch 94.5 mm) stand on their REDCUBE DC
  terminals (6.5 mm) -> leg bottom at z = 6.5; M4 x 8 screws from below through the busbar into the REDCUBEs; nylon
  M2.5 x 6.5 mm standoffs at the leg corner holes H3/H4; M6 stack lugs at x = -+12, y = -37; per leg the 12 x 5 mm
  Cu AC bar through a LEM HO 250-S (envelope 37.8 x 15 x 33 mm, approximate).
Stack: 16 levels in z (pitch LEVEL_DZ); DC+ lug of level k joined to the DC- lug of level k+1 by a Cu braid.
"""
import json
import math
import os
import re

import subprocess

import numpy as np
import pyvista as pv
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
KCLI = "C:/Program Files/KiCad/7.0/bin/kicad-cli.exe"
ORIGIN = {"spb-bb-revb-dpt": (150.0, 100.0), "spb-bb-revb-load": (150.0, 100.0), "spb-busbar": (160.0, 80.0)}
PITCH = 94.5
LEGS = (-PITCH, 0.0, PITCH)
Z_LEG = 6.5                                    # REDCUBE 74650174 height: leg bottom above the busbar top
LEVEL_DZ = 72.0                                # level pitch in the stack (heatsink top 52.8 mm + screws + air)
GREEN, BUSGREEN = (0.10, 0.36, 0.20), (0.12, 0.25, 0.42)
GOLD, COPPER, STEEL, NYLON = (0.85, 0.72, 0.40), (0.85, 0.50, 0.25), (0.62, 0.63, 0.66), (0.93, 0.92, 0.86)
LEMC, BRAID = (0.15, 0.15, 0.17), (0.80, 0.55, 0.35)


def load(name):
    return json.load(open(os.path.join(ROOT, "hardware", name, "plots", "models3d.json")))


_cache = {}


def read_wrl(path):
    """[(rgb, points (n, 3) mm model y up, faces list of index lists)] from a VRML IndexedFaceSet file."""
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
        v = np.array([float(s) for s in re.split(r"[\s,]+", pm.group(1).strip()) if s])
        pts = v[:len(v) // 3 * 3].reshape(-1, 3) * 2.54
        faces, cur = [], []
        for s in re.split(r"[\s,]+", im.group(1).strip()):
            if not s:
                continue
            k = int(s)
            if k < 0:
                if len(cur) >= 3:
                    faces.append(cur)
                cur = []
            else:
                cur.append(k)
        if len(cur) >= 3:
            faces.append(cur)
        shapes.append((rgb, pts, faces))
    _cache[path] = shapes
    return shapes


def rot(P, ang, axis):
    if not ang:
        return P
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    i, j = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[axis]
    Q = P.copy()
    Q[:, i] = P[:, i] * c - P[:, j] * s
    Q[:, j] = P[:, i] * s + P[:, j] * c
    return Q


class Scene:
    """one big triangle mesh with a colour per face; coordinates leg-local (y down) are stored as (x, -y, z)."""

    def __init__(self):
        self.pts, self.faces, self.cols, self.n = [], [], [], 0
        self.tex = []                                   # textured board faces: (4 corners, png)

    def add(self, P, faces, rgb):
        if len(P) == 0 or not faces:
            return
        self.pts.append(np.asarray(P, float))
        for f in faces:
            self.faces.append([len(f)] + [k + self.n for k in f])
            self.cols.append(rgb)
        self.n += len(P)

    def box(self, x0, y0, z0, x1, y1, z1, rgb):
        P = np.array([(x0, -y0, z0), (x1, -y0, z0), (x1, -y1, z0), (x0, -y1, z0),
                      (x0, -y0, z1), (x1, -y0, z1), (x1, -y1, z1), (x0, -y1, z1)])
        self.add(P, [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], rgb)

    def cyl(self, x, y, z0, z1, r, rgb, n=24, r_in=0.0):
        a = np.linspace(0, 2 * math.pi, n, endpoint=False)
        ring = np.c_[x + r * np.cos(a), -y + r * np.sin(a)]
        P = np.r_[np.c_[ring, np.full(n, z0)], np.c_[ring, np.full(n, z1)]]
        faces = [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
        if r_in > 0:
            ri = np.c_[x + r_in * np.cos(a), -y + r_in * np.sin(a)]
            P = np.r_[P, np.c_[ri, np.full(n, z0)], np.c_[ri, np.full(n, z1)]]
            faces += [[2 * n + k, 3 * n + k, 3 * n + (k + 1) % n, 2 * n + (k + 1) % n] for k in range(n)]
            faces += [[k, 2 * n + k, 2 * n + (k + 1) % n, (k + 1) % n] for k in range(n)]
            faces += [[n + k, n + (k + 1) % n, 3 * n + (k + 1) % n, 3 * n + k] for k in range(n)]
        else:
            faces += [list(range(n))[::-1], list(range(n, 2 * n))]
        self.add(P, faces, rgb)

    def segment(self, p0, p1, w, h, rgb):
        """flat strap (braid) from p0 to p1 (leg-local, y down), width w, thickness h."""
        p0, p1 = np.array([p0[0], -p0[1], p0[2]], float), np.array([p1[0], -p1[1], p1[2]], float)
        d = p1 - p0
        u = np.cross(d, [0, 1, 0])
        if np.linalg.norm(u) < 1e-9:
            u = np.cross(d, [1, 0, 0])
        u = u / np.linalg.norm(u) * w / 2
        v = np.cross(d, u)
        v = v / np.linalg.norm(v) * h / 2
        P = np.array([p0 - u - v, p0 + u - v, p0 + u + v, p0 - u + v, p1 - u - v, p1 + u - v, p1 + u + v, p1 - u + v])
        self.add(P, [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], rgb)

    def board(self, D, dx=0.0, dy=0.0, dz=0.0, color=GREEN, skip=()):
        x0, y0, x1, y1 = D["edge"]
        T = D["thickness"]
        self.box(x0 + dx, y0 + dy, dz - T, x1 + dx, y1 + dy, dz, color)
        textured = set()
        for side in ("top", "bottom"):
            png = board_texture(D, side)
            if png:
                z = dz + 0.03 if side == "top" else dz - T - 0.03
                P = np.array([(x0 + dx, -(y0 + dy), z), (x1 + dx, -(y0 + dy), z), (x1 + dx, -(y1 + dy), z),
                              (x0 + dx, -(y1 + dy), z)])
                self.tex.append((P, png))
                textured.add(side)
        for a, b, c, d, side, circ, drill in D["pads"]:
            if side in textured:
                continue
            z = dz + 0.02 if side == "top" else dz - T - 0.02
            if circ:
                n = 20
                r = (c - a) / 2
                ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
                cx, cy = (a + c) / 2 + dx, (b + d) / 2 + dy
                P = np.c_[cx + r * np.cos(ang), -cy + r * np.sin(ang), np.full(n, z)]
                self.add(P, [list(range(n)) if side == "top" else list(range(n))[::-1]], GOLD)
            else:
                P = np.array([(a + dx, -(b + dy), z), (c + dx, -(b + dy), z), (c + dx, -(d + dy), z),
                              (a + dx, -(d + dy), z)])
                self.add(P, [[0, 1, 2, 3] if side == "top" else [3, 2, 1, 0]], GOLD)
        for p in D["parts"]:
            if any(p["ref"].startswith(s) for s in skip):
                continue
            for m in p["models"]:
                for rgb, P0, faces in read_wrl(m["path"]):
                    P = P0 * np.array(m.get("scale", [1, 1, 1]))
                    P = rot(rot(rot(P, m["rot"][0], "x"), m["rot"][1], "y"), m["rot"][2], "z")
                    P = P + np.array(m["off"]) * np.array([1, 1, 1])
                    if p["bottom"]:                      # KiCad 3D canvas: 180 deg about y, then about z
                        P = P * np.array([1, -1, -1])
                    P = rot(P, p["rot"], "z")
                    P = P + np.array([p["x"] + dx, -(p["y"] + dy), dz - (T if p["bottom"] else 0.0)])
                    self.add(P, faces, rgb)

    def mesh(self):
        P = np.vstack(self.pts)
        F = np.hstack([np.array(f) for f in self.faces])
        m = pv.PolyData(P, F)
        m.cell_data["rgb"] = (np.array(self.cols) * 255).astype(np.uint8)
        return m


def level(sc, D_leg, D_bus, dz=0.0, lem=True, screws=True):
    """one 75 V level: busbar + three legs + hardware, busbar top at z = dz."""
    sc.board(D_bus, 0.0, 0.0, dz, BUSGREEN)
    for xl in LEGS:
        sc.board(D_leg, xl, 0.0, dz + Z_LEG + D_leg["thickness"])
        for hx in (-42.35, 42.35):                                      # nylon standoffs at leg H3/H4
            sc.cyl(xl + hx, -22.0, dz, dz + Z_LEG, 2.5, NYLON, 6, 1.35)
        if screws:
            for xt in (-6.0, 6.0):                                      # M4 x 8 screw head + washer below
                sc.cyl(xl + xt, -18.8, dz - 1.6 - 0.8, dz - 1.6, 4.5, STEEL, 24, 2.15)
                sc.cyl(xl + xt, -18.8, dz - 1.6 - 3.6, dz - 1.6 - 0.8, 3.5, STEEL, 6)
        if lem:                                                         # LEM HO 250-S on the AC bar (approx.)
            yl, zb = 55.6 + 8.0, dz + Z_LEG + D_leg["thickness"]
            sc.box(xl - 18.9, yl, zb - 14.0, xl + 18.9, yl + 15.0, zb + 19.0, LEMC)
    for x in (-12.0, 12.0):                                             # M6 stack lugs: ring lug + bolt
        sc.cyl(x, -37.0, dz, dz + 2.0, 6.5, COPPER, 32, 3.3)
        sc.box(x - 4.0, -37.0 - 22.0, dz + 0.4, x + 4.0, -37.0 - 5.5, dz + 1.6, COPPER)
        sc.cyl(x, -37.0, dz + 2.0, dz + 6.0, 5.0, STEEL, 6)
        sc.cyl(x, -37.0, dz - 1.6 - 5.0, dz - 1.6, 5.0, STEEL, 6)


_TEX = {}


def board_texture(D, side):
    """solder mask (green), mask openings (gold) and silkscreen (white) of one board side, plotted by KiCad at
    20 px/mm and cropped to the outline; None if the board does not fit the A4 plot page (busbar)."""
    name = D["name"]
    key = (name, side)
    if key in _TEX:
        return _TEX[key]
    ox, oy = ORIGIN[name]
    x0, y0, x1, y1 = D["edge"]
    ax0, ay0, ax1, ay1 = x0 + ox, y0 + oy, x1 + ox, y1 + oy
    if ax0 < 0 or ay0 < 0 or ax1 > 297 or ay1 > 210:
        _TEX[key] = None
        return None
    pcb = os.path.join(ROOT, "hardware", name, name + ".kicad_pcb")
    tmp = os.path.join(os.environ.get("TEMP", "."), "r3d_tex")
    os.makedirs(tmp, exist_ok=True)
    R = 20.0 * 25.4
    lays = {}
    for what in ("Mask", "SilkS"):
        lay = ("F." if side == "top" else "B.") + what
        pdf = os.path.join(tmp, "%s_%s.pdf" % (name, lay))
        subprocess.run([KCLI, "pcb", "export", "pdf", "--layers", lay, "--black-and-white", "--drill-shape-opt", "0",
                        "-o", pdf, pcb], check=True, capture_output=True)
        out = os.path.join(tmp, "%s_%s" % (name, lay))
        k = R / 25.4
        subprocess.run(["pdftoppm", "-r", "%d" % R, "-gray", "-png", "-singlefile", "-x", str(int(ax0 * k)),
                        "-y", str(int(ay0 * k)), "-W", str(int((ax1 - ax0) * k)), "-H", str(int((ay1 - ay0) * k)),
                        pdf, out], check=True)
        lays[what] = np.asarray(Image.open(out + ".png").convert("L")) < 128
    h = min(a.shape[0] for a in lays.values())
    w = min(a.shape[1] for a in lays.values())
    img = np.zeros((h, w, 3), np.uint8)
    img[:] = (24, 92, 52)
    img[lays["Mask"][:h, :w]] = (214, 182, 100)
    img[lays["SilkS"][:h, :w]] = (245, 245, 240)
    png = os.path.join(tmp, "%s_%s_tex.png" % (name, side))
    Image.fromarray(img).save(png)
    _TEX[key] = png
    return png


_TEXOBJ = {}


def add_textures(pl, quads):
    for P, png in quads:
        if png not in _TEXOBJ:
            _TEXOBJ[png] = pv.read_texture(png)
        q = pv.PolyData(np.asarray(P, float), np.array([4, 0, 1, 2, 3]))
        q.active_texture_coordinates = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], float)
        pl.add_mesh(q, texture=_TEXOBJ[png], ambient=0.35, diffuse=0.7, specular=0.1)


def render(mesh, name, cam, size=(2400, 1500), zoom=1.0, parallel=False, bg="white", tex=()):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background(bg)
    pl.add_mesh(mesh, scalars="rgb", rgb=True, show_edges=False, smooth_shading=False, specular=0.15, ambient=0.25,
                diffuse=0.8)
    add_textures(pl, tex)
    pl.enable_anti_aliasing("ssaa")
    pl.camera_position = cam
    if parallel:
        pl.enable_parallel_projection()
    pl.camera.zoom(zoom)
    out = os.path.join(IMG, name)
    pl.screenshot(out)
    pl.close()
    print(out)


def iso(center, dist, az, el):
    c = np.array(center, float)
    d = np.array([math.cos(math.radians(el)) * math.cos(math.radians(az)),
                  math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))])
    return [tuple(c + dist * d), tuple(c), (0, 0, 1)]


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    DPT, LOAD, BUS = load("spb-bb-revb-dpt"), load("spb-bb-revb-load"), load("spb-busbar")
    # single boards (board centre at 0; KiCad y down -> scene y up)
    for D, nm, skip in ((DPT, "r3d_dpt.png", ()), (LOAD, "r3d_load.png", ()), (LOAD, "r3d_load_nohs.png", ("HS",))):
        sc = Scene()
        sc.board(D, skip=skip)
        render(sc.mesh(), nm, iso((0, -12, 0), 230, -60, 38), zoom=1.0, tex=sc.tex)
    sc = Scene()
    sc.board(DPT)
    render(sc.mesh(), "r3d_dpt_bottom.png", iso((0, -12, 0), 230, -60, -40), zoom=1.0, tex=sc.tex)
    sc = Scene()
    sc.board(DPT)
    render(sc.mesh(), "r3d_dpt_top.png", [(0, -15, 260), (0, -15, 0), (0, 1, 0)], zoom=1.25, parallel=True, tex=sc.tex)
    sc = Scene()
    sc.board(LOAD, skip=("HS",))
    render(sc.mesh(), "r3d_load_top.png", [(0, -15, 260), (0, -15, 0), (0, 1, 0)], zoom=1.25, parallel=True, tex=sc.tex)
    # one 75 V level: busbar + three load-test legs
    sc = Scene()
    level(sc, LOAD, BUS)
    m = sc.mesh()
    T_ = sc.tex
    render(m, "r3d_level_iso.png", iso((0, -10, 15), 520, -62, 32), zoom=1.15, tex=T_)
    render(m, "r3d_level_back.png", iso((0, 20, 10), 520, 110, 28), zoom=1.15, tex=T_)
    render(m, "r3d_level_below.png", iso((0, 15, 0), 520, -70, -35), zoom=1.15, tex=T_)
    render(m, "r3d_level_side.png", [(600, 15, 20), (0, 15, 20), (0, 0, 1)], zoom=2.0, parallel=True, tex=T_)
    # detail: DC connection of the middle leg to the busbar
    render(m, "r3d_level_detail.png", iso((0, 19, 4), 170, 72, 7), zoom=1.0, tex=T_)
    # full inverter: 16 levels in z, DC+ lug of level k to the DC- lug of level k+1 (Cu braid)
    sc = Scene()
    lvl = Scene()
    level(lvl, LOAD, BUS, lem=True, screws=False)
    base = lvl.mesh()
    blocks = []
    for k in range(16):
        blocks.append(base.translate((0, 0, k * LEVEL_DZ), inplace=False))
    for k in range(15):
        z0, z1 = k * LEVEL_DZ + 2.0, (k + 1) * LEVEL_DZ
        sc.segment((-12.0, -37.0 - 14.0, z0), (12.0, -37.0 - 14.0, z1), 8.0, 1.5, BRAID)
    for x, z in ((12.0, 0.0), (-12.0, 15 * LEVEL_DZ + 2.0)):          # stack ends: DC- / DC+ of the 1200 V bus
        sc.segment((x, -37.0 - 14.0, z), (x, -37.0 - 70.0, z), 10.0, 2.0, (0.75, 0.1, 0.1) if x < 0 else (0.1, 0.1, 0.1))
    stack = pv.merge(blocks + [sc.mesh()])
    H = 16 * LEVEL_DZ
    stex = [(P + np.array([0, 0, k * LEVEL_DZ]), png) for k in range(16) for P, png in lvl.tex]
    render(stack, "r3d_stack.png", iso((0, 0, H / 2), 2600, 58, 16), size=(1800, 2400), zoom=1.0, tex=stex)
