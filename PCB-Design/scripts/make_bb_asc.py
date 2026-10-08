"""
Generate LTspice schematics (.asc) + symbols (.asy) for the building-block model in simulation/bb_spice.

    python scripts/make_bb_asc.py

The netlists stay the single source of truth: the circuit comes from BB_circuit.inc, the top-level parameters
and .step lines from the schematic definitions below. Every element becomes a symbol with a net-label flag on
each pin, grouped by the "* ---- section ----" comments of BB_circuit.inc; every dot-directive becomes a SPICE
directive on the sheet. Schematics written:
  BB_DPT.asc            single double pulse at 141 A, Rg_on/Rg_off = 2/0 ohm (about 1 min)
  BB_energy_sweep.asc   E_on / E_off vs current, 7 currents (about 5 min)
  BB_rg_slow.asc        slow-switching study at 141 A: Rg_on 2 / 10 ohm x Rg_off 0 / 2 / 5 / 10 ohm (8 runs, ~6 min)
Symbols written: BB_PL.asy (Q3D power loop, 21 terminals), BB_GL.asy (Q3D gate star), EPC2361.asy.
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = os.path.join(ROOT, "simulation", "bb_spice")
INC = os.path.join(SP, "BB_circuit.inc")

EXTRA_MEAS = [
    "* gated energies (400 ns window, only while V_DS > 1 V: excludes the conduction tail; use for slow switching)",
    ".meas TRAN Eoff400 INTEG (V(QL_D_L,QL_S_L)*I(VILL)+V(QL_D_R,QL_S_R)*I(VILR))*(V(QL_D_L,QL_S_L)>1) FROM {T1} TO {T1+400n}",
    ".meas TRAN Eon400 INTEG (V(QL_D_L,QL_S_L)*I(VILL)+V(QL_D_R,QL_S_R)*I(VILR))*(V(QL_D_L,QL_S_L)>1) FROM {T2} TO {T2+400n}",
]
SHEETS = {
    "BB_DPT": dict(title="Building block double-pulse test, 141 A (rated peak), Rg_on/Rg_off = 2/0 ohm",
                   params=".param VBUS=75 IPK=141 LLOAD=5u TON1={LLOAD*IPK/VBUS} RGON=2 RGOFF=0 RPU=0.6 RPD=0.2",
                   steps=[]),
    "BB_energy_sweep": dict(title="Switching energy vs current (TON1 fixed, LLOAD stepped: .meas windows are evaluated once)",
                            params=".param VBUS=75 TON1=10.667u LLOAD={TON1*VBUS/IPK} RGON=2 RGOFF=0 RPU=0.6 RPD=0.2",
                            steps=[".step param IPK list 10 30 60 90 120 141 160"]),
    "BB_rg_slow": dict(title="Slow switching at 141 A: gate resistors stepped (read Eon400 / Eoff400 in the log)",
                       params=".param VBUS=75 IPK=141 TON1=10.667u LLOAD={TON1*VBUS/IPK} RPU=0.6 RPD=0.2",
                       steps=[".step param RGON list 2 10", ".step param RGOFF list 0 2 5 10"]),
}

# ------------------------------------------------------------------ symbols
PL_LEFT = ["CapPL", "CapNL", "CapPR", "CapNR", "CapB1P", "CapB1N", "CapB2P", "CapB2N", "CapB3P", "CapB3N"]
PL_RIGHT = ["QH_D_L", "QH_S_L", "QL_D_L", "QL_S_L", "QH_D_R", "QH_S_R", "QL_D_R", "QL_S_R"]
PL_TOP = ["T_DCP", "T_DCN", "T_AC"]
PL_ORDER = sorted(PL_LEFT + PL_RIGHT + PL_TOP)          # .subckt BB_PL pin order (sorted terminal names)
GL_LEFT = ["DrvOut", "DrvGnd"]
GL_RIGHT = ["Gate_L", "Kelvin_L", "Gate_R", "Kelvin_R"]
GL_ORDER = sorted(GL_LEFT + GL_RIGHT)


def block(name, left, right, top, order, w, desc, lines):
    n = max(len(left), len(right))
    h = 32 * (n + 1)
    pins, pos = [], {}
    for k, p in enumerate(left):
        pos[p] = (0, 32 * (k + 1))
    for k, p in enumerate(right):
        pos[p] = (w, 32 * (k + 1))
    for k, p in enumerate(top):
        pos[p] = (int(w * (k + 1) / (len(top) + 1)) // 16 * 16, -32)
    out = ["Version 4", "SymbolType BLOCK", "RECTANGLE Normal 0 0 %d %d" % (w, h)]
    out += ["TEXT %d %d Center 2 %s" % (w // 2, h // 2 - 24 + 20 * i, t) for i, t in enumerate([name] + lines)]
    for p in left:
        out.append("TEXT 8 %d Left 1 %s" % (pos[p][1], p))
    for p in right:
        out.append("TEXT %d %d Right 1 %s" % (w - 8, pos[p][1], p))
    for p in top:
        out.append("LINE Normal %d 0 %d -32" % (pos[p][0], pos[p][0]))
        out.append("TEXT %d 16 Center 1 %s" % (pos[p][0], p))
    out += ["WINDOW 0 %d -48 Center 2" % (w // 2), "SYMATTR Prefix X", "SYMATTR Value %s" % name,
            "SYMATTR Description %s" % desc]
    for p in order:
        x, y = pos[p]
        out += ["PIN %d %d NONE 0" % (x, y), "PINATTR PinName %s" % p, "PINATTR SpiceOrder %d" % (order.index(p) + 1)]
    return "\n".join(out) + "\n", [pos[p] for p in order], (w, h)


PINS = {
    "res": [(16, 16), (16, 96)], "ind": [(16, 16), (16, 96)], "cap": [(16, 0), (16, 64)],
    "voltage": [(0, 16), (0, 96)], "diode": [(16, 0), (16, 64)],
    "EPC2361": [(0, 48), (96, 0), (96, 96)],
}
SIZE = {"res": (160, 160), "ind": (160, 160), "cap": (160, 160), "voltage": (176, 160), "diode": (144, 160),
        "EPC2361": (240, 160)}
SYM = {"R": "res", "L": "ind", "C": "cap", "V": "voltage", "D": "diode"}


def parse_inc():
    sections, directives = [], []
    cur = None
    for raw in open(INC, encoding="ascii", errors="replace"):
        s = raw.strip()
        if not s:
            continue
        m = re.match(r"\*\s*-+\s*(.*?)\s*-+\s*$", s)
        if m:
            cur = (m.group(1), [])
            sections.append(cur)
        elif s.startswith("*"):
            continue
        elif s.startswith("."):
            directives.append(s)
        elif cur is not None:
            cur[1].append(s.split())
    return [x for x in sections if x[1]], directives


def element(tok):
    name, kind = tok[0], tok[0][0].upper()
    if kind == "X":
        return tok[-1], name[1:], tok[1:-1], tok[-1], ""
    nets, rest = tok[1:3], tok[3:]
    if kind in "LC":
        return SYM[kind], name, nets, rest[0], " ".join(rest[1:])
    if kind == "V" and len(rest) > 1:                 # PWL(...) source written with spaces
        return SYM[kind], name, nets, " ".join(rest), ""
    return SYM[kind], name, nets, " ".join(rest), ""


def write_sheet(key, spec, sections, directives):
    out = ["Version 4", "SHEET 1 4200 3000"]
    syms, flags, texts = [], [], []
    texts.append("TEXT 48 -96 Left 4 ;%s" % spec["title"])
    texts.append("TEXT 48 -40 Left 2 ;2 x EPC2361 per switch, LT8418-like driver in the middle, Q3D copper: BB_PL (power loop) and BB_GL (gate star). "
                 "Probe V(QL_D_L,QL_S_L), I(VILL), I(VILR), V(gtLL,QL_S_L), V(gtHL,QH_S_L).")
    y0 = 96
    for title, elems in sections:
        texts.append("TEXT 48 %d Left 3 ;%s" % (y0 - 40, title))
        x, y, row_h = 64, y0 + 48, 0
        for tok in elems:
            sym, inst, nets, value, extra = element(tok)
            w, h = SIZE[sym] if sym in SIZE else (BLOCKS[sym][1][0] + 320, BLOCKS[sym][1][1] + 160)
            if x + w > 2700:
                x, y, row_h = 64, y + row_h, 0
            ox, oy = x, y + (64 if sym in BLOCKS else 0)
            syms.append("SYMBOL %s %d %d R0" % (sym, ox, oy))
            if sym in ("res", "ind", "cap", "diode"):
                syms += ["WINDOW 0 36 32 Left 2", "WINDOW 3 36 64 Left 2"]
            syms.append("SYMATTR InstName %s" % inst)
            syms.append("SYMATTR Value %s" % value)
            if extra:
                syms.append("SYMATTR SpiceLine %s" % extra)
            pins = BLOCKS[sym][0] if sym in BLOCKS else PINS[sym]
            for (px, py), net in zip(pins, nets):
                flags.append("FLAG %d %d %s" % (ox + px, oy + py, net))
            x += w
            row_h = max(row_h, h + (64 if sym in BLOCKS else 0))
        y0 = y + row_h + 112
    # directives: top-level parameters and steps first, then the circuit's directives
    lines = ["* --- top-level parameters (edit here) ---", spec["params"]] + spec["steps"] + \
            ["* --- circuit directives (from BB_circuit.inc) ---"] + directives + EXTRA_MEAS
    ty = 64
    for d in lines:
        if d.startswith("*"):
            texts.append("TEXT 2800 %d Left 2 ;%s" % (ty, d.lstrip("* ")))
        else:
            texts.append("TEXT 2800 %d Left 2 !%s" % (ty, d))
        ty += 40 if len(d) < 140 else 72
    out += flags + syms + texts
    with open(os.path.join(SP, key + ".asc"), "w", encoding="ascii") as f:
        f.write("\n".join(out) + "\n")


def main():
    global BLOCKS
    pl, pl_pins, pl_wh = block("BB_PL", PL_LEFT, PL_RIGHT, PL_TOP, PL_ORDER, 352,
                               "Q3D copper of the building block power loop (../bb_q3d/results/BB_PL.lib)",
                               ["Q3D power loop", "R/L/K at 100 MHz"])
    gl, gl_pins, gl_wh = block("BB_GL", GL_LEFT, GL_RIGHT, [], GL_ORDER, 256,
                               "Q3D gate star from the centre driver (../bb_q3d/results/BB_GL.lib)", ["Q3D gate star"])
    BLOCKS = {"BB_PL": (pl_pins, pl_wh), "BB_GL": (gl_pins, gl_wh)}
    open(os.path.join(SP, "BB_PL.asy"), "w").write(pl)
    open(os.path.join(SP, "BB_GL.asy"), "w").write(gl)
    shutil.copy(os.path.join(ROOT, "simulation", "dpt", "EPC2361.asy"), os.path.join(SP, "EPC2361.asy"))
    sections, directives = parse_inc()
    for key, spec in SHEETS.items():
        write_sheet(key, spec, sections, directives)
        print("wrote", key + ".asc")
    with open(os.path.join(SP, "Open-BB.cmd"), "w") as f:
        f.write('@echo off\r\nrem Open the building-block schematics in LTspice (BB_DPT.asc; others: BB_energy_sweep.asc, BB_rg_slow.asc)\r\n'
                'cd /d "%~dp0"\r\nset ASC=%1\r\nif "%ASC%"=="" set ASC=BB_DPT.asc\r\n'
                'start "" "%LOCALAPPDATA%\\Programs\\ADI\\LTspice\\LTspice.exe" "%~dp0%ASC%"\r\n')


BLOCKS = {}
if __name__ == "__main__":
    main()
