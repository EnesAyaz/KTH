"""
3D collision check of the assembled board: every footprint's 3D model (VRML, as resolved by dump_3d.py) is placed
like the KiCad 3D viewer does (model scale / rotation / offset, bottom parts turned 180 deg about y, footprint
rotation and position, bottom side below the board) and split into its shapes; each shape becomes an axis-aligned
box in board mm. Two parts collide when a shape of one overlaps a shape of the other by more than TOL in x, y and z.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\dump_3d.py          (writes plots/models3d.json)
    python scripts/check_3d_collisions.py [spb-bb-revb-dpt]   -> report on stdout, exit code 1 if anything collides

Also listed: parts without a 3D model (test points and mounting holes have no body by design).
"""
import json
import math
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 0.05                                       # mm overlap in every axis before it counts
NO_BODY = ("TP", "H")                            # bare pads / holes by design
_cache = {}


def read_wrl(path):
    """[points (n, 3) mm] per Shape of a VRML IndexedFaceSet file (KiCad units: 0.1 inch)"""
    if path in _cache:
        return _cache[path]
    if not os.path.exists(path):
        _cache[path] = None
        return None
    txt = open(path, errors="ignore").read()
    shapes = []
    for blk in re.split(r"\bShape\s*\{", txt)[1:]:
        pm = re.search(r"point\s*\[([^\]]*)\]", blk)
        if not pm:
            continue
        v = np.array([float(s) for s in re.split(r"[\s,]+", pm.group(1).strip()) if s])
        if len(v) >= 3:
            shapes.append(v[:len(v) // 3 * 3].reshape(-1, 3) * 2.54)
    _cache[path] = shapes
    return shapes


def rot(P, deg, axis):
    if not deg:
        return P
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    R = {"x": [[1, 0, 0], [0, c, -s], [0, s, c]], "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
         "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]
    return P @ np.array(R).T


def boxes(p, T):
    """world boxes (x0, y0, z0, x1, y1, z1) of one part, scene frame (x, y up, z up), board top at z = 0"""
    out = []
    for m in p["models"]:
        shapes = read_wrl(m["path"])
        if shapes is None:
            return None
        for P0 in shapes:
            P = P0 * np.array(m.get("scale", [1, 1, 1]))
            P = rot(rot(rot(P, m["rot"][0], "x"), m["rot"][1], "y"), m["rot"][2], "z")
            P = P + np.array(m["off"])
            if p["bottom"]:
                P = P * np.array([1, -1, -1])
            P = rot(P, p["rot"], "z")
            P = P + np.array([p["x"], -p["y"], -T if p["bottom"] else 0.0])
            lo, hi = P.min(axis=0), P.max(axis=0)
            out.append(tuple(lo) + tuple(hi))
    return out


def overlap(a, b):
    d = [min(a[i + 3], b[i + 3]) - max(a[i], b[i]) for i in range(3)]
    return d if all(x > TOL for x in d) else None


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-revb-dpt"
    D = json.load(open(os.path.join(ROOT, "hardware", name, "plots", "models3d.json")))
    T = D["thickness"]
    parts, nomodel, missing = [], [], []
    for p in D["parts"]:
        if not p["models"]:
            (nomodel if not p["ref"].startswith(NO_BODY) else []).append(p["ref"])
            continue
        b = boxes(p, T)
        if b is None:
            missing.append((p["ref"], [m["path"] for m in p["models"]]))
            continue
        parts.append((p["ref"], p["value"], b))
    hits = []
    for i in range(len(parts)):
        ra, va, ba = parts[i]
        A = [min(x[k] for x in ba) for k in range(3)] + [max(x[k + 3] for x in ba) for k in range(3)]
        for j in range(i + 1, len(parts)):
            rb, vb, bb = parts[j]
            B = [min(x[k] for x in bb) for k in range(3)] + [max(x[k + 3] for x in bb) for k in range(3)]
            if not overlap(A, B):
                continue
            worst = None
            for sa in ba:
                for sb in bb:
                    d = overlap(sa, sb)
                    if d and (worst is None or min(d) > min(worst)):
                        worst = d
            if worst:
                hits.append((ra, rb, worst, (A[2], A[5]), (B[2], B[5])))
    print("%s: %d parts with a 3D body checked" % (name, len(parts)))
    if missing:
        print("model file not found: %s" % "; ".join("%s %s" % m for m in missing))
    if nomodel:
        print("no 3D model: %s" % " ".join(sorted(nomodel)))
    if not hits:
        print("no 3D collisions (overlap > %.2f mm in x, y and z)" % TOL)
    for ra, rb, d, za, zb in sorted(hits):
        print("COLLISION %-6s %-6s overlap x %.2f y %.2f z %.2f mm   (z %.2f..%.2f / %.2f..%.2f)" % (
            ra, rb, d[0], d[1], d[2], za[0], za[1], zb[0], zb[1]))
    return 1 if hits or missing or nomodel else 0


if __name__ == "__main__":
    sys.exit(main())
