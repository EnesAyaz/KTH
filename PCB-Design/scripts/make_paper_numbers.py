"""
LaTeX macros with every number quoted in the conference paper (reports/paper/spb_building_block.tex), taken from the
same result files as the design-flow deck, so that paper and slides cannot drift apart:

  reports/slides/data/flow_numbers.json       inputs (phase current)
  reports/slides/data/revb_flow_numbers.json  V_m, LTspice 0.5 / 1 nH, n in parallel, thermal (revb_flow_figures.py)
  reports/slides/data/capacitor_compare.json  DC-bias derating and the selected MLCC
  reports/slides/data/final_numbers.json      Q3D of the final boards and the busbar (final_post.py)
  simulation/bb_q3d/results/loop_breakdown.json

    python scripts/make_paper_numbers.py  ->  reports/paper/paper_numbers.tex
Missing results are written as \\TBD (red), so a draft compiles before every Q3D run has finished.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "reports", "slides", "data")


def js(*p):
    f = os.path.join(*p)
    return json.load(open(f)) if os.path.exists(f) else {}


FN = js(D, "flow_numbers.json")
RF = js(D, "revb_flow_numbers.json")
CC = js(D, "capacitor_compare.json")
FQ = js(D, "final_numbers.json")
LB = js(ROOT, "simulation", "bb_q3d", "results", "loop_breakdown.json")
M = {}


def get(d, *keys):
    for k in keys:
        if not isinstance(d, (dict, list)):
            return None
        try:
            d = d[k]
        except (KeyError, IndexError, TypeError):
            return None
    return d


WORDS = {"1": "One", "2": "Two", "3": "Three", "4": "Four", "20": "Twenty", "50": "Fifty", "60": "Sixty",
         "80": "Eighty", "100": "Hundred", "120": "OneTwenty"}


def put(name, value, fmt="%.1f"):
    import re
    name = re.sub(r"\d+", lambda m: WORDS[m.group(0)], name)     # LaTeX macro names: letters only
    M[name] = (fmt % value) if value is not None else r"\TBD"


put("Irms", get(FN, "I_rms_leg"), "%.0f")
put("Ipk", get(FN, "I_pk"), "%.0f")
for i in (60, 80, 120):
    for L, tag in (("0.5nH", "A"), ("1nH", "B")):
        k = "%d_A_%s" % (i, L)
        put("Didt%d%s" % (i, tag), get(RF, "vm", k, "didt"), "%.0f")
        put("Vmax%d%s" % (i, tag), get(RF, "vm", k, "vm_max"), "%.0f")
for i in (60, 80, 120):
    put("Pcond%d" % i, get(RF, "cond", str(i), "P100"), "%.1f")
NUMW = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 8: "Eight"}
for L, tag in (("0.5nH", "A"), ("1nH", "B")):
    for n in (2, 3, 4, 6, 8):
        r = get(RF, "npar", L, n - 1) or {}
        w = NUMW[n]
        put("Tot%s%s" % (w, tag), r.get("tot"))
        put("Sw%s%s" % (w, tag), r.get("sw"))
        put("Vpk%s%s" % (w, tag), r.get("vpk"), "%.0f")
        if tag == "A":
            put("Cond%s" % w, r.get("cond"))
            put("Tj%s" % w, r.get("tj"), "%.0f")
            put("Pdev%s" % w, r.get("pdev"))
            put("Eta%s" % w, 100 * r["eta"] if "eta" in r else None, "%.2f")
th = RF.get("thermal", {})
put("Rpad", th.get("R_PAD"))
put("Rspr", th.get("R_SPR"))
put("Rjh", th.get("R_JH"))
put("TjAmbFourty", th.get("tj4_40"), "%.0f")
put("TjAmbTwentyfive", th.get("tj4_25"), "%.0f")
put("TjPadThree", th.get("tj4_40_3W"), "%.0f")
for f in ("20", "50", "100"):
    put("EtaF%s" % f, get(RF, "fsw", "eta4", f), "%.2f")
put("Nicap", get(RF, "fsw", "n_i"), "%d")
put("SwWaveA", get(RF, "wave", "0.5nH", "p_sw"))
put("SwWaveB", get(RF, "wave", "1nH", "p_sw"))
put("CondWave", get(RF, "wave", "0.5nH", "p_cond"))
sel = [p for p in CC.get("parts", []) if "226" in p["part"]]
if sel:
    put("CtwoEff", sel[0]["C_eff_uF"], "%.2f")
    put("CtwoRet", 100 * sel[0]["retention"], "%.0f")
    put("CtwoEsr", sel[0]["ESR50k_mOhm"], "%.1f")
    put("CtwoI", sel[0]["I_10K_A"], "%.2f")
put("IripLeg", CC.get("I_ripple_leg"), "%.1f")
for b, tag in (("dpt", "Dpt"), ("load", "Load")):
    lp = get(FQ, b, "loop") or {}
    put("Loop%s" % tag, lp.get("mean_nH"), "%.2f")
    put("Vos%s" % tag, lp.get("overshoot_30Apns_V"), "%.0f")
    c = [get(lp, "all_switching", "cell%d" % k) for k in range(1, 5)]
    if all(v is not None for v in c):
        for k, v in enumerate(c):
            put("Loop%sC%d" % (tag, k + 1), v, "%.3f")
        put("Loop%sSpread" % tag, (max(c) / min(c) - 1) * 100, "%.1f")
    put("Cu%s" % tag, get(LB, b, "copper"), "%.2f")
    put("Esl%s" % tag, get(LB, b, "esl_part"), "%.2f")
    put("Sh%s" % tag, get(LB, b, "shunt_part"), "%.2f")
    for p in ("HS", "LS"):
        put("Imb%s%s" % (tag, p), get(FQ, b, "dc", p, "imbalance_pct"), "%.0f")
        put("Rcu%s%s" % (tag, p), get(FQ, b, "dc", p, "R_copper_mOhm"), "%.2f")
    put("Pcu%s" % tag, get(FQ, b, "dc", "P_copper_W"), "%.0f")
    put("Lx%sHS" % tag, get(FQ, b, "lx", "HS"), "%.2f")
    put("Lx%sLS" % tag, get(FQ, b, "lx", "LS"), "%.2f")
    put("Skew%s" % tag, get(FQ, b, "lx", "dI_per_ns_A"), "%.0f")
put("DidtDptMax", 15.0 / get(FQ, "dpt", "loop", "mean_nH") if get(FQ, "dpt", "loop", "mean_nH") else None, "%.0f")
lb = get(FQ, "bank", "L_b_nH")
put("LbMin", min(lb) if lb else None, "%.2f")
put("LbMax", max(lb) if lb else None, "%.2f")
put("LtermBank", get(FQ, "bank", "L_term_bank_nH"), "%.2f")
put("BusLab", get(FQ, "level", "bus_ac", "L_leg12_nH"), "%.2f")
put("BusLac", get(FQ, "level", "bus_ac", "L_leg13_nH"), "%.2f")
put("BusLabDc", get(FQ, "level", "bus_dc", "L_leg12_nH"), "%.1f")
put("BusRab", get(FQ, "level", "bus_ac", "R_leg12_mOhm"), "%.2f")
put("BusPdc", get(FQ, "level", "dc", "P_bus_W"), "%.1f")
put("BusIterm", get(FQ, "level", "dc", "I_terminal_max_A"), "%.0f")
sh = get(FQ, "level", "ripple_50kHz", "share_of_leg")
for k, v in enumerate(sh or [None] * 3):
    put("Share%s" % "abc"[k], 100 * v if v is not None else None, "%.0f")

out = os.path.join(ROOT, "reports", "paper", "paper_numbers.tex")
with open(out, "w", encoding="utf-8") as f:
    f.write("% generated by scripts/make_paper_numbers.py - do not edit\n")
    f.write("\\providecommand{\\TBD}{\\textcolor{red}{\\textbf{TBD}}}\n")
    for k, v in sorted(M.items()):
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print("%d macros, %d TBD -> %s" % (len(M), sum(v == r"\TBD" for v in M.values()), out))
