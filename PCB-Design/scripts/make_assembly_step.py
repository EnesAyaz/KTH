"""
Mechanical assembly STEP files (OpenCascade XCAF, colours kept) from the KiCad board STEPs:

    "C:\\Program Files\\KiCad\\7.0\\bin\\kicad-cli.exe" pcb export step --subst-models --user-origin 150x100mm ...
    %LOCALAPPDATA%\\kth3d\\Scripts\\python.exe scripts\\make_assembly_step.py
      -> hardware/assembly/spb-level-assembly.step   one 75 V level: PCB busbar + 3 load-test legs + hardware
         hardware/assembly/spb-stack-assembly.step   16 levels (1200 V), Cu braids between the stack lugs

STEP frame (KiCad STEP convention): x across the legs, y = -(KiCad y), z up; busbar top face (L1) at z = 0, leg-board
bottom at z = 6.5 (REDCUBE 74650174 height). Each board is ONE prototype, placed by reference (small files).
Hardware (envelopes, not manufacturer CAD): M4 x 8 screws + washers, nylon M2.5 x 6.5 mm standoffs, M6 ring lugs +
bolts, LEM HO 250-S envelope (37.8 x 15 x 33 mm, aperture for the 12 x 5 mm bar), Cu braids 8 x 1.5 mm.
Same numbers as scripts/render_3d.py.
"""
import math
import os

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.TopLoc import TopLoc_Location
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_ColorType, XCAFDoc_DocumentTool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "hardware", "assembly")
PITCH = 94.5
LEGS = (-PITCH, 0.0, PITCH)
Z_LEG = 6.5
LEVEL_DZ = 72.0
STEEL, NYLON, COPPER, LEMC = (0.62, 0.63, 0.66), (0.93, 0.92, 0.86), (0.85, 0.50, 0.25), (0.15, 0.15, 0.17)


def new_doc():
    app = XCAFApp_Application.GetApplication_s()
    doc = TDocStd_Document(TCollection_ExtendedString("XmlXCAF"))
    app.InitDocument(doc)
    return doc


def free_labels(st):
    seq = TDF_LabelSequence()
    st.GetFreeShapes(seq)
    return [seq.Value(i + 1) for i in range(seq.Length())]


def read_into(doc, st, path, name):
    before = set(l.Tag() for l in free_labels(st))
    r = STEPCAFControl_Reader()
    r.SetColorMode(True)
    r.SetNameMode(True)
    assert r.ReadFile(path) == IFSelect_RetDone, path
    assert r.Transfer(doc)
    new = [l for l in free_labels(st) if l.Tag() not in before]
    assert len(new) == 1, (path, len(new))
    TDataStd_Name.Set_s(new[0], TCollection_ExtendedString(name))
    return new[0]


def loc(dx=0.0, dy=0.0, dz=0.0):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(dx, dy, dz))
    return TopLoc_Location(t)


def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(min(x0, x1), min(y0, y1), min(z0, z1)), abs(x1 - x0), abs(y1 - y0),
                               abs(z1 - z0)).Shape()


def cyl(x, y, z0, z1, r, r_in=0.0):
    s = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()
    if r_in > 0:
        s = BRepAlgoAPI_Cut(s, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0 - 0.1), gp_Dir(0, 0, 1)), r_in,
                                                         z1 - z0 + 0.2).Shape()).Shape()
    return s


def hexagon(x, y, z0, z1, af, r_in=0.0):
    """hex nut / bolt head (across flats af), optional bore."""
    r = af / math.sqrt(3)
    poly = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        a = math.pi / 6 + k * math.pi / 3
        poly.Add(gp_Pnt(x + r * math.cos(a), y + r * math.sin(a), z0))
    poly.Close()
    s = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(0, 0, z1 - z0)).Shape()
    if r_in > 0:
        s = BRepAlgoAPI_Cut(s, cyl(x, y, z0 - 0.1, z1 + 0.1, r_in)).Shape()
    return s


def strap(p0, p1, w, h):
    """flat strap from p0 to p1 (STEP frame), width w along x-y normal, thickness h."""
    d = gp_Vec(gp_Pnt(*p0), gp_Pnt(*p1))
    L = d.Magnitude()
    t = gp_Trsf()
    t.SetDisplacement(gp_Ax3(), gp_Ax3(gp_Pnt(*p0), gp_Dir(d), gp_Dir(1, 0, 0)))
    return BRepBuilderAPI_Transform(box(-w / 2, -h / 2, 0.0, w / 2, h / 2, L), t, True).Shape()


class Asm:
    def __init__(self):
        self.doc = new_doc()
        self.st = XCAFDoc_DocumentTool.ShapeTool_s(self.doc.Main())
        self.ct = XCAFDoc_DocumentTool.ColorTool_s(self.doc.Main())

    def part(self, shape, name, rgb):
        lab = self.st.AddShape(shape, False)
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(name))
        self.ct.SetColor(lab, Quantity_Color(rgb[0], rgb[1], rgb[2], Quantity_TOC_RGB),
                         XCAFDoc_ColorType.XCAFDoc_ColorSurf)
        return lab

    def assembly(self, name):
        lab = self.st.NewShape()
        TDataStd_Name.Set_s(lab, TCollection_ExtendedString(name))
        return lab

    def add(self, assy, lab, dx=0.0, dy=0.0, dz=0.0):
        return self.st.AddComponent(assy, lab, loc(dx, dy, dz))

    def write(self, root, path):
        self.st.UpdateAssemblies()
        w = STEPCAFControl_Writer()
        w.SetColorMode(True)
        w.SetNameMode(True)
        assert w.Transfer(self.doc, STEPControl_AsIs)
        assert w.Write(path) == IFSelect_RetDone
        print("written", path, "%.1f MB" % (os.path.getsize(path) / 1e6))


def build_level(A):
    leg = read_into(A.doc, A.st, os.path.join(ROOT, "hardware", "spb-bb-revb-load", "fab", "spb-bb-revb-load.step"),
                    "leg board, load test (spb-bb-revb-load)")
    bus = read_into(A.doc, A.st, os.path.join(ROOT, "hardware", "spb-busbar", "fab", "spb-busbar.step"),
                    "PCB busbar (spb-busbar)")
    lvl = A.assembly("75 V level: busbar + legs a, b, c")
    A.add(lvl, bus, 0.0, 0.0, -1.6)                       # KiCad STEP: board bottom at z = 0 -> busbar top at 0
    screw = A.part(hexagon(0, 0, -1.6 - 3.6, -1.6 - 0.8, 7.0), "M4 x 8 screw head (DIN 933)", STEEL)
    washer = A.part(cyl(0, 0, -1.6 - 0.8, -1.6, 4.5, 2.15), "M4 washer", STEEL)
    stand = A.part(cyl(0, 0, 0.0, Z_LEG, 2.5, 1.35), "nylon standoff M2.5 x 6.5 mm", NYLON)
    lem = A.part(BRepAlgoAPI_Cut(box(-18.9, -(55.6 + 8.0), -14.0, 18.9, -(55.6 + 23.0), 19.0),
                                 box(-7.5, -(55.6 + 7.0), -1.0, 7.5, -(55.6 + 24.0), 9.0)).Shape(),
                 "LEM HO 250-S (envelope, approx.)", LEMC)
    for k, xl in enumerate(LEGS):
        A.add(lvl, leg, xl, 0.0, Z_LEG)
        for xt in (-6.0, 6.0):
            A.add(lvl, screw, xl + xt, 18.8, 0.0)
            A.add(lvl, washer, xl + xt, 18.8, 0.0)
        for hx in (-42.35, 42.35):
            A.add(lvl, stand, xl + hx, 22.0, 0.0)
        A.add(lvl, lem, xl, 0.0, Z_LEG + 1.6)
    ring = BRepAlgoAPI_Fuse(cyl(0, 0, 0.0, 2.0, 6.5), box(-4.0, 5.5, 0.4, 4.0, 22.0, 1.6)).Shape()
    lug = A.part(BRepAlgoAPI_Cut(ring, cyl(0, 0, -0.1, 2.1, 3.3)).Shape(), "M6 ring lug (stack)", COPPER)
    bolt = A.part(hexagon(0, 0, 2.0, 6.0, 10.0), "M6 bolt head", STEEL)
    nut = A.part(hexagon(0, 0, -1.6 - 5.0, -1.6, 10.0, 3.0), "M6 nut", STEEL)
    for x in (-12.0, 12.0):
        for p in (lug, bolt, nut):
            A.add(lvl, p, x, 37.0, 0.0)
    return lvl


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    A = Asm()
    lvl = build_level(A)
    A.write(lvl, os.path.join(OUT, "spb-level-assembly.step"))
    # 16 levels: same level assembly referenced 16 times + braids (DC+ lug of level k -> DC- lug of level k+1)
    S = Asm()
    lvl = build_level(S)
    stack = S.assembly("SPB 1200 V stack: 16 levels")
    for k in range(16):
        S.add(stack, lvl, 0.0, 0.0, k * LEVEL_DZ)
    braid = S.part(strap((-12.0, 37.0 + 14.0, 2.0), (12.0, 37.0 + 14.0, LEVEL_DZ), 8.0, 1.5),
                   "Cu braid 8 x 1.5 mm (level k DC+ -> level k+1 DC-)", COPPER)
    for k in range(15):
        S.add(stack, braid, 0.0, 0.0, k * LEVEL_DZ)
    S.write(stack, os.path.join(OUT, "spb-stack-assembly.step"))
