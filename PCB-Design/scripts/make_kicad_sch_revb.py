"""
KiCad 7 schematic of the Rev B SPB leg board (4 x EPC2361 per switch, 2 x 2EDF7275K), generated so that it matches
the routed PCB pin by pin (hardware/<board>/pad_nets.json from scripts/dump_pad_nets.py, and parts.json).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\dump_pad_nets.py spb-bb-revb
    python scripts/make_kicad_sch_revb.py spb-bb-revb-dpt  ->  hardware/spb-bb-revb-dpt/spb-bb-revb-dpt.kicad_sch, spb_fab.kicad_sym, sym-lib-table
    kicad-cli sch export netlist ... ; python scripts/check_sch_vs_pcb.py <netlist> spb-bb-revb-dpt   (0 problems)

Parts are found by the nets they connect (not by reference), so a renumbered board does not break the drawing.
Sections: power stage (DC link, four cells with Kelvin pad, per-cell UFCS shunt, joined AC to four terminals), the two
driver blocks (control header with common-mode chokes, input filters, R_ON / D + R_OFF, star, R_G), the four isolated
supply islands (CMC, Zener VDD-S, bias resistor S-VEE, decoupling) and the twelve U.FL measurement ports.
"""
import json
import math
import os
import re
import sys
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-revb-dpt"      # spb-bb-revb-dpt | spb-bb-revb-load
HW = os.path.join(ROOT, "hardware", NAME)
SYMDIR = "C:/Program Files/KiCad/7.0/share/kicad/symbols"
ROOT_UUID = str(uuid.uuid5(uuid.NAMESPACE_URL, NAME + "-root"))
G = 2.54


def uid(*k):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, NAME + "/" + "/".join(str(x) for x in k)))


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


CUSTOM = {
    # pad 2 is the Kelvin source (own net KH/KL on Rev B), pads 4/6 the power source
    "EPC2361": box_symbol("EPC2361", [None, ("1", "G"), None, None, ("2", "K")],
                          [("3", "D"), ("5", "D"), ("7", "D"), None, ("4", "S"), ("6", "S")], "Q", 10.16),
    "2EDF7275K": box_symbol("2EDF7275K", [("7", "VDDI"), ("2", "INA"), ("3", "INB"), ("5", "DISABLE"), ("4", "SLDON"),
                                          ("6", "NC"), ("1", "GNDI")],
                            [("13", "VDDA"), ("12", "OUTA"), ("11", "GNDA"), None, ("10", "VDDB"), ("9", "OUTB"),
                             ("8", "GNDB")], "U", 17.78),
    # common-mode choke, windings 1-2 and 4-3
    "WE-CNSW": box_symbol("WE-CNSW", [("1", "1"), None, ("4", "4")], [("2", "2"), None, ("3", "3")], "L", 7.62),
}
STD = [("Device", "R"), ("Device", "C"), ("Device", "D_Schottky"), ("Device", "D_Zener"), ("Device", "LED"),
       ("Device", "Thermistor_NTC"), ("Mechanical", "MountingHole"), ("Connector_Generic", "Conn_01x01"),
       ("Connector_Generic", "Conn_02x03_Odd_Even"), ("Connector_Generic", "Conn_02x05_Odd_Even"),
       ("Connector_Generic", "Conn_01x02"), ("Connector", "Conn_Coaxial"), ("Device", "FerriteBead")]
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
    '(sym_lib_table\n  (lib (name "spb_fab")(type "KiCad")(uri "${KIPRJMOD}/spb_fab.kicad_sym")(options "")(descr "SPB board symbols"))\n)\n')

# ------------------------------------------------------------------ parts and nets from the board
PADS = {r: (v, p) for r, v, p in json.load(open(os.path.join(HW, "pad_nets.json")))}
PARTS = {p["ref"]: p for p in json.load(open(os.path.join(HW, "parts.json")))}
SKIP = {"HS1"}                                   # board-only (heatsink)
_pcb = open(os.path.join(HW, NAME + ".kicad_pcb"), encoding="utf-8").read()
FPID = {}
for _m in re.finditer(r'\(footprint "([^"]+)"', _pcb):
    _r = re.search(r'\(fp_text reference "([^"]+)"', _pcb[_m.end():_m.end() + 3000])
    if _r:
        FPID[_r.group(1)] = _m.group(1)


def net_of(ref, pin):
    return PADS[ref][1].get(pin, "")


def refkey(r):
    return re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0)


def find(*nets, pre=None):
    s = set(nets)
    return sorted((r for r, (v, p) in PADS.items() if set(p.values()) == s and (pre is None or r.startswith(pre))),
                  key=refkey)


def one(*nets):
    r = find(*nets)
    assert len(r) == 1, (nets, r)
    return r[0]


def with_pin(pin, net, pre):
    r = [x for x in PADS if x.startswith(pre) and net_of(x, pin) == net]
    assert len(r) == 1, (pin, net, r)
    return r[0]


def lib_id(ref):
    val = PADS[ref][0]
    if ref.startswith("Q"):
        return "spb_fab:EPC2361"
    if ref.startswith("U"):
        return "spb_fab:2EDF7275K"
    if ref.startswith("FB"):
        return "Device:FerriteBead"
    if ref.startswith("L"):
        return "spb_fab:WE-CNSW"
    if ref.startswith("RT"):
        return "Device:Thermistor_NTC"
    if ref.startswith("R"):
        return "Device:R"
    if ref.startswith("C"):
        return "Device:C"
    if ref.startswith("D"):
        return "Device:D_Schottky" if val.startswith("PMEG") else "Device:D_Zener" if val.startswith("BZX") else "Device:LED"
    if ref.startswith("H"):
        return "Mechanical:MountingHole"
    if val.startswith("U.FL"):
        return "Connector:Conn_Coaxial"
    n = len(PADS[ref][1])
    return {10: "Connector_Generic:Conn_02x05_Odd_Even", 6: "Connector_Generic:Conn_02x03_Odd_Even",
            2: "Connector_Generic:Conn_01x02"}.get(
        n, "Connector_Generic:Conn_01x01")


# ------------------------------------------------------------------ drawing primitives
INST = {}          # ref -> (lib_id, x, y, rot)
WIRES = []         # ((x0, y0), (x1, y1))
LABELS = []        # (net, x, y, angle)
NOCON = []
TEXT = []
DIODES = ("Device:LED", "Device:D_Schottky", "Device:D_Zener")
BELOW = set()      # horizontal parts with reference/value under the body
ABOVE = set()      # horizontal parts with reference and value both above the body


def rnd(v):
    return round(v / 0.01) * 0.01


def place(ref, x, y, rot=0):
    INST[ref] = (lib_id(ref), rnd(x), rnd(y), rot)


def pin_xy(ref, num):
    lid, X, Y, rot = INST[ref]
    px, py, ang = PINS[lid][num]
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
    if lib_id(ref) in DIODES:                              # pin 1 = K
        rot = 90 if net_of(ref, "2") == top_net else 270
    else:
        rot = 0 if net_of(ref, "1") == top_net else 180
    place(ref, x, yc, rot)
    a, b = pin_xy(ref, "1"), pin_xy(ref, "2")
    return (a, b) if a[1] < b[1] else (b, a)


def horiz(ref, xc, y, left_net):
    if lib_id(ref) in DIODES:
        rot = 0 if net_of(ref, "1") == left_net else 180
    else:
        rot = 90 if net_of(ref, "1") == left_net else 270
    place(ref, xc, y, rot)
    a, b = pin_xy(ref, "1"), pin_xy(ref, "2")
    return (a, b) if a[0] < b[0] else (b, a)


def T(s, x, y, size=2.0, bold=True):
    TEXT.append((s, x, y, size, bold))


def lab_up(p, net):
    W(p, (p[0], p[1] - 2.54))
    LBL(net, p[0], p[1] - 2.54, (0, -1))


def lab_dn(p, net):
    W(p, (p[0], p[1] + 2.54))
    LBL(net, p[0], p[1] + 2.54, (0, 1))


# ================================================================== 1 power stage
SHUNT = any(r.startswith("RS") for r in PADS)
T("POWER STAGE AND DC LINK  (block 1: Q1-Q4, block 2: Q5-Q8; one cell = HS + LS transistor%s; AC of all four cells "
  "joined on the PCB)" % (" + UFCS shunt in the LS source" if SHUNT else ", LS source straight to DC-"), 25.4, 27.94)
caps = find("DCP", "DCN", pre="C")
half = (len(caps) + 1) // 2
for row, (yp, yn) in enumerate(((40.64, 76.2), (96.52, 132.08))):
    lst = caps[row * half:(row + 1) * half]
    for k, ref in enumerate(lst):
        x = 35.56 + 6.35 * k
        t, b = vert(ref, x, (yp + yn) / 2, "DCP")
        W((x, yp), t)
        W(b, (x, yn))
    xe = 35.56 + 6.35 * (len(lst) - 1)
    W((30.48, yp), (xe, yp))
    W((30.48, yn), (xe, yn))
    LBL("DCP", 30.48, yp, (-1, 0))
    LBL("DCN", 30.48, yn, (-1, 0))
cnt = {}
for r in caps:
    v = PADS[r][0].split(" (")[0]
    cnt[v] = cnt.get(v, 0) + 1
T("DC link, %d capacitors: " % len(caps) + ",  ".join("%d x %s" % (n, v) for v, n in sorted(cnt.items())) +
  "  (1 uF 0805: bypass at the HS drains of each cell, top + bottom; 22 uF 2220: bank)", 30.48, 144.78, 1.5, False)

YDP, YSW, YL, YDN = 35.56, 76.2, 116.84, 142.24
XA, XD = 609.6, 670.56
hs_q = sorted((r for r in PADS if r.startswith("Q") and net_of(r, "3") == "DCP"), key=refkey)
xbs = []
for c, hq in enumerate(hs_q):
    X = 393.7 + 50.8 * c
    blk = net_of(hq, "2")[-1]
    lq = with_pin("1", "GL_" + net_of(hq, "1")[3:], "Q")                # same cell: GH_L1 -> GL_L1
    lsrc = net_of(lq, "4")
    rs = one(lsrc, "DCN") if lsrc != "DCN" else None
    xb = X + 10.16
    xbs.append(xb)
    for ref, Y, ytop, ybot in ((hq, 55.88, YDP, YSW), (lq, 99.06, YSW, YL)):
        place(ref, X, Y)
        for n in ("3", "5", "7", "4", "6"):
            px, py = pin_xy(ref, n)
            W((px, py), (xb, py))
        W((xb, ytop), (xb, Y - 1.27))
        W((xb, Y + 3.81), (xb, ybot))
        plabel(ref, "1")
        plabel(ref, "2")
    if rs:
        W((xb, YL), (xb + 5.08, YL))
        LBL(lsrc, xb + 5.08, YL, (1, 0))
        t, b = vert(rs, xb, 127.0, lsrc)
        W((xb, YL), t)
        W(b, (xb, YDN))
    else:                                        # load-test board: LS source = DC- (via-in-pad to L2)
        W((xb, YL), (xb, YDN))
    T("cell %d (block %s)" % (c + 1, blk), X - 7.62, 43.18, 1.5, False)
W((xbs[0] - 7.62, YDP), (XD, YDP))
W((xbs[0] - 7.62, YDN), (XD, YDN))
LBL("DCP", xbs[0] - 7.62, YDP, (-1, 0))
LBL("DCN", xbs[0] - 7.62, YDN, (-1, 0))
W((xbs[0], YSW), (XA, YSW))
LBL("SW", xbs[0] + 5.08, YSW, (0, -1))
T("RS1-RS4: PMK UFCS-R001 1 mOhm coaxial shunt, IN = LS source (LSRCx), SHLD = DC-" if SHUNT else
  "No shunt (load-test board): LS source stripes via-in-pad (blind L1-L2) into the DC- plane", 393.7, 152.4, 1.5, False)
# AC terminals on the joined switch node
ac = sorted((r for r in PADS if r.startswith("J") and set(PADS[r][1].values()) == {"SW"}), key=refkey)
for k, ref in enumerate(ac):
    y = YSW + 5.08 * k
    place(ref, XA + 10.16, y)
    W((XA, y), pin_xy(ref, "1"))
W((XA, YSW), (XA, YSW + 5.08 * (len(ac) - 1)))
T("%s: AC output, M6 bolt pad, 12 x 5 mm Cu bar bolted on" % ac[0], XA - 5.08, YSW + 25.4, 1.5, False)
T("the bar passes through a LEM HO 250-S (off board,", XA - 5.08, YSW + 29.21, 1.5, False)
T("3.2 mV/A, JST PHR-5 straight to the C2000)", XA - 5.08, YSW + 33.02, 1.5, False)
# DC terminals
for net, y0, dy in (("DCP", YDP, 5.08), ("DCN", YDN, -5.08)):
    js = sorted((r for r in PADS if r.startswith("J") and set(PADS[r][1].values()) == {net}), key=refkey)
    W((XD, y0), (XD, y0 + dy * (len(js) - 1)))
    for k, ref in enumerate(js):
        y = y0 + dy * k
        place(ref, XD + 10.16, y)
        W((XD, y), pin_xy(ref, "1"))
# DC-link indicator and bleeder
x = 635.0
t, b = vert(one("DCP", "HVA"), x, 48.26, "DCP")
W((x, YDP), t)
t2, b2 = vert(one("HVA", "HVB"), x, 60.96, "HVA")
W(b, t2)
t3, b3 = vert(one("HVB", "DCN"), x, 73.66, "HVB")
W(b2, t3)
W(b3, (x, YDN))
rbl = [r for r in find("DCP", "DCN", pre="R")][0]
t, b = vert(rbl, 650.24, 88.9, "DCP")
W((650.24, YDP), t)
W(b, (650.24, YDN))
T("DC link present LED, %s 100 k bleeder" % rbl, 627.38, 157.48, 1.5, False)

# ================================================================== 2 driver blocks
YD = 220.98
T("GATE DRIVER BLOCKS: control header with common-mode chokes, 2EDF7275K input filters, R_ON / D + R_OFF, star, "
  "R_G per transistor (block 1 drives Q1-Q4, block 2 drives Q5-Q8)", 25.4, YD - 38.1)
for blk, dx in ((1, -15.24), (2, -15.24 + 406.4)):
    s = str(blk)
    X = lambda v: v + dx                                       # noqa: E731  (Rev A coordinates shifted)
    x0 = 45.72 + dx + 15.24
    T("BLOCK %s" % s, x0 - 15.24, YD - 30.48, 1.8)
    # control header (2 x 5 SMT, every signal with its own return) and one common-mode choke per pair
    jc = [r for r in PADS if r.startswith("J") and "C_PWMH" + s in PADS[r][1].values()][0]
    place(jc, x0, YD)
    for n in sorted(PADS[jc][1], key=int):
        plabel(jc, n)
    chokes = [r for r in PADS if r.startswith("L") and any(v.startswith(("C_PWM", "C_DIS", "C_12V", "C_NTC"))
                                                          and v.endswith(s) for v in PADS[r][1].values())]
    for k, cm in enumerate(sorted(chokes, key=refkey)):
        place(cm, x0 + 40.64, YD - 27.94 + 15.24 * k)
        for n in ("1", "2", "3", "4"):
            plabel(cm, n)
    fb = [r for r in PADS if r.startswith("FB") and "12V_CM" + s in PADS[r][1].values()][0]
    t, b = vert(fb, x0 - 7.62, YD + 22.86, "12V_CM" + s)
    lab_up(t, "12V_CM" + s)
    lab_dn(b, "+12V" + s)
    for c12 in [r for r in find("+12V" + s, "GNDI" + s) if r.startswith("C")]:     # optional 12 V bulk cap
        t, b = vert(c12, x0 + 2.54, YD + 22.86, "+12V" + s)
        lab_up(t, "+12V" + s)
        lab_dn(b, "GNDI" + s)
    rt = find("NTC", "GNDI" + s, pre="RT")
    if rt:
        t, b = vert(rt[0], x0 + 12.7, YD + 22.86, "NTC")
        lab_up(t, "NTC")
        lab_dn(b, "GNDI" + s)
        T("NTC on the control side (board temperature at the driver)", x0 - 12.7, YD + 41.91, 1.27, False)
    # driver core
    u = with_pin("2", "INA" + s, "U")
    place(u, X(190.5), YD)
    ina, inb = pin_xy(u, "2"), pin_xy(u, "3")
    LBL("PWM_H" + s, X(134.62), ina[1], (-1, 0))
    ABOVE.add(one("PWM_H" + s, "INA" + s))
    l, r = horiz(one("PWM_H" + s, "INA" + s), X(149.86), ina[1], "PWM_H" + s)
    W((X(134.62), ina[1]), l)
    W(r, ina)
    for pd in find("GNDI" + s, "PWM_H" + s):                  # optional external pull-down (internal 150 k)
        t, b = vert(pd, X(139.7), ina[1] - 10.16, "GNDI" + s)
        W(b, (X(139.7), ina[1]))
        lab_up(t, "GNDI" + s)
    t, b = vert(one("GNDI" + s, "INA" + s), X(160.02), ina[1] - 10.16, "GNDI" + s)
    W(b, (X(160.02), ina[1]))
    lab_up(t, "GNDI" + s)
    LBL("PWM_L" + s, X(134.62), inb[1], (-1, 0))
    BELOW.add(one("PWM_L" + s, "INB" + s))
    l, r = horiz(one("PWM_L" + s, "INB" + s), X(149.86), inb[1], "PWM_L" + s)
    W((X(134.62), inb[1]), l)
    W(r, inb)
    for pd in find("GNDI" + s, "PWM_L" + s):
        t, b = vert(pd, X(142.24), inb[1] + 10.16, "PWM_L" + s)
        W((X(142.24), inb[1]), t)
        lab_dn(b, "GNDI" + s)
    t, b = vert(one("GNDI" + s, "INB" + s), X(162.56), inb[1] + 10.16, "INB" + s)
    W((X(162.56), inb[1]), t)
    lab_dn(b, "GNDI" + s)
    vddi = pin_xy(u, "7")
    W(vddi, (X(166.37), vddi[1]))
    t, b = vert(one("+12V" + s, "VDDI" + s), X(166.37), vddi[1] - 10.16, "+12V" + s)
    W(b, (X(166.37), vddi[1]))
    lab_up(t, "+12V" + s)
    t, b = vert(one("VDDI" + s, "GNDI" + s), X(176.53), vddi[1] - 10.16, "GNDI" + s)
    W(b, (X(176.53), vddi[1]))
    lab_up(t, "GNDI" + s)
    for n in ("5", "4", "1"):
        p = pin_xy(u, n)
        W(p, (X(172.72), p[1]))
        LBL(net_of(u, n), X(172.72), p[1], (-1, 0))
    NOCON.append(pin_xy(u, "6"))
    T("SLDON = GNDI: input-side LDO on", X(154.94), YD + 27.94, 1.27, False)
    for ch, out_pin, vdd_pin, vee_pin, dy, star, kel, gp in (
            ("A", "12", "13", "11", -1, "GH_STAR" + s, "KH" + s, "GH_"),
            ("B", "9", "10", "8", 1, "GL_STAR" + s, "KL" + s, "GL_")):
        o = pin_xy(u, out_pin)
        plabel(u, vdd_pin)
        plabel(u, vee_pin)
        out, off = "OUT" + ch + s, "OFF" + ch + s
        yo, yd = o[1], o[1] + dy * 7.62
        l, r = horiz(one(out, star), X(213.36), yo, out)
        W(o, l)
        W(r, (X(238.76), yo))
        W((X(205.74), yo), (X(205.74), yd))
        l, r = horiz(one(out, off), X(213.36), yd, out)
        W((X(205.74), yd), l)
        l2, r2 = horiz(one(off, star), X(226.06), yd, off)
        W(r, l2)
        W(r2, (X(233.68), yd), (X(233.68), yo))
        y1, y2 = (yo - 5.08, yo + 5.08) if ch == "A" else (yo + 5.08, yo + 12.7)
        W((X(238.76), yo), (X(238.76), y1))
        W((X(238.76), yo), (X(238.76), y2)) if ch == "A" else W((X(238.76), y1), (X(238.76), y2))
        pd = one(kel, star)
        if ch == "A":
            t, b = vert(pd, X(238.76), y1 - 6.35, kel)
            W(b, (X(238.76), y1))
            lab_up(t, kel)
        else:
            t, b = vert(pd, X(238.76), y2 + 6.35, star)
            W((X(238.76), y2), t)
            lab_dn(b, kel)
        for side, yy in (("L", y1), ("R", y2)):
            gnet = gp + side + s
            l, r = horiz(one(star, gnet), X(246.38), yy, star)
            W((X(238.76), yy), l)
            W(r, (r[0] + 2.54, r[1]))
            LBL(gnet, r[0] + 2.54, r[1], (1, 0))
    T("R_ON 0.75 R, R_OFF 0 R (jumper), R_G 0.5 R per transistor, 10 k gate pull-down at the star to the Kelvin net",
      X(154.94), YD + 30.48, 1.27, False)

# ================================================================== 3 isolated supply islands
Y0 = 274.32
T("GATE SUPPLY ISLANDS: external isolated supply (one HS, one LS, split per block) -> WE-CNSW -> 5.1 V Zener VDD-S, "
  "150 R bias S-VEE: V_GS,on = +5.1 V, V_GS,off = -(V_ISO - 5.1 V)", 25.4, Y0 - 7.62)


def island(j, cm, vdd, k, vee, X0):
    place(j, X0, Y0 + 15.24, 180)
    plabel(j, "1")
    plabel(j, "2")
    cx, cy = X0 + 45.72, Y0 + 15.24
    place(cm, cx, cy, 0)
    pv = [n for n in "1234" if net_of(cm, n) == vdd][0]
    if pin_xy(cm, pv)[0] < cx or pin_xy(cm, pv)[1] > cy:
        place(cm, cx, cy, 180)
    pe = [n for n in "1234" if net_of(cm, n) == vee][0]
    for n in "1234":
        if n not in (pv, pe):
            plabel(cm, n)
    a, e = pin_xy(cm, pv), pin_xy(cm, pe)
    xa, xb = a[0] + 2.54, a[0] + 5.08
    W(a, (xa, a[1]), (xa, Y0))
    W(e, (xb, e[1]), (xb, Y0 + 30.48))
    x = xb + 7.62
    for ref in find(vdd, vee):
        t, b = vert(ref, x, cy, vdd)
        W((x, Y0), t)
        W(b, (x, Y0 + 30.48))
        x += 10.16
    up = sorted(find(vdd, k), key=lambda r: (r[0] == "C", refkey(r)))
    lo = sorted(find(k, vee), key=lambda r: (r[0] == "C", refkey(r)))
    xk = x
    for u_, l_ in zip(up, lo):
        t, b = vert(u_, x, Y0 + 7.62, vdd)
        W((x, Y0), t)
        W(b, (x, cy))
        t, b = vert(l_, x, Y0 + 22.86, k)
        W((x, cy), t)
        W(b, (x, Y0 + 30.48))
        x += 10.16
    W((xa, Y0), (x, Y0))
    W((xk, cy), (x, cy))
    W((xb, Y0 + 30.48), (x, Y0 + 30.48))
    LBL(vdd, x, Y0, (1, 0))
    LBL(k, x, cy, (1, 0))
    LBL(vee, x, Y0 + 30.48, (1, 0))
    T("%s / %s: %s" % (j, cm, "HS" if k.startswith("KH") else "LS") + " block " + k[-1], X0 - 5.08, Y0 + 40.64, 1.5,
      False)


for i, (blk, ab, kk) in enumerate(((1, "A", "KH"), (1, "B", "KL"), (2, "A", "KH"), (2, "B", "KL"))):
    s = str(blk)
    j = with_pin("1", "VIN%s_P%s" % (ab, s), "J")
    cm = [r for r in PADS if r.startswith("L") and "VIN%s_P%s" % (ab, s) in PADS[r][1].values()][0]
    island(j, cm, "VDD%s%s" % (ab, s), kk + s, "VEE%s%s" % (ab, s), 38.1 + 203.2 * i)

# ================================================================== 4 U.FL measurement ports
YU = 337.82
T("U.FL MEASUREMENT PORTS (bottom side, at each cell): V_GS HS / LS (0 R, shield = Kelvin), V_DS LS (953 R series = "
  "20:1 into the 50 R scope input, shield = LS source %s)" % ("LSRCx" if SHUNT else "= DC-"), 25.4, YU - 12.7)
ufl = sorted((r for r in PADS if PADS[r][0].startswith("U.FL")), key=refkey)
for i, j in enumerate(ufl):
    Xu, Yu = 50.8 + 101.6 * (i % 6), YU + 25.4 * (i // 6)
    sig = net_of(j, "1")
    rr = [r for r in PADS if r.startswith("R") and sig in PADS[r][1].values()][0]
    src = [n for n in PADS[rr][1].values() if n != sig][0]
    place(j, Xu + 20.32, Yu)
    l, r = horiz(rr, Xu + 5.08, Yu, src)
    W((Xu - 5.08, Yu), l)
    LBL(src, Xu - 5.08, Yu, (-1, 0))
    W(r, pin_xy(j, "1"))
    plabel(j, "2")

# ================================================================== 5 mechanical, notes
YM = 391.16
T("MOUNTING: H1-H4 board corners (insulated), H5-H7 heatsink spreader; heatsink HS1 (Fischer LAM 4, 100 mm, rotated "
  "90 deg, tube across the board width) is a board-only item" if "HS1" in PADS else
  "MOUNTING: H1-H4 board corners (insulated); no heatsink (double-pulse board)", 25.4, YM - 7.62)
holes = sorted((r for r in PADS if r.startswith("H") and r not in SKIP), key=refkey)
for k, h in enumerate(holes):
    place(h, 30.48 + 12.7 * k, YM + 5.08)
notes = [
    "Nets: DCP = DC+, DCN = DC-, SW = joined switch node of all four cells.  KH1/KH2 and KL1/KL2 are the Kelvin source "
    "nets (pad 2 of each EPC2361); they meet the power source only inside the package.",
    ("LSRC1-LSRC4: LS power source of each cell = UFCS IN; the shunt SHLD side is DC-.  " if SHUNT else
     "LS power source = DC- directly (no shunt).  ") + "The LS gate drive and the LS supply are referenced to the "
    "Kelvin net KLx, not to DC-.",
    "Block suffix 1/2 on every driver-side net (GNDI1, VDDA2, ...).  Control side (CTRLx 2 x 5 header): PWM_H, PWM_L, "
    "DIS, 12 V and (block 1) NTC each with their own return C_RTN_* through one WE-CNSW common-mode choke per pair; "
    "12 V then through a ferrite bead.  The control side is a top-layer-only area with a 1200 V barrier (4 mm outer, "
    "3 mm L2) to all power copper; see reports/pcb-rules/PCB_rules_and_checklist.md.",
    "No short-circuit protection on this board.  Closed-loop control from a TI TMS320F28379D over the CTRL headers.",
]
for k, t in enumerate(notes):
    T(t, 25.4, YM + 22.86 + 5.08 * k, 1.5, False)

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
    WIRES[:] = list(dict.fromkeys(new_w))

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
JUNC = set(p for p, n in ends.items() if n + pinpts.get(p, 0) >= 3)

# ------------------------------------------------------------------ write
out = ['(kicad_sch (version 20230121) (generator eeschema)', ' (uuid %s)' % ROOT_UUID, ' (paper "A1")',
       ' (title_block (title "SPB leg, Rev B, %s") (date "2026-10-14") (rev "B") (company "KTH")'
       ' (comment 1 "4 x EPC2361 per switch, 2 x 2EDF7275K, %s, external isolated supplies, U.FL ports")' % (
           ("double-pulse board" if SHUNT else "load-test board"), ("UFCS shunt per cell, no heatsink" if SHUNT else
                                                                   "no shunt, LAM 4 heatsink")) + ''
       ' (comment 2 "generated by scripts/make_kicad_sch_revb.py; netlist identical to the PCB (check_sch_vs_pcb.py)"))',
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
    p = PARTS.get(ref, {})
    short = val.split(" (")[0] if ref[0] in "RCD" else val
    short = re.sub(r" (0402|0603|0805|1206|1210)$", "", short)
    if ref.startswith("J"):
        short = val.split(":")[0]
    elif ref.startswith("H"):
        short = "M2.5"
    two = lid in ("Device:R", "Device:C", "Device:Thermistor_NTC", "Device:FerriteBead") + DIODES
    vertical = rot in (0, 180) if lid in ("Device:R", "Device:C", "Device:Thermistor_NTC", "Device:FerriteBead") else rot in (90, 270)
    left = False
    if lid.startswith("spb_fab"):
        top = max(abs(py) for _, py, _ in PINS[lid].values()) + 2.54
        geo = {"Reference": (X, Y - top - 1.27, 0), "Value": (X, Y + top + 2.54, 0)}
    elif lid == "Connector:Conn_Coaxial":
        geo = {"Reference": (X + 3.81, Y - 1.27, 0), "Value": (X + 3.81, Y + 1.27, 0)}
        left = True
    elif two and vertical:
        geo = {"Reference": (X - (3.4 if lid == "Device:C" else 2.6), Y, 90),
               "Value": (X + (3.4 if lid == "Device:C" else 2.6), Y, 90)}
    elif two and ref in ABOVE:
        geo = {"Reference": (X, Y - 5.6, 0), "Value": (X, Y - 2.8, 0)}
    elif two and ref in BELOW:
        geo = {"Reference": (X, Y + 2.8, 0), "Value": (X, Y + 5.6, 0)}
    elif two:
        geo = {"Reference": (X, Y - 2.8, 0), "Value": (X, Y + 2.8, 0)}
    else:
        geo = {"Reference": (X, Y - 5.0, 0), "Value": (X, Y + 5.5, 0)}
    pl = []
    for pn, pv in (("Reference", ref), ("Value", short), ("Footprint", FPID.get(ref, p.get("footprint", ""))),
                   ("Datasheet", "~"), ("MPN", p.get("mpn", "")), ("Description", val)):
        gx, gy, ga = geo.get(pn, (X, Y, 0))
        ga = (ga - rot) % 180                    # KiCad adds the symbol rotation to the field angle
        hide = " hide" if pn not in ("Reference", "Value") or (pn == "Value" and ref in caps) else ""
        just = " (justify left)" if left and pn in ("Reference", "Value") else ""
        pl.append('(property %s %s (at %.2f %.2f %d) (effects (font (size 1.27 1.27))%s%s))'
                  % (q(pn), q(pv), gx, gy, ga, just, hide))
    pinlist = " ".join('(pin %s (uuid %s))' % (q(n), uid(ref, "pin", n)) for n in sorted(PINS[lid]))
    out.append(' (symbol (lib_id %s) (at %.2f %.2f %d) (unit 1) (in_bom %s) (on_board yes) (dnp no) (uuid %s)\n  %s\n'
               '  %s\n  (instances (project %s (path "/%s" (reference %s) (unit 1)))))'
               % (q(lid), X, Y, rot, "no" if ref.startswith("H") else "yes", uid(ref), "\n  ".join(pl),
                  pinlist, q(NAME), ROOT_UUID, q(ref)))
out.append(' (sheet_instances (path "/" (page "1")))')
out.append(')')
path = os.path.join(HW, NAME + ".kicad_sch")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("written", path, len(INST), "symbols", len(WIRES), "wires", len(JUNC), "junctions", len(LABELS), "labels")
