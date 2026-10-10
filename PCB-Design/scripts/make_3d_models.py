"""
Simple 3D models (boxes) for the parts of the SPB fabrication board that have no KiCad model, and for the lab
heatsink assembly. Each model is written as STEP (AP214, used by the KiCad STEP export) and as VRML (KiCad 3D viewer,
0.1 inch units).

    python scripts/make_3d_models.py  ->  hardware/spb-bb-fab/3d/*.step, *.wrl

Coordinates: mm, origin = footprint origin, z = 0 on the board top surface, x/y as in the footprint (y down in
KiCad footprints is y up in the 3D model, so y is negated here).
Dimensions:
  EPC2361      5.0 x 3.0 x 0.68 mm (datasheet: 3 x 5 mm; height from the tape pocket depth, approximate)
  2EDF7275K    5.0 x 5.0 x 1.0 mm  (PG-TFLGA-13-4, approximate)
  MGN1S1208MC  14.5 x 12.0 x 4.25 mm (Murata KDC_MGN1_B02 p. 17)
  heatsink     Fischer LAM 4 K 50 12 (40 x 40 x 50 mm hollow profile + 12 V fan), aluminium spreader 42 x 14 x 3 mm,
               0.6 mm pedestals over the cells, 0.5 mm insulating gap pads (0.4 mm compressed)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "hardware", "spb-bb-fab", "3d")
os.makedirs(OUT, exist_ok=True)


def faces_of_box(x0, y0, z0, x1, y1, z1):
    """corners (KiCad y down -> model y up) and 6 faces with vertex order CCW seen from outside."""
    ya, yb = -y1, -y0
    c = [(x0, ya, z0), (x1, ya, z0), (x1, yb, z0), (x0, yb, z0),
         (x0, ya, z1), (x1, ya, z1), (x1, yb, z1), (x0, yb, z1)]
    f = [((0, 3, 2, 1), (0, 0, -1)), ((4, 5, 6, 7), (0, 0, 1)), ((0, 1, 5, 4), (0, -1, 0)),
         ((1, 2, 6, 5), (1, 0, 0)), ((2, 3, 7, 6), (0, 1, 0)), ((3, 0, 4, 7), (-1, 0, 0))]
    return c, f


class Step:
    def __init__(self):
        self.lines = []
        self.n = 0

    def add(self, s):
        self.n += 1
        self.lines.append("#%d = %s;" % (self.n, s))
        return "#%d" % self.n


def fmt(v):
    return "%.6f" % v


def write_step(path, name, boxes):
    """boxes: list of (x0, y0, z0, x1, y1, z1, (r, g, b))."""
    S = Step()
    ctx_app = S.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    S.add("APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,%s)" % ctx_app)
    pctx = S.add("PRODUCT_CONTEXT('',%s,'mechanical')" % ctx_app)
    prod = S.add("PRODUCT('%s','%s','',(%s))" % (name, name, pctx))
    S.add("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(%s))" % prod)
    pdf = S.add("PRODUCT_DEFINITION_FORMATION('','',%s)" % prod)
    pdc = S.add("PRODUCT_DEFINITION_CONTEXT('part definition',%s,'design')" % ctx_app)
    pd = S.add("PRODUCT_DEFINITION('design','',%s,%s)" % (pdf, pdc))
    pds = S.add("PRODUCT_DEFINITION_SHAPE('','',%s)" % pd)
    mm = S.add("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
    rad = S.add("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
    sr = S.add("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
    unc = S.add("UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),%s,'distance_accuracy_value','confusion accuracy')" % mm)
    ctx = S.add("( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((%s)) "
                "GLOBAL_UNIT_ASSIGNED_CONTEXT((%s,%s,%s)) REPRESENTATION_CONTEXT('Context #1','3D Context') )"
                % (unc, mm, rad, sr))
    o = S.add("CARTESIAN_POINT('',(0.,0.,0.))")
    dz = S.add("DIRECTION('',(0.,0.,1.))")
    dx = S.add("DIRECTION('',(1.,0.,0.))")
    ax0 = S.add("AXIS2_PLACEMENT_3D('',%s,%s,%s)" % (o, dz, dx))
    solids, styled = [], []
    for bi, (x0, y0, z0, x1, y1, z1, rgb) in enumerate(boxes):
        c, f = faces_of_box(x0, y0, z0, x1, y1, z1)
        pts = [S.add("CARTESIAN_POINT('',(%s,%s,%s))" % tuple(fmt(v) for v in p)) for p in c]
        vps = [S.add("VERTEX_POINT('',%s)" % p) for p in pts]
        edges = {}

        def edge(a, b):
            k = (min(a, b), max(a, b))
            if k not in edges:
                pa, pb = c[k[0]], c[k[1]]
                d = [pb[i] - pa[i] for i in range(3)]
                ln = sum(v * v for v in d) ** 0.5
                dr = S.add("DIRECTION('',(%s,%s,%s))" % tuple(fmt(v / ln) for v in d))
                vv = S.add("VECTOR('',%s,%s)" % (dr, fmt(ln)))
                line = S.add("LINE('',%s,%s)" % (pts[k[0]], vv))
                edges[k] = S.add("EDGE_CURVE('',%s,%s,%s,.T.)" % (vps[k[0]], vps[k[1]], line))
            return edges[k], a < b

        faces = []
        for idx, n in f:
            oes = []
            for i in range(4):
                a, b = idx[i], idx[(i + 1) % 4]
                e, fwd = edge(a, b)
                oes.append(S.add("ORIENTED_EDGE('',*,*,%s,%s)" % (e, ".T." if fwd else ".F.")))
            loop = S.add("EDGE_LOOP('',(%s))" % ",".join(oes))
            bound = S.add("FACE_OUTER_BOUND('',%s,.T.)" % loop)
            nd = S.add("DIRECTION('',(%s,%s,%s))" % tuple(fmt(v) for v in n))
            p0 = c[idx[0]]
            p1 = c[idx[1]]
            rd = [p1[i] - p0[i] for i in range(3)]
            ln = sum(v * v for v in rd) ** 0.5
            rdd = S.add("DIRECTION('',(%s,%s,%s))" % tuple(fmt(v / ln) for v in rd))
            ax = S.add("AXIS2_PLACEMENT_3D('',%s,%s,%s)" % (pts[idx[0]], nd, rdd))
            pl = S.add("PLANE('',%s)" % ax)
            faces.append(S.add("ADVANCED_FACE('',(%s),%s,.T.)" % (bound, pl)))
        shell = S.add("CLOSED_SHELL('',(%s))" % ",".join(faces))
        solid = S.add("MANIFOLD_SOLID_BREP('%s_%d',%s)" % (name, bi, shell))
        solids.append(solid)
        col = S.add("COLOUR_RGB('',%s,%s,%s)" % tuple(fmt(v) for v in rgb))
        fac = S.add("FILL_AREA_STYLE_COLOUR('',%s)" % col)
        fas = S.add("FILL_AREA_STYLE('',(%s))" % fac)
        ssfa = S.add("SURFACE_STYLE_FILL_AREA(%s)" % fas)
        sss = S.add("SURFACE_SIDE_STYLE('',(%s))" % ssfa)
        ssu = S.add("SURFACE_STYLE_USAGE(.BOTH.,%s)" % sss)
        psa = S.add("PRESENTATION_STYLE_ASSIGNMENT((%s))" % ssu)
        styled.append(S.add("STYLED_ITEM('color',(%s),%s)" % (psa, solid)))
    rep = S.add("ADVANCED_BREP_SHAPE_REPRESENTATION('%s',(%s,%s),%s)" % (name, ax0, ",".join(solids), ctx))
    S.add("SHAPE_DEFINITION_REPRESENTATION(%s,%s)" % (pds, rep))
    S.add("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',(%s),%s)" % (",".join(styled), ctx))
    with open(path, "w") as fo:
        fo.write("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('%s'),'2;1');\n" % name)
        fo.write("FILE_NAME('%s','2026-10-09T00:00:00',('KTH'),('KTH'),'spb_fab','spb_fab','');\n"
                 % os.path.basename(path))
        fo.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\nENDSEC;\nDATA;\n")
        fo.write("\n".join(S.lines))
        fo.write("\nENDSEC;\nEND-ISO-10303-21;\n")


def write_wrl(path, boxes):
    k = 1 / 2.54
    out = ["#VRML V2.0 utf8"]
    for x0, y0, z0, x1, y1, z1, rgb in boxes:
        c, f = faces_of_box(x0, y0, z0, x1, y1, z1)
        pts = ", ".join("%.4f %.4f %.4f" % (p[0] * k, p[1] * k, p[2] * k) for p in c)
        idx = ", ".join("%d,%d,%d,%d,-1" % fi[0] for fi in f)
        out.append("Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f "
                   "specularColor 0.2 0.2 0.2 shininess 0.3 } }\n geometry IndexedFaceSet { solid TRUE "
                   "coord Coordinate { point [ %s ] } coordIndex [ %s ] } }" % (rgb + (pts, idx)))
    open(path, "w").write("\n".join(out) + "\n")


BLACK = (0.10, 0.10, 0.11)
SILVER = (0.78, 0.79, 0.80)
DARK = (0.20, 0.20, 0.22)
WHITE = (0.92, 0.92, 0.90)
ALU = (0.80, 0.82, 0.85)
PAD = (0.55, 0.62, 0.70)
FAN = (0.12, 0.12, 0.12)
MODELS = {
    "EPC2361": [(-2.5, -1.5, 0.0, 2.5, 1.5, 0.60, BLACK), (-2.4, -1.4, 0.60, 2.4, 1.4, 0.68, SILVER)],
    "2EDF7275K_PG-TFLGA-13-4": [(-2.5, -2.5, 0.0, 2.5, 2.5, 1.0, DARK)],
    "Murata_MGN1_SMD": [(-7.25, -6.0, 0.0, 7.25, 6.0, 4.25, WHITE)],
    # heatsink assembly, origin at the centre of the cells (board y = 6.1): gap pads over each cell, spreader
    # 42 x 14 x 3 mm, LAM 4 (40 x 50 x 40 mm, tube along y) and its fan at the far end
    "HS_LAM4K5012_assembly": [
        (-13.5, -4.0, 0.68, -5.5, 6.0, 1.08, PAD), (5.5, -4.0, 0.68, 13.5, 6.0, 1.08, PAD),
        (-13.5, -4.0, 1.08, -5.5, 6.0, 1.68, ALU), (5.5, -4.0, 1.08, 13.5, 6.0, 1.68, ALU),
        (-21.0, -6.95, 1.68, 21.0, 6.95, 4.68, ALU),
        (-21.0, -10.15, 1.68, -16.5, -6.95, 4.68, ALU), (16.5, -10.15, 1.68, 21.0, -6.95, 4.68, ALU),
        (-21.0, 6.95, 1.68, -16.5, 11.25, 4.68, ALU), (16.5, 6.95, 1.68, 21.0, 11.25, 4.68, ALU),
        (-20.0, -25.0, 4.68, 20.0, 25.0, 44.68, ALU),
        (-20.0, 25.0, 4.68, 20.0, 35.0, 44.68, FAN)],
}
if __name__ == "__main__":
    EPC3D = os.path.join(ROOT, "hardware", "epc2361-cell", "epc2361-cell.3dshapes")
    os.makedirs(EPC3D, exist_ok=True)
    for name, boxes in MODELS.items():
        d = EPC3D if name == "EPC2361" else OUT
        write_step(os.path.join(d, name + ".step"), name, boxes)
        write_wrl(os.path.join(d, name + ".wrl"), boxes)
        print("model", name)
