"""
3D pictures of the SPB cell assembly without Fusion: same geometry and parameters as
hardware/cell-assembly/SPB_Cell_Assembly/SPB_Cell_Assembly.py (parsed from that file), leg boards from the KiCad
3D dump (spb-building-block_3d.json + KiCad VRML models).

    python scripts/cell_render.py -> hardware/cell-assembly/cell_iso.png, cell_exploded.png, cell_bottom.png
"""
import ast
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import render_board as rb  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

OUT = os.path.join(ROOT, "hardware", "cell-assembly")
FUS = os.path.join(OUT, "SPB_Cell_Assembly", "SPB_Cell_Assembly.py")
src = open(FUS, encoding="utf-8").read()
tree = ast.parse(src)
G = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], (ast.Name, ast.Tuple)):
        try:
            val = ast.literal_eval(node.value) if not isinstance(node.value, ast.Call) else \
                {k.arg: ast.literal_eval(k.value) for k in node.value.keywords}
        except Exception:
            continue
        if isinstance(node.targets[0], ast.Name):
            G[node.targets[0].id] = val
        else:
            for t, v in zip(node.targets[0].elts, val):
                G[t.id] = v
P = G["P"]
FETS, DRIVER, HOLES, PED_FET, PED_BANK = G["FETS"], G["DRIVER"], G["HOLES"], G["PED_FET"], G["PED_BANK"]
J1, J2, J3, J4 = G["J1"], G["J2"], G["J3"], G["J4"]

AL, CU, ALN, TIMC = (0.74, 0.77, 0.82), (0.86, 0.50, 0.30), (0.95, 0.95, 0.90), (0.45, 0.75, 0.95)
INS, PEEK, STEEL, DARK, GREEN, WATER = (0.95, 0.80, 0.25), (0.88, 0.82, 0.68), (0.55, 0.57, 0.60), (0.13, 0.13, 0.15), \
    (0.10, 0.42, 0.22), (0.15, 0.45, 0.90)


# ------------------------------------------------------------------ primitives -> list of polygons
def box(x0, x1, y0, y1, z0, z1):
    c = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])
    q = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return [c[list(f)] for f in q]


def cyl(x, y, z0, z1, d, n=18, axis="z"):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = d / 2
    if axis == "z":
        b = np.c_[x + r * np.cos(a), y + r * np.sin(a), np.full(n, z0)]
        t = np.c_[x + r * np.cos(a), y + r * np.sin(a), np.full(n, z1)]
    else:                                   # along x from z0 to z1 at (y, x as z-height)
        b = np.c_[np.full(n, z0), y + r * np.cos(a), x + r * np.sin(a)]
        t = np.c_[np.full(n, z1), y + r * np.cos(a), x + r * np.sin(a)]
    polys = [b, t]
    for k in range(n):
        polys.append(np.array([b[k], b[(k + 1) % n], t[(k + 1) % n], t[k]]))
    return polys


def build(explode=0.0, housing=True):
    """-> list of objects: (polys, rgb, alpha, lit, name)."""
    n, pitch = P["n_legs"], P["pitch"]
    xs = [k * pitch for k in range(n)]
    ez_up, ez_dn = explode, -explode
    objs = []

    def add(polys, col, alpha=1.0, name="", dz=0.0):
        polys = [p + np.array([0, 0, dz]) for p in polys]
        objs.append((polys, np.array(col), alpha, True, name))
    CAT = {"plate": "plate", "coolant": "plate", "fitting": "plate", "pedestal": "plate", "AlN": "plate", "TIM": "plate",
           "DC+": "busbar", "ins": "busbar", "DC-": "busbar", "boss": "busbar", "screw": "busbar", "lead": "leads",
           "aux": "aux", "ffc": "ffc", "ins sheet": "housing", "housing": "housing", "": "top"}

    # leg boards from the KiCad dump (board layers as one object, each part as one object)
    d = json.load(open(os.path.join(ROOT, "hardware", "spb-building-block", "spb-building-block_3d.json")))
    flat, _ = rb.build(d)
    for k in range(n):
        groups = {}
        for poly, col, lit, o in flat:
            groups.setdefault(o, ([], []))
            groups[o][0].append(poly + np.array([xs[k], 0, 0]))
            groups[o][1].append(col)
        for o, (polys, cols) in groups.items():
            zc = float(np.mean([np.mean(pp[:, 2]) for pp in polys]))
            objs.append((polys, np.array(cols), 1.0, o >= 0, "board" if o < 0 else ("terminal" if zc < 0 else "part")))
        for fx, fy in FETS:
            add(box(xs[k] + fx - 2.5, xs[k] + fx + 2.5, fy - 1.5, fy + 1.5, P["bt"], P["bt"] + P["fet_h"]), DARK)
        add(box(xs[k] + DRIVER[0] - 2.5, xs[k] + DRIVER[0] + 2.5, DRIVER[1] - 2.5, DRIVER[1] + 2.5, P["bt"],
                P["bt"] + P["drv_h"]), DARK)
        for hx, hy in HOLES:
            add(cyl(xs[k] + hx, hy, P["bt"], P["plate_z0"], 5.0), PEEK, name="standoff")

    # cold plate, channel, pedestals, AlN, TIM
    z0, z1 = P["plate_z0"], P["plate_z0"] + P["plate_t"]
    add(box(P["plate_x0"], P["plate_x1"], P["plate_y0"], P["plate_y1"], z0, z1), AL, 0.28, "plate", ez_up)
    w, (ya, yb) = P["ch_w"], P["ch_y"]
    cz0, cz1 = P["ch_z0"], P["ch_z0"] + P["ch_h"]
    xb = P["plate_x1"] - 8.0
    for poly in (box(P["plate_x0"], xb + w / 2, ya - w / 2, ya + w / 2, cz0, cz1),
                 box(P["plate_x0"], xb + w / 2, yb - w / 2, yb + w / 2, cz0, cz1),
                 box(xb - w / 2, xb + w / 2, ya - w / 2, yb + w / 2, cz0, cz1)):
        add(poly, WATER, 0.85, "coolant", ez_up)
    for yy in (ya, yb):
        add(cyl((cz0 + cz1) / 2, yy, P["plate_x0"] - 14.0, P["plate_x0"], 8.0, axis="x"), AL, 1.0, "fitting", ez_up)
    for k in range(n):
        for peds, h in ((PED_FET, P["fet_h"]), (PED_BANK, P["cap_bank_h"])):
            for px0, px1, py0, py1 in peds:
                zc = P["bt"] + h
                za, zal = zc + P["tim_t"], zc + P["tim_t"] + P["aln_t"]
                add(box(xs[k] + px0, xs[k] + px1, py0, py1, zal, z0), AL, 0.9, "pedestal", ez_up)
                add(box(xs[k] + px0, xs[k] + px1, py0, py1, za, zal), ALN, 1.0, "AlN", ez_up)
                add(box(xs[k] + px0 + 0.2, xs[k] + px1 - 0.2, py0 + 0.2, py1 - 0.2, zc, za), TIMC, 1.0, "TIM",
                    ez_up * 0.5)

    # laminated busbar
    zt = -P["term_dc_h"]
    zp0, zi0 = zt - P["bb_cu"], zt - P["bb_cu"] - P["bb_ins"]
    zn0 = zi0 - P["bb_cu"]
    y0, y1 = P["bb_y0"], P["bb_y1"]
    add(box(P["bb_x0"] - 14.0, P["bb_x1"] - 12.0, y0, y1, zp0, zt), CU, 1.0, "DC+", ez_dn * 0.6)
    add(box(P["bb_x0"], P["bb_x1"] + 2.0, y0 - 1.5, y1 + 1.5, zi0, zp0), INS, 0.75, "ins", ez_dn * 0.8)
    add(box(P["bb_x0"] + 12.0, P["bb_x1"] + 14.0, y0, y1, zn0, zi0), (0.72, 0.40, 0.22), 1.0, "DC-", ez_dn)
    for k in range(n):
        add(cyl(xs[k] + J2[0], J2[1], zi0, zt, P["boss_d"]), (0.72, 0.40, 0.22), 1.0, "boss", ez_dn)
        for (jx, jy), zh in ((J1, zp0), (J2, zn0)):
            add(cyl(xs[k] + jx, jy, zh - P["head_h"], zh, P["head_d"], n=6), STEEL, 1.0, "screw",
                ez_dn * (0.6 if zh == zp0 else 1.0))

    # phase leads
    for k in range(n):
        x3, y3, zl, t, wl = xs[k] + J3[0], J3[1], P["lead_z"][k], P["lead_t"], P["lead_w"]
        yl = P["lead_lane_y"]
        col = [(0.93, 0.62, 0.20), (0.62, 0.35, 0.70), (0.45, 0.45, 0.48)][k]
        for poly in (box(x3 - wl / 2, x3 + wl / 2, y3 - wl / 2, y3 + wl / 2, zl - t, -P["term_ac_h"]),
                     box(x3 - wl / 2, x3 + wl / 2, y3 - wl / 2, yl + wl / 2, zl - t, zl),
                     box(x3 - wl / 2, P["lead_x_end"], yl - wl / 2, yl + wl / 2, zl - t, zl)):
            add(poly, col, 1.0, "lead", ez_dn * 1.4)

    # aux board and FFC
    add(box(P["aux_x0"], P["aux_x1"], P["aux_y0"], P["aux_y1"], 0, P["bt"]), GREEN, 1.0, "aux")
    for dx, dy, w2, h2, hh in ((4, -18, 10, 8, 4), (4, -6, 8, 6, 4), (4, 2, 8, 6, 4), (4, 10, 8, 6, 4), (15, -10, 6, 6, 1),
                               (15, 4, 8, 12, 9)):
        add(box(P["aux_x0"] + dx, P["aux_x0"] + dx + w2, dy, dy + h2, P["bt"], P["bt"] + hh), DARK)
    for k in range(n):
        x4, yf, zz = xs[k] + J4[0], P["ffc_lane_y"], 4.6 + 0.35 * k
        add(box(x4 - 5.0, x4 + 5.0, J4[1] - 3.0, yf + 5.0, zz, zz + 0.3), INS, 1.0, "ffc")
        add(box(x4 - 5.0, P["aux_x0"] + 2.0, yf - 5.0, yf + 5.0, zz, zz + 0.3), INS, 1.0, "ffc")

    if housing:
        zb = min(P["lead_z"]) - P["lead_t"] - 0.5
        add(box(P["plate_x0"] - 16, P["lead_x_end"], P["plate_y0"] - 4, P["plate_y1"] + 4, zb - P["ins_t"], zb), INS,
            0.35, "ins sheet", ez_dn * 1.8)
        add(box(P["plate_x0"] - 16, P["lead_x_end"], P["plate_y0"] - 4, P["plate_y1"] + 4,
                P["housing_z1"] - P["housing_t"], P["housing_z1"]), (0.62, 0.65, 0.68), 0.45, "housing", ez_dn * 2.2)
    cat = {"board": "board", "part": "top", "terminal": "terminal", "standoff": "top"}
    cat.update(CAT)
    return [o + (cat.get(o[4], "top"),) for o in objs]


def shade(poly, col, lit):
    if not lit:
        return col
    nrm = np.cross(poly[1] - poly[0], poly[2] - poly[0])
    nn = np.linalg.norm(nrm)
    k = 0.55 + 0.45 * abs(nrm @ rb.LIGHT) / nn if nn > 0 else 0.8
    return np.clip(col * k, 0, 1)


def render(objs, elev, azim, path, title, show=None, labels=(), lims=None, size=(9, 5.2)):
    objs = [o for o in objs if show is None or o[5] in show]
    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    e, a = math.radians(elev), math.radians(azim)
    view = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    depth = [float(np.mean([np.mean(p, axis=0) for p in o[0]], axis=0) @ view) for o in objs]
    allp = np.vstack([np.vstack(o[0]) for o in objs])
    for z, i in enumerate(sorted(range(len(objs)), key=lambda i: depth[i])):
        polys, col, alpha, lit, name, cat = objs[i]
        order = sorted(range(len(polys)), key=lambda j: float(np.mean(polys[j], axis=0) @ view))
        if col.ndim == 1:
            fc = [np.r_[shade(polys[j], col, lit), alpha] for j in order]
        else:
            fc = [np.r_[shade(polys[j], col[j], lit), alpha] for j in order]
        ax.add_collection3d(Poly3DCollection([polys[j] for j in order], facecolors=fc,
                                             edgecolors=(0, 0, 0, 0.3 if alpha < 1 else 0.1),
                                             linewidths=0.15, zorder=z))
    lo, hi = (allp.min(axis=0), allp.max(axis=0)) if lims is None else (np.array(lims[0]), np.array(lims[1]))
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(hi - lo))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=10, family="serif")
    for (x, y, z, txt) in labels:
        ax.text(x, y, z, txt, fontsize=7.5, family="serif", zorder=10000,
                bbox=dict(fc="w", ec="none", alpha=0.75, pad=1))
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    full = build(0.0)
    render(full, 30, -60, os.path.join(OUT, "cell_iso.png"),
           "SPB cell (75 V, 3 legs): liquid cold plate (transparent), boards, busbar, phase leads, aux board",
           show={"plate", "board", "top", "terminal", "busbar", "leads", "aux", "ffc"},
           labels=((-30, -30, 16, "coolant in/out"), (95, 25, 10, "aux / control"), (130, -12, -12, "phase leads")))
    render(build(24.0), 24, -60, os.path.join(OUT, "cell_exploded.png"), "Exploded view",
           labels=((40, 30, 42, "cold plate, pedestals, AlN, TIM"), (40, 30, 3, "leg boards A, B, C"),
                   (40, 30, -24, "laminated DC busbar"), (120, -15, -40, "phase leads"),
                   (40, -40, -62, "insulation sheet, housing")))
    render(full, -35, -60, os.path.join(OUT, "cell_bottom.png"),
           "From below: laminated DC busbar on the DC terminals, phase leads on the AC terminals",
           show={"board", "terminal", "busbar", "leads"},
           labels=((-38, 22, -10, "DC+ tab to SM k$-$1"), (100, 22, -12, "DC$-$ tab to SM k+1"), (120, -12, -16, "A, B, C")))
