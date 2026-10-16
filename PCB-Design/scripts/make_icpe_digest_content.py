"""
Content of the ICPE 2027-ECCE Asia digest (5 pages, one column, blind review), with every number taken from
reports/paper/paper_numbers.tex (scripts/make_paper_numbers.py), i.e. the same results as the IEEE paper draft.

    python scripts/make_icpe_digest_content.py   -> reports/paper/icpe/digest_content.json
    powershell -File scripts/build_icpe_digest.ps1 -> reports/paper/icpe/SPB_BB_ICPE2027_digest.docx / .pdf

Mini markup inside text: _{..} subscript, ^{..} superscript, *..* italic, **..** bold.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "paper", "icpe")
IMG = os.path.join(OUT, "img")

N = {}
for line in open(os.path.join(ROOT, "reports", "paper", "paper_numbers.tex"), encoding="utf-8"):
    m = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}\s*$", line)
    if m:
        N[m.group(1)] = m.group(2)
missing = []


def n(k):
    v = N.get(k, "")
    if not v or "TBD" in v:
        missing.append(k)
        return "??"
    return v


def typo(s):
    """en dash in number and citation ranges"""
    s = re.sub(r"(?<=\d)-(?=\d)", "–", s)
    return s.replace("]-[", "]–[")


def runs(s):
    """mini markup -> [[text, fmt], ...]; fmt is a string of flags: s(ub) p(sup) i(talic) b(old)"""
    s = typo(s)
    out = []
    pat = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]*\}|\^\{[^}]*\})")
    for tok in pat.split(s):
        if not tok:
            continue
        if tok.startswith("**"):
            out.append([tok[2:-2], "b"])
        elif tok.startswith("*"):
            out.append([tok[1:-1], "i"])
        elif tok.startswith("_{"):
            out.append([tok[2:-1], "s"])
        elif tok.startswith("^{"):
            out.append([tok[2:-1], "p"])
        else:
            out.append([tok, ""])
    return out


B = []


def h1(t):
    B.append({"t": "h1", "text": t})


def p(t):
    B.append({"t": "p", "runs": runs(t)})


def fig(img, w, cap):
    B.append({"t": "fig", "img": os.path.join(IMG, img), "w_cm": w, "cap": runs(cap)})


def eq(um, k):
    B.append({"t": "eq", "um": um, "n": k})


def table(cap, rows, widths):
    B.append({"t": "table", "cap": runs(cap), "rows": [[runs(c) for c in r] for r in rows], "w_cm": widths})


def ref(t):
    B.append({"t": "ref", "runs": runs(t)})


TOPIC = ("Topic categories: 17. Power Electronics for Transportation Electrification; "
         "01. Power Devices (Si / Wide Band Gap) and Applications")
TITLE = "Building Block Design for Stacked Polyphase Bridge Converters for High-Voltage Traction Drives"
ABSTRACT = (
    "In a stacked polyphase bridge (SPB) converter the battery voltage is shared by series-connected three-phase "
    "submodules, so the transistor voltage class becomes a design variable. This digest presents the design of the "
    "phase-leg building block of a 1200 V, 300 kW SPB traction inverter. Because the phase current does not depend "
    "on the number of submodules, 100 V GaN transistors give the lowest loss, and the turn-off overshoot at a "
    "realistic commutation-loop inductance sets 16 submodules of 75 V. Four EPC2361 per switch, driven as two "
    "mirrored pairs by one dual-channel isolated driver each, keep the junction temperature at %s °C. The leg is "
    "built as a double-pulse-test (DPT) board with a coaxial shunt in every cell and as a load-test board without "
    "shunts. Q3D extraction of the routed boards gives %s nH per cell without and %s nH with the shunt. A "
    "double-pulse simulation with the complete extracted parasitic network confirms current sharing among the four "
    "cells within %s %% and a peak drain-source voltage of %s V at the peak phase current. Double-pulse "
    "measurements on the DPT board will be added in the final paper."
    % (n("TjFour"), n("LoopLoad"), n("LoopDpt"), n("QsShareLoad"), n("QsVhLoadRgThree")))

# ------------------------------------------------------------------------------------------------ I
h1("Introduction")
p("High-voltage traction batteries push two-level inverters to 1200 V transistors and large voltage steps at the "
  "machine terminals. The stacked polyphase bridge (SPB) converter [1], [2] connects *N* three-phase bridges in "
  "series on the dc side, each feeding one winding set of a multiphase machine. Every submodule blocks only "
  "*V*_{bus}/*N*, which allows low-voltage transistors and reduces the voltage step and the dc-link capacitance "
  "[3], [4]. Control, dc-link stability and machine design of the SPB have been studied [2]-[6], and a GaN-based "
  "SPB was found competitive with a three-level flying-capacitor inverter [7].")
p("The submodule itself has received little attention. At 1200 V and 300 kW each leg conducts %s A_{rms} at 75 V, "
  "so several GaN transistors must be paralleled, and paralleled low-voltage GaN stages are limited by turn-off "
  "overshoot [8], uneven dynamic current sharing [9], [10] and gate disturbances. Designs with up to eight devices "
  "per switch [11], [12] start from a given bus voltage. In an SPB the submodule voltage is free, and it is coupled "
  "to the device count and the layout through the loop inductance. This work contributes: (i) a selection of the "
  "device voltage class and the submodule voltage that includes the loop inductance; (ii) a gate-drive arrangement "
  "for four paralleled GaN transistors per switch based on a current-sharing sensitivity analysis; (iii) a "
  "four-cell leg board in a test and an operating version, verified by Q3D extraction and by a double-pulse "
  "simulation with the complete extracted parasitic network." % n("Irms"))

# ------------------------------------------------------------------------------------------------ II
h1("Device and Submodule Voltage")
fig("fig_spb.png", 16.0,
    "Fig. 1: (a) SPB inverter with *N* submodules (SM) of *V*_{m} = *V*_{bus}/*N*. (b) Building block, one phase "
    "leg: four commutation cells (QH, QL: EPC2361) with bypass capacitors *C*_{byp}, a common bank *C*_{bank} and "
    "one ac output; one dual-channel driver per pair of cells; shunt (dashed) on the DPT board only. (c) Gate "
    "circuit with the common-source inductance *L*_{CS} up to the Kelvin pad K.")
p("For *N* submodules sharing the power equally (Fig. 1a), the inverter power is")
eq("P=3N P_(\"leg\")=(3M V_(\"bus\"))/(2√2) I_(\"ph\") cos⁡φ", 1)
p("so the phase current is independent of *N*: with *M* = 1.15 and cos φ = 0.9, 300 kW at 1200 V require %s A_{rms} "
  "(%s A peak) in every leg. Since every submodule carries the full current, the conduction loss scales with "
  "*N I*^{2}*R*_{DS(on)}/*n* and the output-charge loss with *N n f*_{sw}*C*_{oss,tr}*V*_{m}^{2} for *n* devices "
  "per switch. Optimizing *n* gives" % (n("Irms"), n("Ipk")))
eq("P_(\"min\")=6 I V_(\"bus\") √(f_(\"sw\") R_(\"DS(on)\") C_(\"oss,tr\"))", 2)
p("in which the voltage class cancels to first order. Ten GaN transistors of the 100-650 V classes are therefore "
  "ranked by the time constant τ = *R*_{DS(on)}*C*_{oss,tr} and, since conduction dominates, by the on-resistance "
  "per volt of blocking capability (Fig. 2). The 100 V class leads in both; EPC2361 (0.75 mΩ) reaches 7.5 µΩ/V, "
  "three to thirty times below the higher-voltage parts. The submodule voltage then follows from the overshoot at "
  "turn-off,")
eq("V_m+L_(\"loop\") di∕dt≤90 \"V\"", 3)
p("A vertical loop over a 0.1 mm dielectric reaches about 0.5 nH per cell, whereas a measurement shunt raises it to "
  "about 1 nH. With the turn-on rate of %s A/ns at 80 A per device, (3) allows %s V at 0.5 nH and %s V at 1 nH. An "
  "even *N* is required for symmetric winding sets, so *N* = 16 and *V*_{m} = 75 V are selected; the operating "
  "hardware must therefore stay close to 0.5 nH." % (n("DidtEightyA"), n("VmaxEightyA"), n("VmaxEightyB")))
fig("dev_compare.png", 14.5,
    "Fig. 2: Device selection (datasheet values). (a) *R*_{DS(on)} against *C*_{oss,tr} with lines of constant τ; "
    "(b) both per volt of blocking capability; (c) SPBs from the best device of each class, normalized: minimum "
    "loss (2), devices per switch, submodules, voltage step and transistor count.")

# ------------------------------------------------------------------------------------------------ III
h1("Devices per Switch, Gate Drive and DC Link")
p("The leg loss over a fundamental period is computed from LTspice switching energies at 0.5 and 1 nH, with the "
  "junction temperature and *R*_{DS(on)} solved together for the thermal path of the load-test hardware (fan "
  "heatsink 0.65 K/W, %s K/W from junction to heatsink per device). One device per switch runs away thermally and "
  "two reach %s °C (Fig. 3). Three devices exceed 90 V. Four devices dissipate %s W per leg at %s °C and 40 °C "
  "ambient with %s V peak at 0.5 nH, but %s V at 1 nH; four per switch are chosen."
  % (n("Rjh"), n("TjTwo"), n("TotFourA"), n("TjFour"), n("VpkFourA"), n("VpkFourB")))
fig("flow_npar2.png", 14.5,
    "Fig. 3: *n* EPC2361 per switch at %s A_{rms} and 50 kHz. (a) Semiconductor loss per leg, 0.5 nH (left) and "
    "1 nH (right, hatched); (b) junction temperature on the load-test heatsink; (c) peak *v*_{DS} at the peak "
    "current per device." % n("Irms"))
table("Table I: Switching-energy imbalance of two paralleled EPC2361 (LTspice, 75 V, 120 A)",
      [["**Asymmetry**", "**Imbalance**", "**Layout measure**"],
       ["Power loop, *L*_{D} +0.3 nH", "2 %", "mirrored cells"],
       ["Gate loop, *L*_{G} 2 vs. 8 nH", "19 %", "star gate network"],
       ["No Kelvin, *L*_{CS} +0.2 nH", "29 %", "Kelvin return per device"],
       ["Threshold, *V*_{th} +0.3 V", "7 %", "one channel per pair"]],
      [5.6, 2.4, 5.0])
p("Dynamic sharing is dominated by the gate loop and the common-source path, not by the power loop (Table I). One "
  "channel for all four devices of a switch is excluded, since the slower gate charging raises the turn-on energy "
  "by 31 %% and the sink current exceeds the 8 A rating. One 2EDF7275K (isolated high- and low-side channel) is "
  "therefore placed on the symmetry line between two mirrored cells and drives both gates through a star with "
  "Kelvin returns (Fig. 1b); a Zener split of its supply gives +5.1 V and −1.2 V against the Miller-induced gate "
  "bump. The three legs of a submodule share one dc bus, so only the switching-frequency ripple remains: 3 %% ripple "
  "requires 127 µF effective per leg, and with only %s %% of the nominal value left at 75 V, twenty 22 µF 2220 "
  "MLCCs are placed on each leg board, plus ten 1 µF 0805 bypass capacitors per cell." % n("CtwoRet"))

# ------------------------------------------------------------------------------------------------ IV
h1("Leg Board in Two Versions")
fig("boards.png", 16.0,
    "Fig. 4: Leg board, four EPC2361 per switch (89.5 × 85.2 mm, four layers). (a) DPT board with a coaxial shunt per "
    "cell; (b) load-test board with fan heatsink; (c) Q3D model of the cells, generated from the routed copper "
    "(red dc+, blue dc−, orange switch node).")
p("The four-layer board (2 oz, 0.1 mm dielectric between L1 and L2) carries the cells as two mirrored pairs, each "
  "with its driver in the centre; every commutation loop closes vertically on the dc− plane directly below "
  "(Fig. 4). Vias removed for clearance are removed together with their mirror image. The driver inputs, with one "
  "common-mode choke per signal pair and a ferrite bead in the 12 V feed, keep 4.0 mm (outer) and 3.0 mm (inner "
  "layers) from all power copper, the IPC-2221B spacing for 1200 V, so the layout is ready for a reinforced isolated "
  "driver; the 2EDF7275K used here provides functional isolation for the 75 V tests. Measuring every cell current "
  "requires a shunt in each low-side source, which lengthens the loop and blocks the heatsink, so the same design "
  "is built twice: the DPT board carries a 1 mΩ coaxial shunt per cell and U.FL probes for *v*_{GS} and *v*_{DS}; "
  "the load-test board connects the sources through blind vias to the dc− plane and carries the heatsink. Q3D "
  "extraction with all four cells switching gives %s nH per cell on the load-test board (%s nH copper, %s nH "
  "capacitor ESL), equal in the four cells within %s %%, and %s nH on the DPT board, where the shunt and its "
  "connection add 0.24 nH. Three load-test boards form a level on a laminated PCB busbar with %s nH between "
  "neighbouring legs." % (n("LoopLoad"), n("CuLoad"), n("EslLoad"), n("LoopLoadSpread"), n("LoopDpt"), n("BusLab")))

# ------------------------------------------------------------------------------------------------ V
h1("Validation With the Extracted Parasitics")
p("To check the lumped design against the routed copper, the extracted network was inserted into a double-pulse "
  "circuit: the 100 MHz partial-inductance matrix of cells, bypass pads, shunt lands and switch-node copper as one "
  "inductor per terminal with every mutual coupling (29 inductors and 400 couplings for the load-test board), the "
  "dc resistance matrix including its mutual terms as behavioural sources, eight EPC2361 models, the bypass "
  "capacitors with dc-bias capacitance and ESL, the shunts, the bank and two drivers with star gates and Kelvin "
  "returns. The load current is switched at the peak phase current (Fig. 5).")
fig("q3d_spice_2x2.png", 14.5,
    "Fig. 5: Double-pulse simulation with the Q3D-extracted copper, 75 V, 316 A (≈ 80 A per device), "
    "*R*_{g,on} = 2 Ω. (a) Low-side turn-off and (b) turn-on on the load-test board, four cells: drain current "
    "(solid), *v*_{DS} (dashed). (c) High-side *v*_{DS} at the low-side turn-on vs. the lumped model. (d) Switching "
    "energy per device in each cell; lines: lumped model.")
p("The four cells carry %s-%s A at turn-off and their turn-on energies differ by %s %%, so the mirrored layout and "
  "the per-pair drive leave none of the mechanisms of Table I active. The low-side turn-off is uncritical (%s V). "
  "The critical event is the low-side turn-on, at %s A/ns: the high-side device peaks at %s V on the load-test "
  "board, in agreement with the lumped model at the extracted loop (%s V), and at %s V on the DPT board. Turn-on "
  "energies agree with the lumped model within 10 %%. With *R*_{g,on} = 3 Ω the turn-on slows to %s A/ns and the "
  "peaks drop to %s V and %s V for a 20 %% higher turn-on energy (below 1 W per leg); both boards are operated "
  "with 3 Ω. The gate bump of %s V with a 0 V off-state confirms the need for the negative off-state voltage."
  % (n("QsIminLoad"), n("QsImaxLoad"), n("QsShareEonLoad"), n("QsVlLoad"), n("QsDidtLoad"), n("QsVhLoad"),
     n("QsLumVhLoad"), n("QsVhDpt"), n("QsDidtLoadRgThree"), n("QsVhLoadRgThree"), n("QsVhDptRgThree"),
     n("QsBumpLoad")))

# ------------------------------------------------------------------------------------------------ VI
h1("Experimental Verification in the Final Paper")
p("The final paper will add double-pulse measurements on the DPT board at 75 V up to the peak phase current of "
  "%s A: the four cell currents through the coaxial shunts, *v*_{DS} and *v*_{GS} of every cell through the U.FL "
  "probe points, the overshoot for *R*_{g,on} = 2 and 3 Ω, and the measured switching energies and their spread, "
  "compared with the simulation of Section V. Continuous operation of the load-test board will verify the thermal "
  "design." % n("Ipk"))

# ------------------------------------------------------------------------------------------------ VII
h1("Conclusion")
p("Because the phase current of an SPB is independent of the number of submodules, the device and the submodule "
  "voltage can be chosen for minimum loss and the available overshoot margin. For a 1200 V, 300 kW inverter this "
  "gives 16 submodules of 75 V with four 100 V GaN transistors per switch, driven in mirrored pairs by one "
  "dual-channel isolated driver each. Q3D extraction of the routed board gives %s nH per cell, and a double-pulse "
  "simulation with the full extracted network confirms equal sharing among the four cells and a peak voltage of "
  "%s V with *R*_{g,on} = 3 Ω." % (n("LoopLoad"), n("QsVhLoadRgThree")))

h1("References")
for r in [
    "[1] S. Norrga, L. Jin, O. Wallmark, A. Mayer, and K. Ilves, \"A novel inverter topology for compact EV and HEV "
    "drive systems,\" in *Proc. IECON*, 2013, pp. 6590-6595.",
    "[2] L. Jin, S. Norrga, O. Wallmark, and M. Nikouei Harnefors, \"Control and modulation of the stacked polyphase "
    "bridges inverter,\" in *Proc. IEEE ECCE*, 2014.",
    "[3] L. Jin, S. Norrga, O. Wallmark, and N. Apostolopoulos, \"Modulation and power losses of a stacked polyphase "
    "bridge converter,\" *IEEE J. Emerg. Sel. Topics Power Electron.*, vol. 5, no. 1, pp. 409-418, 2017.",
    "[4] T. Bringezu and J. Biela, \"Control of a 9-phase PMSM with stacked polyphase bridge converter including dc "
    "source impedance,\" in *Proc. EPE ECCE Europe*, 2023.",
    "[5] M. Nikouie, O. Wallmark, L. Jin, L. Harnefors, and H.-P. Nee, \"DC-link stability analysis and controller "
    "design for the stacked polyphase bridges converter,\" *IEEE Trans. Power Electron.*, vol. 32, no. 2, "
    "pp. 1666-1674, 2017.",
    "[6] L. Verkroost *et al.*, \"Multi-agent control scheme for power distribution in a multi-three-phase motor "
    "drive fed by a stacked polyphase bridges converter,\" *IEEE Trans. Energy Convers.*, vol. 39, no. 4, "
    "pp. 2568-2580, 2024.",
    "[7] G. Rohner, J. Huber, S. Mirić, and J. W. Kolar, \"Comparative evaluation of three-phase three-level flying "
    "capacitor and stacked polyphase bridge GaN inverter systems for integrated motor drives,\" *Electronics*, "
    "vol. 13, no. 7, 1259, 2024.",
    "[8] J. A. Brothers and T. Beechner, \"GaN module design recommendations based on the analysis of a commercial "
    "3-phase GaN module,\" in *Proc. IEEE ECCE*, 2019, pp. 4109-4116.",
    "[9] J. Lu and D. Chen, \"Paralleling GaN E-HEMTs in 10 kW-100 kW systems,\" in *Proc. IEEE APEC*, 2017, "
    "pp. 3049-3056.",
    "[10] M. T. Tran *et al.*, \"A high-performance GaN power module with parallel packaging for high-current and "
    "low-voltage traction inverter applications,\" *IEEE J. Emerg. Sel. Topics Power Electron.*, vol. 13, no. 1, "
    "pp. 1188-1209, 2025.",
    "[11] M. Wattenberg, O. G. Lorenz, and J. Sanchez, \"A multi-kilowatt low-profile GaN inverter for light "
    "electric vehicles and high-power tools,\" in *Proc. IEEE APEC*, 2023, pp. 1443-1450.",
    "[12] M. W. J. Cooke and D. J. Rogers, \"120 V, 155 A traction inverter using eight parallel GaN HEMTs,\" 2026.",
]:
    ref(r)

COMPLIANCE = ("Statement of compliance: this digest complies with the export control laws of the country in which "
              "the authors reside; the required clearances have been obtained prior to submission.")

json.dump({"topic": TOPIC, "title": TITLE, "abstract": runs(ABSTRACT.replace("-1.2", "−1.2")), "blocks": B,
           "compliance": runs(COMPLIANCE)},
          open(os.path.join(OUT, "digest_content.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
words = len(re.sub(r"[_^*{}]", "", ABSTRACT + " ".join(
    "".join(r[0] for r in b.get("runs", [])) for b in B)).split())
print("blocks %d, words %d, missing %s" % (len(B), words, sorted(set(missing))))
