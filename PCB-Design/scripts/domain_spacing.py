"""
Copper spacing between the voltage domains of a Rev B leg board: the check behind the clearance/creepage rule set
(reports/pcb-rules/PCB_rules_and_checklist.md).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\domain_spacing.py dpt [workdir]
      -> <workdir>/domain_spacing_<board>.json, printed summary per domain pair

The board is copied to a work folder (the project is not touched). For each domain pair a .kicad_dru with one probe
rule (a deliberately large minimum clearance) is written and the KiCad DRC is run; the reported actual distances are
then filtered by the net domains of both items (KiCad's wildcard matching in rule conditions is looser than needed).
KiCad 7 stops a report at 579 violations, so "capped" means more pairs exist beyond the ones listed; the minimum
distance is still found because the closest pairs are reported first per item.

Domains (by net name):
  CTRL  primary side of the 2EDF7275K: control connector, 12 V, PWM, DIS, GNDI   (potential of the controller)
  HS    switch-node domain: SW, high-side Kelvin KH and the HS gate/driver nets  (0..90 V against DC-)
  LS    DC- domain: DC-, LS sources, low-side Kelvin KL and the LS gate/driver nets
  DCP   DC+ (and the DC+ LED divider)
"""
import fnmatch
import json
import os
import re
import shutil
import sys

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = sys.argv[1] if len(sys.argv) > 1 else "dpt"
WORK = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "build", "spacing")
NAME = "spb-bb-revb-" + BOARD
SRC = os.path.join(ROOT, "hardware", NAME)

DOM = {
    "CTRL": ["GNDI*", "+12V*", "C_*", "PWM_*", "DIS*", "INA*", "INB*", "VDDI*", "LEDA_12V*"],
    "HS": ["SW", "KH*", "VDDA*", "VEEA*", "GH_*", "OUTA*", "OFFA*", "VINA_*", "UFL_H*"],
    "LS": ["DCN", "LSRC*", "KL*", "VDDB*", "VEEB*", "GL_*", "OUTB*", "OFFB*", "VINB_*", "UFL_L*", "UFL_D*", "NTC"],
    "DCP": ["DCP", "HVA", "HVB"],
}
PAIRS = [("CTRL", "HS"), ("CTRL", "LS"), ("CTRL", "DCP"), ("HS", "LS"), ("HS", "DCP"), ("LS", "DCP")]
PROBES = {"CTRL": 4.0}                          # mm: control-to-power pairs probed to 4 mm, power pairs to 1 mm
CAP = 579                                       # KiCad 7 report limit


def cond(dom, side):
    return "(" + " || ".join("%s.NetName == '%s'" % (side, p) for p in DOM[dom]) + ")"


def domain(net):
    for d, pats in DOM.items():
        if any(fnmatch.fnmatchcase(net, p) for p in pats):
            return d
    return "?"


def parse(rpt, want):
    txt = open(rpt, encoding="utf-8", errors="replace").read()
    n = int(re.search(r"Found (\d+) DRC violations", txt).group(1))
    rows = []
    for blk in re.split(r"\n(?=\[)", txt):
        m = re.search(r"actual ([0-9.]+) mm", blk)
        items = re.findall(r"@\(([-0-9.]+) mm, ([-0-9.]+) mm\): (.*)", blk)
        if not m or len(items) < 2:
            continue
        nets = [re.search(r"\[([^\]]*)\]", it[2]) for it in items[:2]]
        if not all(nets) or {domain(nets[0].group(1)), domain(nets[1].group(1))} != want:
            continue
        rows.append((float(m.group(1)), items[0][2][:70], items[1][2][:70]))
    rows.sort()
    return n, rows


def main():
    os.makedirs(WORK, exist_ok=True)
    for ext in (".kicad_pcb", ".kicad_pro"):
        shutil.copy(os.path.join(SRC, NAME + ext), os.path.join(WORK, NAME + ext))
    res = {}
    for a, b in PAIRS:
        probe = PROBES.get(a, 1.0)
        # KiCad evaluates A/B in one item order only: make the condition symmetric
        c = "(%s && %s) || (%s && %s)" % (cond(a, "A"), cond(b, "B"), cond(b, "A"), cond(a, "B"))
        open(os.path.join(WORK, NAME + ".kicad_dru"), "w").write(
            '(version 1)\n(rule "probe %s-%s"\n  (condition "%s")\n  (constraint clearance (min %.1fmm)))\n'
            % (a, b, c, probe))
        board = pcbnew.LoadBoard(os.path.join(WORK, NAME + ".kicad_pcb"))
        rpt = os.path.join(WORK, "%s_%s-%s.rpt" % (NAME, a, b))
        pcbnew.WriteDRCReport(board, rpt, pcbnew.EDA_UNITS_MILLIMETRES, True)
        n, rows = parse(rpt, {a, b})
        key = "%s-%s" % (a, b)
        res[key] = {"probe_mm": probe, "min_mm": rows[0][0] if rows else None,
                    "pairs_below_1mm": sum(r[0] < 1.0 for r in rows), "pairs_below_3p4mm": sum(r[0] < 3.4 for r in rows),
                    "capped": n >= CAP, "closest": rows[:8]}
        print("%-9s min %s mm, pairs < 1 mm: %d%s" % (key, "%.3f" % rows[0][0] if rows else "> %.1f" % probe,
                                                       res[key]["pairs_below_1mm"], " (report capped)" if n >= CAP else ""),
              flush=True)
        for r in rows[:3]:
            print("            %.3f  %s | %s" % r, flush=True)
    os.remove(os.path.join(WORK, NAME + ".kicad_dru"))
    out = os.path.join(WORK, "domain_spacing_%s.json" % BOARD)
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
