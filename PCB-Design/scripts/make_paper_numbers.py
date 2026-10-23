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

# simulation validation with the Q3D copper (simulation/bb_q3d/revb_q3d_spice.py)
QS = js(D, "q3d_spice_numbers.json")
for key, tag in (("load", "Load"), ("dpt", "Dpt"), ("load_rg3", "LoadRgThree"), ("dpt_rg2.5", "DptRgLow"),
                 ("dpt_lumpgate", "DptLump")):
    q = QS.get(key, {})
    cells = q.get("cells", [])
    put("QsVh%s" % tag, q.get("VHpk_max"), "%.0f")
    put("QsVl%s" % tag, q.get("Vpk_max"), "%.0f")
    put("QsShare%s" % tag, q.get("share_off_pct"), "%.0f")
    put("QsShareEon%s" % tag, q.get("share_Eon_pct"), "%.0f")
    put("QsEon%s" % tag, sum(c["Eon_uJ"] for c in cells) / 4 if cells else None, "%.1f")
    put("QsEoff%s" % tag, sum(c["Eoff_uJ"] for c in cells) / 4 if cells else None, "%.1f")
    put("QsDidt%s" % tag, sum(c["didt_on"] for c in cells) / 4 if cells else None, "%.0f")
    put("QsBump%s" % tag, max(c["bump"] for c in cells) if cells else None, "%.1f")
    put("QsBumpMin%s" % tag, min(c["bump"] for c in cells) if cells else None, "%.1f")
    put("QsEonTot%s" % tag, q.get("Eon_tot_uJ"), "%.0f")
    put("QsEoffTot%s" % tag, q.get("Eoff_tot_uJ"), "%.0f")
    put("QsImin%s" % tag, min(c["I_off"] for c in cells) if cells else None, "%.0f")
    put("QsImax%s" % tag, max(c["I_off"] for c in cells) if cells else None, "%.0f")
lu = QS.get("lumped", {})
for i, tag in ((0, "Load"), (1, "Dpt")):
    put("QsLumEon%s" % tag, get(lu, "Eon_uJ", i), "%.1f")
    put("QsLumEoff%s" % tag, get(lu, "Eoff_uJ", i), "%.1f")
    put("QsLumVh%s" % tag, get(lu, "VHpk", i), "%.0f")
    put("QsLumVl%s" % tag, get(lu, "Vpk", i), "%.0f")

# loop-to-loop coupling between the four cells (loop_post.py: 1 A in one cell, voltage across every cell)
mc = get(FQ, "dpt", "loop", "mutual_cell_nH") or {}
kc = get(FQ, "dpt", "loop", "coupling_k") or {}
offd = [(mc[i][j], kc[i][j]) for i in mc for j in mc[i] if i != j]
put("CellMmax", max(m for m, _ in offd) * 1000 if offd else None, "%.0f")          # pH
put("CellKmax", max(k for _, k in offd) if offd else None, "%.3f")
# gate loops of driver block 1 on the DPT board (gate_post.py, copper only, 100 MHz)
GS = js(ROOT, "simulation", "bb_q3d", "results", "gate_summary_dpt.json")
gl = get(GS, "gate_loop_nH") or {}
if gl:
    g0 = {q: gl[q]["esl0.0"] for q in gl}
    put("GateHS", (g0["Q1"]["on"] + g0["Q2"]["on"]) / 2, "%.1f")
    put("GateLS", (g0["Q3"]["on"] + g0["Q4"]["on"]) / 2, "%.1f")
    put("GatePairHS", (g0["Q1"]["on_pair_driven"] + g0["Q2"]["on_pair_driven"]) / 2, "%.1f")
    put("GatePairLS", (g0["Q3"]["on_pair_driven"] + g0["Q4"]["on_pair_driven"]) / 2, "%.1f")
    put("GateSym", 100 * max(abs(g0["Q1"]["on"] / g0["Q2"]["on"] - 1), abs(g0["Q3"]["on"] / g0["Q4"]["on"] - 1)), "%.1f")
    sp = get(GS, "split_nH", "esl0.0") or {}
    put("GateBranchHS", (sp["Q1"]["branch"] + sp["Q2"]["branch"]) / 2, "%.1f")
    put("GateBranchLS", (sp["Q3"]["branch"] + sp["Q4"]["branch"]) / 2, "%.1f")
    put("GateCommonHS", sp["Q1"]["common_on"], "%.1f")
    put("GateCommonLS", sp["Q3"]["common_on"], "%.1f")
    cp = get(GS, "coupling_pH") or {}
    put("GateCoupMax", max(abs(v) for st in cp.values() for v in st["both_cells"].values()), "%.0f")
    vg = get(GS, "v_gk_at_30Apns_V") or {}
    put("GateVgkMax", max(abs(v) for st in vg.values() for v in st.values()), "%.2f")

out = os.path.join(ROOT, "reports", "paper", "paper_numbers.tex")
with open(out, "w", encoding="utf-8") as f:
    f.write("% generated by scripts/make_paper_numbers.py - do not edit\n")
    f.write("\\providecommand{\\TBD}{\\textcolor{red}{\\textbf{TBD}}}\n")
    for k, v in sorted(M.items()):
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print("%d macros, %d TBD -> %s" % (len(M), sum(v == r"\TBD" for v in M.values()), out))
