"""
JLCPCB PCBA files of the DPT board from the fabrication outputs (scripts/make_fab_outputs_revb.py):

    python scripts/make_jlc_files.py [board]          (default spb-bb-revb-dpt)
-> hardware/<board>/fab/jlc/<board>-BOM-JLC.csv   Comment, Designator, Footprint, LCSC Part #, Manufacturer Part, Note
   hardware/<board>/fab/jlc/<board>-CPL-JLC.csv   Designator, Mid X, Mid Y, Layer, Rotation

Left out of both: the UFCS shunts RS1-RS4 (hand-soldered in the lab), DNP parts (the 0 R U.FL links) and the
board-only footprints (test points, spring pads, mounting holes), which are not in the BOM. The LCSC column stays
empty: JLC's BOM tool matches the manufacturer part number in "Comment", and every match is confirmed in its web
interface; parts that JLC does not stock (see SOURCING) are ordered through JLC Global Sourcing or sent in as
consignment parts. Rotations are KiCad's; check them in JLC's placement preview (JLC library orientations differ for
some packages).
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-revb-dpt"
FAB = os.path.join(ROOT, "hardware", NAME, "fab")
OUT = os.path.join(FAB, "jlc")
os.makedirs(OUT, exist_ok=True)

# special parts: LCSC stock could not be confirmed (2026-10-23) -> Global Sourcing / consignment, check at upload
SOURCING = {
    "EPC2361": "EPC; check LCSC, else Global Sourcing / consignment",
    "2EDF7275K": "Infineon 2EDF7275KXUMA1 (LGA-13); check LCSC, else Global Sourcing",
    "74650174": "Wuerth REDCUBE 74650174R, THR on the bottom side (paste-in-hole or hand-soldered); Global Sourcing",
    "66012102111404": "Wuerth WR-MMCX, bottom side; Global Sourcing",
    "744232601": "Wuerth WE-CNSW 1206; Global Sourcing if not stocked",
    "TSM-105-01-T-DV": "Samtec 2 x 5 SMT header; an equivalent 2.54 mm 2 x 5 SMT header is acceptable",
    "U.FL-R-SMT-1": "Hirose U.FL, bottom side",
}


MAKERS = ("TDK", "Murata", "Panasonic", "Yageo", "Nexperia", "Wurth", "Wuerth", "Infineon", "Hirose", "Samtec", "EPC")


def mpn_of(text):
    """manufacturer part number: the token after the manufacturer name ('Nexperia PMEG3020EJ (30 V ...)',
    '1.5R 0603 1% (Yageo RC0603FR-071R5L)'); generic parts ('10k 0402 1%') keep their value text"""
    m = re.search(r"\b(%s)\s+([A-Za-z0-9][A-Za-z0-9.\-()/]*)" % "|".join(MAKERS), text)
    if m:
        return m.group(2).rstrip(",)") if not m.group(2).endswith("(10)") else m.group(2)
    if text.strip() == "EPC2361":
        return "EPC2361"
    return ""


bom = list(csv.reader(open(os.path.join(FAB, NAME + "-bom.csv"), encoding="utf-8")))
rows, fitted = [], set()
for r in bom:
    if len(r) < 6 or not r[0].isdigit():
        continue
    qty, refs, val, fp, note, fit = r[:6]
    refs = refs.split()
    if fit != "fit":                                    # DNP and lab-fitted (RS1-RS4)
        continue
    mpn = mpn_of(note)
    src = next((v for k, v in SOURCING.items() if k in note or k in val), "")
    comment = mpn if mpn else note                       # generic part: value, package, tolerance as written
    comment = {"74650174": "74650174R"}.get(comment, comment)          # orderable REDCUBE number
    old = next((x for x in rows if x[0] == comment and x[2] == fp), None)
    if old:                                              # one line per part (e.g. R_G of HS and LS, U.FL H and L)
        old[1] += "," + ",".join(refs)
    else:
        rows.append([comment, ",".join(refs), fp, "", note, src])
    fitted.update(refs)
with open(os.path.join(OUT, NAME + "-BOM-JLC.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Manufacturer Part / value", "Sourcing note"])
    w.writerows(rows)

pos = list(csv.reader(open(os.path.join(FAB, NAME + "-pos.csv"), encoding="utf-8")))
n = 0
with open(os.path.join(OUT, NAME + "-CPL-JLC.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for ref, val, pkg, x, y, rot, side in pos[1:]:
        if ref not in fitted:
            continue
        w.writerow([ref, "%.4fmm" % float(x), "%.4fmm" % float(y), "Top" if side == "top" else "Bottom",
                    "%.0f" % (float(rot) % 360)])
        n += 1
missing = sorted(fitted - set(p[0] for p in pos[1:]))
print("%s: JLC BOM %d lines (%d parts), CPL %d placements%s -> %s" % (
    NAME, len(rows), len(fitted), n, ("; NOT in the pos file: " + " ".join(missing)) if missing else "", OUT))
