"""
Pictures of the Q3D models of the final boards, drawn from exactly the geometry handed to Q3D
(simulation/bb_q3d/results/revb_*geometry_<b>.json, written by revb_export.py): copper polygons per net and layer with
their clearance holes, vias with their layer span, FET / capacitor terminal pads. z is stretched for visibility.

    %LOCALAPPDATA%\\kth3d\\Scripts\\python.exe scripts\\render_q3d_model.py
      -> reports/slides/revb_pptx/img/q3d_model_cells.png, q3d_loop_dpt.png, q3d_loop_load.png, q3d_full_load.png
"""
import json
import math
import os

import mapbox_earcut as earcut
import numpy as np
import pyvista as pv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "simulation", "bb_q3d", "results")
IMG = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
ZS = 4.0                                            # z stretch
T, HD, H23, H34, TP = 0.070, 0.100, 1.200, 0.100, 0.035
ZR = {"L1": (T + HD, 2 * T + HD), "L2": (0.0, T), "L3": (-H23 - T, -H23), "L4": (-H23 - T - H34 - T, -H23 - T - H34)}
ZTOP, ZBOT = 2 * T + HD, -H23 - 2 * T - H34


def color(net):
    if net == "DCP":
        return (0.84, 0.18, 0.15)
    if net == "DCN":
        return (0.12, 0.40, 0.75)
    if net.startswith("AC"):
        return (0.95, 0.62, 0.15)
    if net.startswith("LSRC"):
        return (0.20, 0.62, 0.30)
    return (0.6, 0.6, 0.6)


class Mesh:
    def __init__(self):
        self.P, self.F, self.Cc, self.n = [], [], [], 0

    def add(self, P, faces, rgb):
        self.P.append(np.asarray(P, float))
        for f in faces:
            self.F.append([len(f)] + [k + self.n for k in f])
            self.Cc.append(rgb)
        self.n += len(P)

    def slab(self, outline, holes, z0, z1, rgb):
        rings = [np.asarray(outline, float)] + [np.asarray(h, float) for h in holes]
        V = np.vstack(rings)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        tri = earcut.triangulate_float64(V, ends).reshape(-1, 3)
        m = len(V)
        P = np.r_[np.c_[V[:, 0], -V[:, 1], np.full(m, z0 * ZS)], np.c_[V[:, 0], -V[:, 1], np.full(m, z1 * ZS)]]
        faces = [[a, b, c] for a, b, c in tri] + [[a + m, b + m, c + m] for a, b, c in tri]
        start = 0
        for r in rings:
            k = len(r)
            for i in range(k):
                a, b = start + i, start + (i + 1) % k
                faces.append([a, b, b + m, a + m])
            start += k
        self.add(P, faces, rgb)

    def cyl(self, x, y, z0, z1, r, rgb, n=10):
        a = np.linspace(0, 2 * math.pi, n, endpoint=False)
        ring = np.c_[x + r * np.cos(a), -y + r * np.sin(a)]
        P = np.r_[np.c_[ring, np.full(n, z0 * ZS)], np.c_[ring, np.full(n, z1 * ZS)]]
        self.add(P, [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)] + [list(range(n)), list(range(n, 2 * n))],
                 rgb)

    def box(self, x0, x1, y0, y1, z0, z1, rgb):
        P = np.array([(x0, -y0, z0), (x1, -y0, z0), (x1, -y1, z0), (x0, -y1, z0),
                      (x0, -y0, z1), (x1, -y0, z1), (x1, -y1, z1), (x0, -y1, z1)]) * np.array([1, 1, ZS])
        self.add(P, [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]], rgb)

    def poly(self):
        m = pv.PolyData(np.vstack(self.P), np.hstack([np.array(f) for f in self.F]))
        m.cell_data["rgb"] = (np.array(self.Cc) * 255).astype(np.uint8)
        return m


def build(geo):
    M = Mesh()
    for net, lay, outl, holes in geo["polys"]:
        if lay in ZR:
            M.slab(outl, holes, *ZR[lay], color(net))
    for v in geo["vias"]:
        net, x, y, r = v[:4]
        lt, lb = (v[4], v[5]) if len(v) > 5 else ("L1", "L4")
        M.cyl(x, y, ZR[lb][0], ZR[lt][1], max(r, 0.12), tuple(0.8 * c for c in color(net)))
    for net, name, x0, x1, y0, y1, side in geo["pads"]:
        z0, z1 = (ZTOP, ZTOP + TP + 0.25) if side == "top" else (ZBOT - TP - 0.25, ZBOT)
        rgb = (0.85, 0.72, 0.40) if name.startswith(("Q", "C")) else color(net)
        M.box(x0, x1, y0, y1, z0, z1, rgb)
    return M.poly()


def shot(mesh, out, cam, zoom=1.0, size=(2400, 1500), legend=None):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.add_mesh(mesh, scalars="rgb", rgb=True, smooth_shading=False, ambient=0.3, diffuse=0.75, specular=0.1)
    if legend:
        pl.add_legend(legend, bcolor="white", border=True, size=(0.22, 0.2), loc="upper right", face="rectangle")
    pl.enable_anti_aliasing("ssaa")
    pl.camera_position = cam
    pl.camera.zoom(zoom)
    pl.screenshot(os.path.join(IMG, out))
    pl.close()
    print(out)


def iso(c, d, az, el):
    c = np.array(c, float)
    v = np.array([math.cos(math.radians(el)) * math.cos(math.radians(az)),
                  math.cos(math.radians(el)) * math.sin(math.radians(az)), math.sin(math.radians(el))])
    return [tuple(c + d * v), tuple(c), (0, 0, 1)]


LEG = [["DC+ (DCP)", color("DCP")], ["DC- (DCN)", color("DCN")], ["switch node AC", color("AC")],
       ["LS source to shunt (LSRC)", color("LSRC1")], ["FET / MLCC terminals", (0.85, 0.72, 0.40)]]
if __name__ == "__main__":
    for b in ("dpt", "load"):
        p = os.path.join(RES, "revb_loop_geometry_%s.json" % b)
        if os.path.exists(p):
            m = build(json.load(open(p)))
            shot(m, "q3d_loop_%s.png" % b, iso((0, -8, 0), 150, -70, 35), 1.3,
                 legend=LEG if b == "dpt" else LEG[:3] + LEG[4:])
            if b == "load":
                shot(m, "q3d_model_cells.png", iso((-23.75, -8, 0), 62, -60, 38), 1.0, legend=LEG[:3] + LEG[4:])
    p = os.path.join(RES, "revb_geometry_load.json")
    if os.path.exists(p):
        shot(build(json.load(open(p))), "q3d_full_load.png", iso((0, -15, 0), 190, -70, 40), 1.2,
             legend=LEG[:3] + LEG[4:])
