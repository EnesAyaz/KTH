"""
KiCad 7 schematic of the SPB leg fabrication board with wired connections, generated so that it matches the routed
PCB pin by pin (hardware/spb-bb-fab/pad_nets.json, written by scripts/dump_pad_nets.py, and parts.json).

    python scripts/make_kicad_sch.py  ->  hardware/spb-bb-fab/spb-bb-fab.kicad_sch, spb_fab.kicad_sym, lib tables
    kicad-cli sch export netlist ... ; python scripts/check_sch_vs_pcb.py <netlist>   (must report 0 mismatches)

Functional blocks are drawn with wires: power stage with DC-link rails, gate driver with input filters and the
turn-on / turn-off networks, the two isolated gate supplies. Connections between blocks use net labels with the PCB
net names (VDDA, SW, GH_L, ...). Measurement landings (TP, probe pads) are drawn as two-pin symbols with labels.
"""
import json
import os
import re
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HW = os.path.join(ROOT, "hardware", "spb-bb-fab")
SYMDIR = "C:/Program Files/KiCad/7.0/share/kicad/symbols"
NAME = "spb-bb-fab"
ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, "spb-bb-fab-root"))
G = 2.54


def uid(*k):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "spb-bb-fab/" + "/".join(str(x) for x in k)))


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


# ------------------------------------------------------------------ library symbols
def extract(lib, name):
    txt = open(os.path.join(SYMDIR, lib + ".kicad_sym"), encoding="utf-8").read()
    m = re.search(r'\n\s*\(symbol "%s"' % re.escape(name), txt)
    i = txt.index("(", m.start())
    depth = 0
    for j in range(i, len(txt)):
        if txt[j] == "(":
            depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0:
                break
    return txt[i:j + 1].replace('(symbol "%s"' % name, '(symbol "%s:%s"' % (lib, name), 1)


def pins_of(symtxt):
    out = {}
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(number "([^"]*)"', symtxt, re.S):
        out.setdefault(m.group(4), (float(m.group(1)), float(m.group(2)), int(m.group(3))))
    return out


def box_symbol(name, left, right, ref="U", w=15.24):
    n = max(len(left), len(right))
    h = (n + 1) * G
    top = (n - 1) * G / 2
    pins = []
    for side, lst in ((0, left), (1, right)):
        for k, p in enumerate(lst):
            if p is None:
                continue
            num, pname = p
            y = top - k * G
            x = -(w / 2 + G) if side == 0 else (w / 2 + G)
            pins.append('(pin passive line (at %.2f %.2f %d) (length 2.54) (name %s (effects (font (size 1.27 1.27)))) '
                        '(number %s (effects (font (size 1.27 1.27)))))' % (x, y, 0 if side == 0 else 180, q(pname), q(num)))
    return ('(symbol "spb_fab:%s" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)\n'
            ' (property "Reference" %s (at 0 %.2f 0) (effects (font (size 1.27 1.27))))\n'
            ' (property "Value" %s (at 0 %.2f 0) (effects (font (size 1.27 1.27))))\n'
            ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            ' (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            ' (symbol "%s_0_1" (rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.254) (type default)) '
            '(fill (type background))))\n'
            ' (symbol "%s_1_1" %s))') % (name, q(ref), h / 2 + 1.27, q(name), -h / 2 - 1.27, name,
                                          -w / 2, h / 2, w / 2, -h / 2, name, "\n  ".join(pins))


PROBE_SYM = '''(symbol "spb_fab:ProbeLanding" (pin_names (offset 0.5)) (in_bom no) (on_board yes)
 (property "Reference" "TP" (at 3.81 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
 (property "Value" "ProbeLanding" (at 3.81 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))
 (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (symbol "ProbeLanding_0_1" (rectangle (start -1.905 3.81) (end 1.905 -3.81) (stroke (width 0.254) (type default))
   (fill (type background)))
  (polyline (pts (xy -0.635 1.27) (xy 0 2.54) (xy 0.635 1.27)) (stroke (width 0.254) (type default)) (fill (type none))))
 (symbol "ProbeLanding_1_1"
  (pin passive line (at 0 6.35 270) (length 2.54) (name "SIG" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))
  (pin passive line (at 0 -6.35 90) (length 2.54) (name "GND" (effects (font (size 1 1)))) (number "2" (effects (font (size 1 1)))))))'''

CUSTOM = {
    "EPC2361": box_symbol("EPC2361", [("1", "G")], [("3", "D"), ("5", "D"), ("7", "D"), None, ("2", "S"), ("4", "S"),
                                                     ("6", "S")], "Q", 10.16),
    "2EDF7275K": box_symbol("2EDF7275K", [("7", "VDDI"), ("2", "INA"), ("3", "INB"), ("5", "DISABLE"), ("4", "SLDON"),
                                          ("6", "NC"), ("1", "GNDI")],
                            [("13", "VDDA"), ("12", "OUTA"), ("11", "GNDA"), None, ("10", "VDDB"), ("9", "OUTB"),
                             ("8", "GNDB")], "U", 17.78),
    "MGN1S1208MC": box_symbol("MGN1S1208MC", [("19", "+Vin"), ("20", "+Vin"), None, ("1", "-Vin"), ("2", "-Vin")],
                              [("11", "+Vout"), ("12", "+Vout"), None, ("9", "0V"), ("10", "0V")], "PS", 17.78),
    "TPS7A4901": box_symbol("TPS7A4901", [("8", "IN"), ("5", "EN"), None, ("4", "GND"), ("9", "EP")],
                            [("1", "OUT"), ("3", "NC"), ("2", "FB"), ("6", "NR/SS"), ("7", "DNC")], "U", 22.86),
    "TLV431": box_symbol("TLV431", [("1", "REF")], [("2", "CATHODE"), ("3", "ANODE")], "U", 20.32),
    "ProbeLanding": PROBE_SYM,
}
STD = [("Device", "R"), ("Device", "C"), ("Device", "D_Schottky"), ("Device", "LED"), ("Device", "Thermistor_NTC"),
       ("Mechanical", "MountingHole"), ("Connector_Generic", "Conn_01x01"),
       ("Connector_Generic", "Conn_02x03_Odd_Even"), ("Connector_Generic", "Conn_01x02")]
LIB = {}
for lib, nm in STD:
    LIB[lib + ":" + nm] = extract(lib, nm)
for k, s in CUSTOM.items():
    LIB["spb_fab:" + k] = s
PINS = {k: pins_of(v) for k, v in LIB.items()}

with open(os.path.join(HW, "spb_fab.kicad_sym"), "w", encoding="utf-8") as f:
    f.write("(kicad_symbol_lib (version 20220914) (generator spb_fab)\n")
    for k, s in CUSTOM.items():
        f.write(s.replace('(symbol "spb_fab:%s"' % k, '(symbol "%s"' % k, 1) + "\n")
    f.write(")\n")
open(os.path.join(HW, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (lib (name "spb_fab")(type "KiCad")(uri "${KIPRJMOD}/spb_fab.kicad_sym")(options "")(descr "SPB fab board symbols"))\n)\n')
open(os.path.join(HW, "fp-lib-table"), "w").write(
    '(fp_lib_table\n  (lib (name "spb_fab")(type "KiCad")(uri "${KIPRJMOD}/spb_fab.pretty")(options "")(descr "SPB fab board footprints"))\n'
    '  (lib (name "epc2361-cell")(type "KiCad")(uri "${KIPRJMOD}/../epc2361-cell/epc2361-cell.pretty")(options "")(descr "EPC2361 land pattern"))\n)\n')

# ------------------------------------------------------------------ parts and nets from the board
PADS = {r: (v, p) for r, v, p in json.load(open(os.path.join(HW, "pad_nets.json")))}
PARTS = {p["ref"]: p for p in json.load(open(os.path.join(HW, "parts.json")))}
SKIP = {"HS1"}                                   # board-only (heatsink)


def lib_id(ref):
    if ref.startswith("TP"):
        return "spb_fab:ProbeLanding"
    if ref.startswith("Q"):
        return "spb_fab:EPC2361"
    if ref == "U1":
        return "spb_fab:2EDF7275K"
    if ref.startswith("PS"):
        return "spb_fab:MGN1S1208MC"
    if ref in ("U2", "U3"):
        return "spb_fab:TPS7A4901"
    if ref in ("U4", "U5"):
        return "spb_fab:TLV431"
    if ref.startswith("RT"):
        return "Device:Thermistor_NTC"
    if ref.startswith("R"):
        return "Device:R"
    if ref.startswith("C"):
        return "Device:C"
    if ref in ("D1", "D2"):
        return "Device:D_Schottky"
    if ref.startswith("D"):
        return "Device:LED"
    if ref.startswith("H"):
        return "Mechanical:MountingHole"
    if ref == "J5":
        return "Connector_Generic:Conn_02x03_Odd_Even"
    if ref in ("J6", "J7"):
        return "Connector_Generic:Conn_01x02"
    return "Connector_Generic:Conn_01x01"


FPLIB = [("C_0805_2012Metric_Tight", "spb_fab"), ("C_1210_3225Metric_Tight", "spb_fab"), ("R_", "Resistor_SMD"),
         ("C_", "Capacitor_SMD"), ("D_SOD", "Diode_SMD"), ("LED_", "LED_SMD"), ("MSOP", "Package_SO"), ("HVSSOP", "Package_SO"),
         ("SOT-23", "Package_TO_SOT_SMD"), ("PinHeader", "Connector_PinHeader_2.54mm"),
         ("Wuerth", "TerminalBlock_Wuerth"), ("MountingHole", "MountingHole"), ("EPC2361", "epc2361-cell"),
         ("2EDF", "spb_fab"), ("Murata_MGN1", "spb_fab"), ("Probe_", "spb_fab")]


def fp_id(ref):
    fp = PARTS[ref]["footprint"]
    for pre, lib in FPLIB:
        if fp.startswith(pre):
            return lib + ":" + fp
    return fp


def net_of(ref, pin):
    return PADS[ref][1].get(pin, "")


# ------------------------------------------------------------------ drawing primitives
INST = {}          # ref -> (lib_id, x, y, rot)
WIRES = []         # ((x0, y0), (x1, y1))
LABELS = []        # (net, x, y, angle)
NOCON = []
TEXT = []


def rnd(v):
    return round(v / 0.01) * 0.01


def place(ref, x, y, rot=0):
    INST[ref] = (lib_id(ref), rnd(x), rnd(y), rot)


def pin_xy(ref, num):
    lid, X, Y, rot = INST[ref]
    px, py, ang = PINS[lid][num]
    import math
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    rx, ry = px * c - py * s, px * s + py * c
    return rnd(X + rx), rnd(Y - ry)


def pin_out(ref, num):
    """outward direction of the pin in screen coordinates (unit vector)."""
    lid, X, Y, rot = INST[ref]
    ang = (PINS[lid][num][2] + rot + 180) % 360
    return {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[ang]


def W(*pts):
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = (rnd(a[0]), rnd(a[1])), (rnd(b[0]), rnd(b[1]))
        if a != b:
            WIRES.append((a, b))


def LBL(net, x, y, d=(1, 0)):
    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[d]
    LABELS.append((net, rnd(x), rnd(y), ang))


def plabel(ref, num, net=None, length=2.54):
    """short stub from the pin and a net label with the PCB net name."""
    net = net or net_of(ref, num)
    x, y = pin_xy(ref, num)
    dx, dy = pin_out(ref, num)
    if not net:
        NOCON.append((x, y))
        return
    ex, ey = x + dx * length, y + dy * length
    W((x, y), (ex, ey))
    LBL(net, ex, ey, (dx, dy))


def vert(ref, x, yc, top_net):
    """2-pin part vertical, the pin carrying top_net on top."""
    lid = lib_id(ref)
    if lid in ("Device:LED", "Device:D_Schottky"):        # pin 1 = K
        rot = 90 if net_of(ref, "2") == top_net else 270
    else:
        rot = 0 if net_of(ref, "1") == top_net else 180
    place(ref, x, yc, rot)
    a, b = pin_xy(ref, "1"), pin_xy(ref, "2")
    return (a, b) if a[1] < b[1] else (b, a)


def horiz(ref, xc, y, left_net):
    lid = lib_id(ref)
    if lid in ("Device:LED", "Device:D_Schottky"):
        rot = 0 if net_of(ref, "1") == left_net else 180
    else:
        rot = 90 if net_of(ref, "1") == left_net else 270
    place(ref, xc, y, rot)
    a, b = pin_xy(ref, "1"), pin_xy(ref, "2")
    return (a, b) if a[0] < b[0] else (b, a)


def T(s, x, y, size=2.0, bold=True):
    TEXT.append((s, x, y, size, bold))


# ================================================================== 1 power stage
YP, YS, YN = 40.64, 96.52, 152.4
T("POWER STAGE AND DC LINK  (Q1/Q3 left cell, Q2/Q4 right cell; Kelvin = source pad 2 end, see notes)", 25.4, 30.48)
place("J1", 25.4, YP, 180)
place("J2", 25.4, YN, 180)
xs = []
for k in range(36):
    ref = "C%d" % (k + 1)
    x = 40.64 + 7.62 * k
    top, bot = vert(ref, x, YS, "DCP")
    W((x, YP), top)
    W(bot, (x, YN))
    xs.append(x)
T("C1-C12: 1 uF 100 V X7S 0805 local (6 per cell at the HS drains)   C13-C36: 10 uF 100 V X7S 1210 bank", 40.64, 165.1,
  1.5, False)
for ref, X, Y, hs in (("Q1", 342.9, 68.58, True), ("Q2", 393.7, 68.58, True), ("Q3", 342.9, 124.46, False),
                      ("Q4", 393.7, 124.46, False)):
    place(ref, X, Y)
    xb = X + 10.16
    for n in ("3", "5", "7", "2", "4", "6"):
        px, py = pin_xy(ref, n)
        W((px, py), (xb, py))
    W((xb, Y - 7.62), (xb, Y - 2.54))
    W((xb, Y + 2.54), (xb, Y + 7.62))
    if hs:
        W((xb, Y - 7.62), (xb, YP))
        W((xb, Y + 7.62), (xb, YS))
    else:
        W((xb, Y - 7.62), (xb, YS))
        W((xb, Y + 7.62), (xb, YN))
    plabel(ref, "1")
place("J3", 426.72, YS)
place("J4", 426.72, YS + 7.62)
j3, j4 = pin_xy("J3", "1"), pin_xy("J4", "1")
W((353.06, YS), j3)
W(j4, (416.56, j4[1]), (416.56, YS))
# DC-link indicator, bleeder and landing
x = 436.88
t, b = vert("R37", x, 50.8, "DCP")
W((x, YP), t)
t2, b2 = vert("R38", x, 63.5, "HVA")
W(b, t2)
t3, b3 = vert("D8", x, 76.2, "HVB")
W(b2, t3)
W(b3, (x, YN))
t, b = vert("R39", 447.04, YS, "DCP")
W((447.04, YP), t)
W(b, (447.04, YN))
place("TP16", 457.2, YS)
W((457.2, YP), pin_xy("TP16", "1"))
W(pin_xy("TP16", "2"), (457.2, YN))
W(pin_xy("J1", "1"), (457.2, YP))
W(pin_xy("J2", "1"), (457.2, YN))
LBL("DCP", 30.48, YP, (0, -1))
LBL("DCN", 30.48, YN, (0, 1))
T("DC+ (DCP)", 33.02, 38.1, 1.5, False)
T("DC- (DCN)", 33.02, 157.48, 1.5, False)
W((375.92, YS), (375.92, YS - 2.54))
LBL("SW", 375.92, YS - 2.54, (0, -1))
T("D8: DC link present, R39: 100 k bleeder", 431.8, 160.02, 1.5, False)
# NTC and its connector (DC- domain)
t, b = vert("RT1", 482.6, 68.58, "NTC")
LBL("NTC", t[0], t[1] - 2.54, (0, -1))
W(t, (t[0], t[1] - 2.54))
LBL("DCN", b[0], b[1] + 2.54, (0, 1))
W(b, (b[0], b[1] + 2.54))
place("J6", 500.38, 68.58)
plabel("J6", "1")
plabel("J6", "2")
T("NTC (on the right HS cell, DC- referenced) and J6: LS domain, high voltage", 474.98, 50.8, 1.5, False)

# ================================================================== 2 measurement landings
T("MEASUREMENT LANDINGS (probe pads: tip SIG, spring ground GND at 2.5 / 5.0 mm)", 25.4, 185.42)
for k in range(1, 17):
    if k == 16:
        continue
    ref = "TP%d" % k
    X = 30.48 + 22.86 * (k - 1)
    place(ref, X, 203.2)
    plabel(ref, "1")
    plabel(ref, "2")
T("TP1/TP5 D: Vds Q3/Q4   TP2/TP6 K: vKS (Kelvin vs power source)   TP3/TP7 G: Vgs Q3/Q4   TP4/TP8 H: Vgs Q1/Q2 "
  "(isolated probe)   TP9-11 / TP12-14: ISO, VDD, S of supply A / B   TP15: 12 V   TP16: DC link", 25.4, 223.52, 1.5,
  False)

# ================================================================== 3 gate driver
YD = 279.4
T("GATE DRIVER U1 (2EDF7275K): input filters, VDDI, separate turn-on / turn-off networks, local decoupling", 25.4,
  248.92)
place("J5", 96.52, YD)
for n in ("1", "2", "3", "4", "5", "6"):
    plabel("J5", n)
place("U1", 190.5, YD)
ina, inb = pin_xy("U1", "2"), pin_xy("U1", "3")
# PWM_H -> R9 -> INA, C104 to GNDI, R35 pull-down
LBL("PWM_H", 134.62, ina[1], (-1, 0))
l, r = horiz("R9", 149.86, ina[1], "PWM_H")
W((134.62, ina[1]), l)
W(r, ina)
t, b = vert("R35", 139.7, ina[1] - 10.16, "GNDI")
W(b, (139.7, ina[1]))
LBL("GNDI", t[0], t[1] - 2.54, (0, -1))
W(t, (t[0], t[1] - 2.54))
t, b = vert("C104", 160.02, ina[1] - 10.16, "GNDI")
W(b, (160.02, ina[1]))
LBL("GNDI", t[0], t[1] - 2.54, (0, -1))
W(t, (t[0], t[1] - 2.54))
# PWM_L -> R10 -> INB, C105, R36
LBL("PWM_L", 134.62, inb[1], (-1, 0))
l, r = horiz("R10", 149.86, inb[1], "PWM_L")
W((134.62, inb[1]), l)
W(r, inb)
t, b = vert("R36", 142.24, inb[1] + 10.16, "PWM_L")
W((142.24, inb[1]), t)
LBL("GNDI", b[0], b[1] + 2.54, (0, 1))
W(b, (b[0], b[1] + 2.54))
t, b = vert("C105", 162.56, inb[1] + 10.16, "INB")
W((162.56, inb[1]), t)
LBL("GNDI", b[0], b[1] + 2.54, (0, 1))
W(b, (b[0], b[1] + 2.54))
# VDDI from +12 V (SLDO on), DISABLE, SLDON, GNDI
vddi = pin_xy("U1", "7")
W(vddi, (166.37, vddi[1]))
t, b = vert("R11", 166.37, vddi[1] - 10.16, "+12V")
W(b, (166.37, vddi[1]))
LBL("+12V", t[0], t[1] - 2.54, (0, -1))
W(t, (t[0], t[1] - 2.54))
t, b = vert("C106", 176.53, vddi[1] - 10.16, "GNDI")
W(b, (176.53, vddi[1]))
LBL("GNDI", t[0], t[1] - 2.54, (0, -1))
W(t, (t[0], t[1] - 2.54))
for n, net in (("5", "DIS"), ("4", "GNDI"), ("1", "GNDI")):
    p = pin_xy("U1", n)
    W(p, (172.72, p[1]))
    LBL(net, 172.72, p[1], (-1, 0))
NOCON.append(pin_xy("U1", "6"))
T("SLDON = GNDI: input-side LDO on", 154.94, YD + 27.94, 1.27, False)
# outputs: OUT -> R_ON || (D + R_OFF) -> star -> R_G,i
for ch, out_pin, vdd_pin, vee_pin, ron, roff, dd, star, rgi_a, rgi_b, dy, vdd, vee, sref, ca, cb in (
        ("A", "12", "13", "11", "R5", "R6", "D1", "GH_STAR", "R1", "R2", -1, "VDDA", "VEEA", "SW", "C100", "C101"),
        ("B", "9", "10", "8", "R7", "R8", "D2", "GL_STAR", "R3", "R4", 1, "VDDB", "VEEB", "DCN", "C103", "C102")):
    o = pin_xy("U1", out_pin)
    plabel("U1", vdd_pin, vdd)
    plabel("U1", vee_pin, vee)
    yo, yd = o[1], o[1] + dy * 7.62
    l, r = horiz(ron, 213.36, yo, "OUT" + ch)
    W(o, l)
    W(r, (238.76, yo))
    W((205.74, yo), (205.74, yd))
    l, r = horiz(dd, 213.36, yd, "OUT" + ch)
    W((205.74, yd), l)
    l2, r2 = horiz(roff, 226.06, yd, "OFF" + ch)
    W(r, l2)
    W(r2, (233.68, yd), (233.68, yo))
    # star
    y1, y2 = (yo - 5.08, yo + 5.08) if ch == "A" else (yo + 5.08, yo + 12.7)
    W((238.76, yo), (238.76, y1))
    W((238.76, yo), (238.76, y2)) if ch == "A" else W((238.76, y1), (238.76, y2))
    # gate pull-down at the star (10 k to the Kelvin source)
    pd = "R41" if ch == "A" else "R42"
    if ch == "A":
        t, b = vert(pd, 238.76, y1 - 6.35, sref)
        W(b, (238.76, y1))
        W(t, (t[0], t[1] - 2.54))
        LBL(sref, t[0], t[1] - 2.54, (0, -1))
    else:
        t, b = vert(pd, 238.76, y2 + 6.35, star)
        W((238.76, y2), t)
        W(b, (b[0], b[1] + 2.54))
        LBL(sref, b[0], b[1] + 2.54, (0, 1))
    for rr, yy in ((rgi_a, y1), (rgi_b, y2)):
        l, r = horiz(rr, 246.38, yy, star)
        W((238.76, yy), l)
        gnet = [n for n in (net_of(rr, "1"), net_of(rr, "2")) if n != star][0]
        W(r, (r[0] + 2.54, r[1]))
        LBL(gnet, r[0] + 2.54, r[1], (1, 0))
    # local decoupling: VDD - S - VEE
    xc = 261.62 if ch == "A" else 271.78
    yc = yo - 2.54 if ch == "A" else yo + 2.54
    t, b = vert(ca, xc, yc - 6.35, vdd if ch == "A" else vdd)
    t2, b2 = vert(cb, xc, yc + 6.35, sref)
    W(b, t2)
    W(t, (t[0], t[1] - 2.54))
    LBL(vdd, t[0], t[1] - 2.54, (0, -1))
    W(b2, (b2[0], b2[1] + 2.54))
    LBL(vee, b2[0], b2[1] + 2.54, (0, 1))
    mid = (xc, (b[1] + t2[1]) / 2)
    W(mid, (xc + 5.08, mid[1]))
    LBL(sref, xc + 5.08, mid[1], (1, 0))
T("R_ON (R5/R7) 0.75 R, R_OFF (R6/R8) 0 R, R_G,i (R1-R4) 0.5 R: 2.0 R on / 0.5 R + diode off per transistor",
  154.94, YD + 30.48, 1.27, False)

# ================================================================== 4 gate supplies
for ch, Y in (("A", 254.0), ("B", 330.2)):
    X0 = 330.2
    ps, cin, ldo, r1, r2, cout, rb, sh, cs1, cs2, c12, rli, dli, rlv, dlv = {
        "A": ("PS1", "C107", "U2", "R12", "R13", "C108", "R14", "U4", "C109", "C110", "C111", "R30", "D3", "R31",
              "D4"),
        "B": ("PS2", "C112", "U3", "R15", "R16", "C113", "R17", "U5", "C114", "C115", "C116", "R32", "D5", "R33",
              "D6")}[ch]
    iso, vdd, vee, s, adj = ("ISOA_P", "VDDA", "VEEA", "SW", "ADJA") if ch == "A" else ("ISOB_P", "VDDB", "VEEB",
                                                                                       "DCN", "ADJB")
    T("GATE SUPPLY %s: MGN1S1208MC 12 V -> 8 V iso, TPS7A4901 6.29 V, TLV431 sets S = VEE + 1.24 V  (S = %s Kelvin)"
      % (ch, s), X0 - 30.48, Y - 17.78)
    place(ps, X0, Y)
    for n, xx in (("19", None), ("20", None), ("1", None), ("2", None), ("11", None), ("12", None), ("9", None),
                  ("10", None)):
        p = pin_xy(ps, n)
        W(p, (p[0] + (2.54 if p[0] > X0 else -2.54), p[1]))
    xl, xr = X0 - 13.97, X0 + 13.97
    W((xl, Y - 5.08), (xl, Y - 2.54))
    W((xl, Y + 2.54), (xl, Y + 5.08))
    W((xr, Y - 5.08), (xr, Y - 2.54))
    W((xr, Y + 2.54), (xr, Y + 5.08))
    W((xl, Y - 5.08), (X0 - 27.94, Y - 5.08))
    W((xl, Y + 5.08), (X0 - 27.94, Y + 5.08))
    LBL("+12V", X0 - 27.94, Y - 5.08, (-1, 0))
    LBL("GNDI", X0 - 27.94, Y + 5.08, (-1, 0))
    t, b = vert(c12, X0 - 22.86, Y, "+12V")
    W((X0 - 22.86, Y - 5.08), t)
    W(b, (X0 - 22.86, Y + 5.08))
    W((X0 + 17.78, Y - 5.08), (X0 + 17.78, Y - 7.62))
    LBL(iso, X0 + 17.78, Y - 7.62, (0, -1))
    YV = Y + 20.32
    W((xr, Y + 5.08), (xr, YV))
    xend = X0 + 172.72
    W((xr, YV), (xend, YV))
    LBL(vee, xend, YV, (1, 0))
    place(ldo, X0 + 55.88, Y)
    W((xr, Y - 5.08), pin_xy(ldo, "8"))
    W(pin_xy(ldo, "5"), (X0 + 38.1, Y - 2.54), (X0 + 38.1, Y - 5.08))
    W(pin_xy(ldo, "4"), (X0 + 36.83, Y + 2.54), (X0 + 36.83, YV))
    W(pin_xy(ldo, "9"), (X0 + 36.83, Y + 5.08))
    for n in ("3", "6", "7"):
        NOCON.append(pin_xy(ldo, n))
    t, b = vert(cin, X0 + 22.86, Y + 7.62, iso)
    W((X0 + 22.86, Y - 5.08), t)
    W(b, (X0 + 22.86, YV))
    t, b = vert(rli, X0 + 30.48, Y + 1.27, iso)
    W((X0 + 30.48, Y - 5.08), t)
    t2, b2 = vert(dli, X0 + 30.48, Y + 12.7, "LEDA_ISO" + ch)
    W(b, t2)
    W(b2, (X0 + 30.48, YV))
    out = pin_xy(ldo, "1")
    W(out, (xend, Y - 5.08))
    LBL(vdd, xend, Y - 5.08, (1, 0))
    fb = pin_xy(ldo, "2")
    xd = X0 + 86.36
    W(fb, (X0 + 81.28, fb[1]), (X0 + 81.28, Y + 5.08), (xd, Y + 5.08))
    t, b = vert(r1, xd, Y + 1.27, vdd)
    W((xd, Y - 5.08), t)
    t2, b2 = vert(r2, xd, Y + 10.16, adj)
    W((xd, Y + 5.08), t2)
    W(b2, (xd, YV))
    t, b = vert(cout, X0 + 96.52, Y + 7.62, vdd)
    W((X0 + 96.52, Y - 5.08), t)
    W(b, (X0 + 96.52, YV))
    t, b = vert(rlv, X0 + 104.14, Y + 1.27, vdd)
    W((X0 + 104.14, Y - 5.08), t)
    t2, b2 = vert(dlv, X0 + 104.14, Y + 12.7, "LEDA_VDD" + ch)
    W(b, t2)
    W(b2, (X0 + 104.14, YV))
    t, b = vert(rb, X0 + 111.76, Y + 2.54, vdd)
    W((X0 + 111.76, Y - 5.08), t)
    W(b, (X0 + 111.76, Y + 10.16))
    xu = X0 + 132.08
    place(sh, xu, Y + 11.43)
    ref_p, k_p, a_p = pin_xy(sh, "1"), pin_xy(sh, "2"), pin_xy(sh, "3")
    W((X0 + 111.76, Y + 10.16), ref_p)
    W((X0 + 116.84, Y + 10.16), (X0 + 116.84, Y + 6.35), (X0 + 149.86, Y + 6.35), (X0 + 149.86, k_p[1]), k_p)
    W(a_p, (X0 + 152.4, a_p[1]), (X0 + 152.4, YV))
    W((X0 + 149.86, Y + 6.35), (X0 + 170.18, Y + 6.35))
    LBL(s, X0 + 170.18, Y + 6.35, (1, 0))
    t, b = vert(cs1, X0 + 157.48, Y + 1.27, vdd)
    W((X0 + 157.48, Y - 5.08), t)
    W(b, (X0 + 157.48, Y + 6.35))
    t, b = vert(cs2, X0 + 165.1, Y + 12.7, s)
    W((X0 + 165.1, Y + 6.35), t)
    W(b, (X0 + 165.1, YV))

# ================================================================== 5 primary misc, mechanical
T("PRIMARY: fan connector, 12 V LED", 25.4, 330.2)
place("J7", 50.8, 345.44)
plabel("J7", "1")
plabel("J7", "2")
t, b = vert("R34", 76.2, 340.36, "+12V")
t2, b2 = vert("D7", 76.2, 353.06, "LEDA_12V")
W(b, t2)
W(t, (t[0], t[1] - 2.54))
LBL("+12V", t[0], t[1] - 2.54, (0, -1))
W(b2, (b2[0], b2[1] + 2.54))
LBL("GNDI", b2[0], b2[1] + 2.54, (0, 1))
T("MOUNTING: H1-H4 board corners, H5-H8 heatsink (Fischer LAM 4 K 50 12 on an Al spreader, board-only item HS1)",
  25.4, 375.92)
for k in range(1, 9):
    place("H%d" % k, 30.48 + 12.7 * (k - 1), 386.08)

notes = [
    "Nets: DCP = DC+, DCN = DC-, SW = switch node.  The high-side gate reference S_A is the SW net via the Kelvin "
    "traces (source pad 2 of Q1/Q2), the low-side reference S_B is the DCN net via the Kelvin traces of Q3/Q4.",
    "Kelvin routing (PCB): Q1/Q2 pad 2 -> L2 collector -> L4 return under the L3 gate trunk -> C100/C101 node; "
    "Q3/Q4 pad 2 -> L2 collector -> C102/C103 node.  The schematic shows them as SW / DCN.",
    "U2/U3 TPS7A4901DGNR: EN tied to IN, NR/SS open (CNR = 0 allowed), DNC and NC open, exposed pad to VEE; VOUT = 1.185 V (1 + R_top/R_bot).",
    "TP1-TP16 are probe landings (copper pads, no part).  TP2/TP6 measure Kelvin vs power-source copper of the "
    "same net (di/dt sensing).  J6 and all TPs in supply A/B are in high-voltage domains.",
]
for k, t in enumerate(notes):
    T(t, 25.4, 406.4 + 5.08 * k, 1.5, False)

missing = set(r for r in PADS if r not in SKIP) - set(INST)
assert not missing, sorted(missing)

# ------------------------------------------------------------------ split wires at T points (KiCad connects wires
# only at their end points; the editor splits a wire when a junction is placed, a generated file must do it itself)
def _interior(p, a, b):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False


_pts = set()
for a, b in WIRES:
    _pts.add(a)
    _pts.add(b)
for ref in INST:
    for n in PINS[INST[ref][0]]:
        _pts.add(pin_xy(ref, n))
changed = True
while changed:
    changed = False
    new_w = []
    for a, b in WIRES:
        cut = sorted((p for p in _pts if _interior(p, a, b)), key=lambda p: abs(p[0] - a[0]) + abs(p[1] - a[1]))
        if cut:
            chain = [a] + cut + [b]
            new_w += list(zip(chain[:-1], chain[1:]))
            changed = True
        else:
            new_w.append((a, b))
    WIRES[:] = new_w

# ------------------------------------------------------------------ junctions
ends = {}
for a, b in WIRES:
    ends[a] = ends.get(a, 0) + 1
    ends[b] = ends.get(b, 0) + 1
pinpts = {}
for ref in INST:
    for n in PINS[INST[ref][0]]:
        p = pin_xy(ref, n)
        pinpts[p] = pinpts.get(p, 0) + 1


def on_interior(p, a, b):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False


JUNC = set()
for p, n in ends.items():
    k = n + pinpts.get(p, 0)
    if k >= 3:
        JUNC.add(p)

# ------------------------------------------------------------------ write
out = ['(kicad_sch (version 20230121) (generator eeschema)', ' (uuid %s)' % ROOT_UUID, ' (paper "A1")',
       ' (title_block (title "SPB leg building block, Rev A") (date "2026-10-09") (rev "A") (company "KTH")'
       ' (comment 1 "2 x EPC2361 per switch, 2EDF7275K, split rail +5.05/-1.24 V, DPT measurement landings")'
       ' (comment 2 "generated by scripts/make_kicad_sch.py; netlist identical to the PCB (check_sch_vs_pcb.py)"))',
       ' (lib_symbols']
for k, s in LIB.items():
    out.append(s)
out.append(' )')
for i, (a, b) in enumerate(WIRES):
    out.append(' (wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type default)) (uuid %s))'
               % (a[0], a[1], b[0], b[1], uid("w", i, a, b)))
for p in sorted(JUNC):
    out.append(' (junction (at %.2f %.2f) (diameter 0) (color 0 0 0 0) (uuid %s))' % (p[0], p[1], uid("j", p)))
for i, p in enumerate(NOCON):
    out.append(' (no_connect (at %.2f %.2f) (uuid %s))' % (p[0], p[1], uid("nc", i, p)))
for i, (net, x, y, ang) in enumerate(LABELS):
    just = "left bottom" if ang in (0, 90) else "right bottom"
    out.append(' (label %s (at %.2f %.2f %d) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify %s)) '
               '(uuid %s))' % (q(net), x, y, ang, just, uid("l", i, net, x, y)))
for i, (s, x, y, size, bold) in enumerate(TEXT):
    out.append(' (text %s (at %.2f %.2f 0) (effects (font (size %.2f %.2f)%s) (justify left bottom)) (uuid %s))'
               % (q(s), x, y, size, size, " bold" if bold else "", uid("t", i)))
for ref, (lid, X, Y, rot) in sorted(INST.items()):
    val, pads = PADS[ref]
    p = PARTS[ref]
    short = val.split(" (")[0] if ref[0] in "RCD" else val
    short = re.sub(r" (0402|0603|0805|1206|1210)$", "", short)
    if ref == "J5":
        short = "lab header 2x3"
    elif ref == "J6":
        short = "NTC, DC- domain"
    elif ref == "J7":
        short = "fan 12 V"
    elif ref.startswith("H"):
        short = "M2.5"
    two = lid in ("Device:R", "Device:C", "Device:Thermistor_NTC", "Device:D_Schottky", "Device:LED")
    vertical = rot in (0, 180) if lid in ("Device:R", "Device:C", "Device:Thermistor_NTC") else rot in (90, 270)
    if lid.startswith("spb_fab") and lid != "spb_fab:ProbeLanding":
        top = max(abs(py) for _, py, _ in PINS[lid].values()) + 2.54
        geo = {"Reference": (X, Y - top - 1.27, 0), "Value": (X, Y + top + 2.54, 0)}
    elif lid == "spb_fab:ProbeLanding":
        geo = {"Reference": (X + 2.54, Y - 1.27, 0), "Value": (X + 2.54, Y + 1.27, 0)}
    elif two and vertical:
        geo = {"Reference": (X - (3.4 if lid == "Device:C" else 2.6), Y, 90),
               "Value": (X + (3.4 if lid == "Device:C" else 2.6), Y, 90)}
    elif two and ref == "R9":
        geo = {"Reference": (X, Y - 5.6, 0), "Value": (X, Y - 2.8, 0)}
    elif two and ref == "R10":
        geo = {"Reference": (X, Y + 2.8, 0), "Value": (X, Y + 5.6, 0)}
    elif two:
        geo = {"Reference": (X, Y - 2.8, 0), "Value": (X, Y + 2.8, 0)}
    else:
        geo = {"Reference": (X, Y - 5.0, 0), "Value": (X, Y + 5.5, 0)}
    pl = []
    for pn, pv in (("Reference", ref), ("Value", short), ("Footprint", fp_id(ref)), ("Datasheet", "~"),
                   ("MPN", p.get("mpn", "")), ("Description", val)):
        gx, gy, ga = geo.get(pn, (X, Y, 0))
        ga = (ga - rot) % 180                    # KiCad adds the symbol rotation to the field angle
        hide = " hide" if pn not in ("Reference", "Value") else ""
        just = " (justify left)" if lid == "spb_fab:ProbeLanding" and pn in ("Reference", "Value") else ""
        pl.append('(property %s %s (at %.2f %.2f %d) (effects (font (size 1.27 1.27))%s%s))'
                  % (q(pn), q(pv), gx, gy, ga, just, hide))
    pinlist = " ".join('(pin %s (uuid %s))' % (q(n), uid(ref, "pin", n)) for n in sorted(PINS[lid]))
    out.append(' (symbol (lib_id %s) (at %.2f %.2f %d) (unit 1) (in_bom %s) (on_board yes) (dnp no) (uuid %s)\n  %s\n'
               '  %s\n  (instances (project %s (path "/%s" (reference %s) (unit 1)))))'
               % (q(lid), X, Y, rot, "no" if ref.startswith(("H", "TP")) else "yes", uid(ref), "\n  ".join(pl),
                  pinlist, q(NAME), ROOT_UUID, q(ref)))
out.append(' (sheet_instances (path "/" (page "1")))')
out.append(')')
path = os.path.join(HW, NAME + ".kicad_sch")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("written", path, len(INST), "symbols", len(WIRES), "wires", len(JUNC), "junctions", len(LABELS), "labels")
