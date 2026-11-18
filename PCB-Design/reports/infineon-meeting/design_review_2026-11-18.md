# Review: Infineon briefing deck (reports/infineon-meeting/index.html)

Date: 2026-11-18. Read-only review. Sources checked: all 23 screenshots, the slide HTML, the JS data arrays (REVB, WAVES, NPAR, SINGLE, BOLT, SW_I/EON*/EOFF, BMP_SIM, DEV), reports/slides/data/q3d_spice_numbers.json, img/loop_breakdown.png, and the board renders in img/.

Slide order used for every reference (order of <section> blocks):
1 s1 Title, 2 s2 DC link, 3 s3 Bottleneck, 4 s4 SPB, 5 s5 Device choice, 6 s6 Benchmark, 7 s7 Design procedure, 8 s7b Devices per switch, 9 s8 Prototype, 10 s9 Overshoot, 11 m1 KiCad, 12 m2 Q3D, 13 m3 Waveforms, 14 s10 Sharing model, 15 s11 Dynamic sharing, 16 s12 Board asymmetry, 17 s13 Driver sink, 18 s14 Gate bump, 19 s15 100 vs 200 V, 20 s16 Switching frequency, 21 dv Device requirements, 22 s17 Questions, 23 s18 Next steps.

The "slide N" references in the text are all correct (9 to 16, 12 to 16, 14 to "next slide" = 15, 21 to 5/8/10/12/13/14-15/17/18/19), with one exception (E4). Agenda data-go targets are correct.

---

## 1. Errors and mistakes

| # | Slide | Exact text / element | Why it is wrong | Suggested fix |
|---|---|---|---|---|
| E1 | 20 | Tiny note "Leg loss from the simulated leg efficiency (99.77 / 99.71 / 99.61 % at 20 / 50 / 100 kHz, 2.65 kW leg), fitted as 5.0 W + 0.053 W/kHz"; readout "7.7 W loss per leg / 99.71 %"; left chart y axis 0 to 16 W | 300 kW / 48 legs = 6.25 kW per leg. Slides 6, 7, 8 give 18.0 W per leg at 50 kHz and the same 99.71 %. 18 W / 6.25 kW = 0.29 % gives 99.71 %. 7.7 W / 2.65 kW gives the same 99.71 %. So the same efficiency is shown as 7.7 W here and 18.0 W on four other slides. The 16 W axis cannot even show the 18 W design point. motor() hard-codes 2652 and 5.04+0.053*f. | Rebase to the 6.25 kW leg. Losses at 20 / 50 / 100 kHz become about 14.4 / 18.1 / 24.4 W (fit about 11.9 W + 0.125 W/kHz), and the y axis should be 0 to 40 W. Recompute from the loss model rather than from rounded efficiencies. If 2.65 kW is a different operating point, say so and do not reuse "per leg". |
| E2 | 7 | "1 → 2 devices gives the large loss gain; 3 adds little but needs a second driver channel." | The slide 8 data (NPAR) shows the opposite. Going 1→2 saves 12.2 W (51.7→39.5 W) and 2→3 saves 16.3 W (39.5→23.2 W). It is 3→4 (−5.2 W) and above where the gain gets small. | "2 → 3 → 4 cut the leg loss 39.5 → 23.2 → 18.0 W; above 4 the gain is < 2.2 W, and every pair needs another channel." |
| E3 | 12 | Readout "0.46 + 0.06 + 0.12, DPT loop per cell [nH]: copper, bypass ESL, shunt and its path" next to the bullet "The shunt and its path add 0.24 nH per cell" | The same phrase "shunt and its path" is given as 0.12 nH and as 0.24 nH. In loop_breakdown.png the 0.12 is "UFCS 120 pH + its path", and the 0.46 copper already includes the path to the shunt (load board copper is 0.35). The 0.24 is the board-to-board difference (0.646 − 0.408). | Readout label: "copper (incl. shunt path), bypass ESL, shunt body". Bullet: "The shunt (0.12 nH) and the longer copper to it (about 0.11 nH) add 0.24 nH per cell." |
| E4 | 21 | Row "Voltage class", column "Where it comes from": "slides 3, 13, 19" | Slide 3 is the two-level bottleneck chart. It says nothing about the 75 V cell, the 90 V limit or the 92.9 V peak. The 90 V limit is on slides 8 and 10. | "slides 8, 10, 13, 19" |
| E5 | 10 | Slider "Loop per cell" shows 0.640 nH; legend "DPT board 0.646 nH" | ovL has min 0.2 and step 0.02, so the value 0.646 snaps to 0.640 and the readout gives 94.2 V for the wrong loop. At the default the magenta "your setting" line also covers the amber DPT line exactly, so only two of the three legend lines are visible. | Use step 0.002 (or a default of 0.65 with step 0.01). Draw the user line thinner or dashed, or hide it when it equals a board line. |
| E6 | 10 | Readout colour pk>92 → "warn"; "max di/dt per cell at this loop" = (100 − V)/L | The design limit everywhere else is 90 V (slides 8, 13, 21). Here the warning starts at 92 V and the "max di/dt" is computed to the 100 V rating. | Warn above 90 V. Label the readout "max di/dt to 100 V rating", or compute it to 90 V. |
| E7 | 10 | "di/dt per cell in our simulations: 23–36 A/ns at turn-off, up to 50 A/ns with low R_g." | The Rev B runs shown on slide 13 (q3d_spice_numbers.json) give turn-off di/dt of 37–42 A/ns in every case. Turn-on is 36 A/ns at 3.5 Ω and 49 A/ns at 2.5 Ω. The 23–36 range looks like an older Rev A number. | "36 A/ns turn-on at 3.5 Ω (49 A/ns at 2.5 Ω), 37–42 A/ns at turn-off (Rev B, LTspice)". |
| E8 | 20 | "raising R_g,off above the critical ≈ 1.5 Ω makes turn-off channel-controlled and E_off grows tenfold" | The chart next to it (60 A default) shows E_off going 7.1 → 9.5 → 15.5 µJ (0 / 2 / 5 Ω) and 28.5 µJ at 10 Ω. That is 2 to 4 times, not ten. Tenfold only appears at 157 A with 10 Ω (92 vs 8.4 µJ). | "...E_off grows 2–4× at 60 A and up to 10× at full current." |
| E9 | 6, 7 | "68.8 °C junction, 40 °C ambient, 0.65 K/W per leg" | A reader computes 40 + 18.0 W × 0.65 K/W = 51.7 °C, not 68.8 °C. The thermal path in the label is incomplete. | State the full path, e.g. "heatsink 0.65 K/W per leg + junction-to-sink per device", or drop the K/W from the label. |
| E10 | 17 | "E_on +16 / +31 % for 3 / 4 transistors. Four per switch is our upper limit." | The chart's x axis is "transistors per driver channel". "Per switch" (4 per switch is the design) contradicts the point being made. | "Four per channel is our upper limit." |
| E11 | 13 | Load board (button "Load · 2 Ω", turn-on): readout "1.23 V high-side gate bump peak (V_th,min 0.8 V)", shown red | The note for this case ("Load board without shunts ... 90.9 V high-side peak") does not mention that the gate goes above V_th,min. It also shows 90.9 V > 90 V limit. This is the reason the DPT board uses −1.9 V. | Add: "At 0 V off-state the high-side gate reaches 1.23 V, above V_th,min; this is why the DPT board uses −1.9 V." |
| E12 | 8 | Chart "Peak V_DS of one device": SINGLE 0.5 nH = 86.9 V at 60 A, then 82.6 V at 80 A; 1 nH curve 87.2 V at 40 A, then 83.2 V at 60 A | The peak drops with more current, and the two curves cross near 60 A. An application engineer will ask about it. It also makes the n = 4 marker (82.6 V at 80 A) look as if it was picked at a dip. The readout uses NPAR 83.1 V, a different number from the marker. | Check the LTspice extraction (ringing-peak sampling). If it is real, add one line explaining the dip. Use one value for marker and readout. Add "V" to the y axis. |
| E13 | 3, 5, 6, 8, 10, 13–20, 22 | Underscore notation in visible text: "R_DS(on)" (6 prose, 19, 22), "C_oss,tr" (5, 19 prose vTxt, 22), "V_th" (22), "E_on / E_off" (13, 15, 17, 20), "I_diff" (14, 15), "T_j", "V_DS" (8), "HS V_GS" (16), "v_GS,HS", "R_g,on" (14, 18, 20), "R_g,off,tot" (17), axis titles "√(R_on,sp · C_oss,sp)", "C_oss,tr = Q_oss/V", "blocking voltage U_B" | The rest of the deck uses real subscripts. Raw underscores look like code in prose and in readouts (ro() writes HTML, so <sub> would work). | Use <sub> in readouts, prose and the Q array. In SVG use a tspan with baseline-shift="sub" or plain forms ("Rds,on"). At minimum fix prose and readouts. |
| E14 | 13, 16, 17, 18 | "-0.50 V", "-15.3 %", "-1.0 V", "bump to -0.02 V", "LS turn-off: -2.26 V" | fmt() outputs a hyphen-minus. Static text uses a true minus (−4.9 V), so the same quantity looks different. | In fmt(): .toFixed(d).replace("-","−") |
| E15 | 13, 18, 21 | "abs. min −4 V" (13 readout), "abs. max −4 V" (18 chart), "−4 V absolute minimum" (21), "limit −4 V" (16) | Three names for one rating. | One wording everywhere, e.g. "V_GS min −4 V (abs. max rating)". |
| E16 | 3 | Legend "√(R_on,sp·C_oss,Q,sp)" vs body text and y axis "C_oss,sp" | Two symbols for the same quantity on one slide. | Use C_oss,Q,sp (the fit in the footnote) everywhere. |
| E17 | 2 | Table "t txt big": header cells right-aligned (table.t th {text-align:right}), body cells left-aligned | "DC link" and "Power" headers do not sit over their columns (visible in 02.png, "Power" is far right of "250 kW"). | table.t.txt th {text-align:left} |
| E18 | 2 | "Infineon eCAV platform, 800 V, 250 kW" | No public Infineon product of that name could be found. Infineon's public 250 kW traction reference is "REF-CAV250KMT7INV" (HybridPACK Drive). A wrong name of the audience's own product is the worst kind of error in this room. | Check the name with the source. If in doubt, write "Infineon 250 kW CAV traction reference design (HybridPACK Drive)". |

## 2. Contradictions

| # | Slides | Statement A | Statement B | Why it matters / fix |
|---|---|---|---|---|
| C1 | 13 vs 9, 16, 23 | 13: "The four cells turn on together", readout "0.7 % spread of the peak cell currents" on the Rev B DPT board (REVB dpt: peaks 130.3–131.2 A) | 9: "±15.3 % turn-on split between cells"; 16: Rev B "one centre bolt", ±15.3 %, HS V_GS −4.9 V; 23: redraw "to remove the ±15 % turn-on split" | The same board is shown as perfectly balanced and as 15 % unbalanced. The difference is evidently the AC take-off (slide 13 runs use the power-loop matrix without the 42 / 5.5 mm AC bus) and 75 vs 80 V. Add to slide 13's note: "AC take-off not included; with the one-bolt AC bus the split is ±15.3 % (slide 16)". |
| C2 | 7, 11, 13, 17, 18, 21, 22 | 7: "+5 / −1 V split from one 6 V isolated rail"; 11: "5.1 V Zener split"; 17 and 18 defaults −1.0 V | 13 and 21: DPT board "V_off −1.9 V"; 18: "window is −1.7 V ± 0.3 V"; 17 ask "+5/−2 V"; 22 "−1…−2 V" | Infineon will ask what the off-state voltage is. A 6 V rail with a 5.1 V Zener gives about −0.9 V, which cannot be −1.9 V. Give one story: the board value (−1.9 V) and the rail that produces it. Set the slide 17/18 slider defaults to −1.9 V (or label −1 V as "block model"). |
| C3 | 20 vs 6, 7, 8, 9 | 7.7 W per leg at 50 kHz, 99.71 % | 18.0 W per leg at 50 kHz, 99.71 % | See E1. |
| C4 | 14 vs 15 (and 20) | 14 (defaults 2 Ω, 6 nH mismatch = 2 vs 8 nH, 60 A per transistor): "E_on Q1 / Q2 36.3 / 9.7 µJ" (symmetric 23 µJ each, the single-device sweep, also used on 20: 2 / 0 Ω = 30 µJ) | 15 (LTspice, same case "Gate 2 / 8 nH", 120 A pair = 60 A each, 2 Ω): E_on 19.2 / 4.9 µJ, symmetric 9.3 µJ each | Same conditions on adjacent slides, energies 2 to 2.5 times apart. Slide 14 even says "the real waveforms are on the next slide". Either scale slide 14's E_on to the two-device LTspice, or state the difference in setup (single device vs pair, integration window 100 ns, high-side device). |
| C5 | 1, 11, 16, 18, 23 | 1: "Rev B, double-pulse board in fabrication"; 11: "KiCad exports of the released design" | 23: stage 2 "Rev B, layout done", "Redraw with two AC bolts in progress"; stage 3 "NOW: order, assemble". 16 calls Rev B "one centre bolt" and the two-bolt version "Redraw". 18 button calls the two-bolt version "4 parallel Rev B, two bolts". | It is unclear whether the board being ordered is the one-bolt Rev B or the redraw, and "Rev B" names both. Pick one name for the two-bolt board (e.g. "Rev B2"). Change slide 1 to the true status ("layout done, two-bolt redraw before order"). |
| C6 | 1, 3, 4, 7, 19, 21 vs 9–16 | "16 × 75 V stacked cells", "16 cells at 100 V", "One cell designed once" (SPB stage = three-phase 75 V bridge) | "four cells, two drivers" on one leg board, "loop per cell", "Four cells at 322 A", "the cells in parallel form the 4 × EPC2361 switch" (cell = one HS + one LS EPC2361 in parallel) | One word for two different things. A listener hears "16 cells, each with 4 cells". Slide 23 already uses "level" for the 75 V stage. Use "level" (or "stage") for the 75 V SPB unit on slides 1, 3, 4, 7, 19, 21. Keep "cell" for the commutation cell, so "loop per cell" stays as the house rule says. |
| C7 | 1 vs 3 | 1: "instead of using 1200–1700 V devices" | 3: "Two-level 1200 V needs 1700–2000 V SiC" | 1200 V devices cannot run a 1200 V link. Use "1700–2000 V devices" on slide 1. |
| C8 | 8 vs 13, 21 | 8: "n = 4 passes ... V_DS ≤ 90 V at 0.5 nH" (83 V) | 13 / 21: DPT board 92.9 V and load board 90.9 V high-side peak, both above the 90 V limit | The design check uses 0.5 nH. The real boards are 0.65 / 0.41 nH, and both exceed the limit. Add one line on slide 8: "on the drawn boards: 92.9 V (DPT, 0.65 nH), 90.9 V (load board) at 322 A, see slide 13". |
| C9 | 18 vs 7 | 18 readout "0.29 W dead-time loss per leg (10 ns, 50 kHz)" at the default −1 V | 7: "dead time 0.46 W" per leg (NPAR n = 4: 0.464 W) | Same quantity, same frequency. Calibrate Pd in bump() to 0.46 W at the design point, or state the different conditions. |
| C10 | 5 vs 19 vs 21, 22 | 5: hypothetical 200 V part defaults 1.6 mΩ / 700 pF (τ 1.12 ps) | 19: defaults 1.5 mΩ / 1200 pF (τ 1.80 ps, C_oss loss 1.33×); 21: "τ ≤ 1.5 ps"; 22: "C_oss,tr ≈ 700–900 pF" | The "200 V device" changes between slides. Set slide 19's default C_oss,tr to 900 pF (the parity value its own text derives) so that it agrees with 5, 21 and 22. |
| C11 | 14, 18, 22, 23 | 14: "turn-on dv/dt (sim.) 15.8 V/ns" (2 Ω, 60 A); 18 title: "our 25–30 V/ns" | 18 ask / 22: "50+ V/ns", "50 V/ns"; 23: "CMTI ≥ 200 V/ns" | Different conditions, which is fine, but none is labelled. Add the condition to slide 14's readout ("single device, 60 A"). The CMTI figure refers to stack-to-ground transients; say so on slide 23. |
| C12 | 18 | Bullet "window is −1.7 V ± 0.3 V" (−1.4 … −2.0 V) | Chart band drawn from −1.29 to −2.05 V (bump(), mode b) | Draw the band at −1.4 … −2.0 V (log: centre −1.65 V, Zener ±0.3 V). |

## 3. Orphaned letters, bad wraps, overlaps, cut-off text

| # | Slide | Element | Problem (seen in screenshot) | Fix |
|---|---|---|---|---|
| W1 | 5 | fomChart labels | "EPC2215" and "EPC2034C" print on top of each other; "τ=5 ps" is under them; "τ=2 ps" is under "IGC033S10S1"; "τ=1 ps" is under the "200 V?" diamond | Per-device label offsets (EPC2215 label to the left/below). Move the τ labels to the right end of each line (pts.length*0.9) or into the top margin. |
| W2 | 16 | boltSvg bar labels "28.8 %" | Struck through by the dashed 25 % line | Put the value inside the bar or above max(bar, line) + 6 px. |
| W3 | 10 | "100 V rating" label | Crossed by the blue load-board line | Move it to the left end or above the red band. |
| W4 | 18 | gbCurve "0.98 V" label | Overlaps the black LTspice points | Put the label below-right of the teal dot, or with a leader. |
| W5 | 17 | dkE "23.3" label | Centred on the vertical n = 2 marker line | Offset the labels by +8 px in x, or draw the marker behind them with a gap. |
| W6 | 3 | "2-level 1200 V" | Label touches the SiC line and the marker circle | Move it to the upper left of the marker. |
| W7 | 7 | Step 1 "phase current fixed, voltage class open; 228 / A_rms per phase" | Number split from its unit | 228&nbsp;A<sub>rms</sub> |
| W8 | 9 | "2 × / 2EDF7275K", "1200 / V spacing" | "2 ×" alone at line end; "1200" split from "V" | 2&nbsp;×&nbsp;2EDF7275K, 1200&nbsp;V |
| W9 | 12 | Readout "0.46 + 0.06 + / 0.12" | Sum broken over two lines in the 22 px mono value | Shorter value ("0.46+0.06+0.12") or white-space:nowrap and a smaller font for this one. |
| W10 | 13 | Readout "high-side gate bump peak (V_th,min 0.8 / V)" | Lone "V)" | 0.8&nbsp;V, or a shorter label "HS gate bump (V_th,min 0.8 V)" |
| W11 | 15 | Explanation "E_on 19.2 / : 4.9 µJ"; tiny note "after 8 / µs" | Ratio split; number split from unit | 19.2&nbsp;:&nbsp;4.9&nbsp;µJ, 8&nbsp;µs (also in the WV strings) |
| W12 | 16 | Readout "HS V_GS minimum at 80 / V (limit −4 V)"; "current split between / cells" | "80" split from "V" | 80&nbsp;V, shorter labels |
| W13 | 18 | Bullet "... discharges it (τ / ≈ 2.6 ns)" | Lone "(τ" at line end | (τ&nbsp;≈&nbsp;2.6&nbsp;ns) |
| W14 | 19 | Bullet "R_200 = 2·R_100 = / 1.5 mΩ" | Equation split | nbsp around "=" |
| W15 | 20 | "above the critical ≈ 1.5 / Ω makes ..."; readout "current ripple vs 20 / kHz" | Lone "Ω"; lone "kHz" | 1.5&nbsp;Ω, 20&nbsp;kHz |
| W16 | 22 | "< / 0.2 Ω pull-down", "CMTI ≥ / 200 V/ns", "(460 / V).", "≈ 1.5–2 / mΩ", "4- / parallel" | Operators and units split from numbers; lone "V)." | nbsp after "<", "≥", "≈" and before units in the Q strings |
| W17 | 23 | Isolation card "for a stack 1200 / V above ground" | Number split from unit | 1200&nbsp;V |
| W18 | 3, 5, 6, 10 | Readouts "device class (≤ 75 % / use)", "R for parity at this / C_oss", "semiconductor efficiency, 300 / kW", "max di/dt per cell at this / loop" | One-word orphans in readout labels | Shorten the labels ("class at ≤ 75 % use", "parity R", "semicond. efficiency", "max di/dt at this loop") or nbsp the last two words. |
| W19 | 13, 23 | Titles wrap to two lines and push the logo down | Visual inconsistency only, nothing cut | Optional: shorten. |
| W20 | 14 | shSweep magenta curve flat at 60 % for R_g < 1 Ω | Clipped at the axis top with no indication; reads as a real plateau | Raise y1 to 100 % or mark the clip ("> 60 %"). |

Nothing is cut off at the slide edges in any of the 23 screenshots.

## 4. Unreadable small print

Canvas scale: the 1280 px canvas fills about 1197 px of the 1400 px screenshots. SVG text is 11 px in viewBox units, so the effective size depends on the chart width.

| # | Slide | Element | Rendered size (canvas px) | Necessary? | Action |
|---|---|---|---|---|---|
| S1 | 13, 15, 18 | Small charts in cards: rbE (energy per cell), wvE (energy per device), gbCurve (bump vs dv/dt): tick labels, "cell 1…4", "E_on/E_off", "0.8 V", value labels | about 9.8 px (viewBox 520 in about 464 px) | Yes: the energy bars and the bump-vs-dv/dt points are the evidence | Keep, enlarge (13 px for these), or set the viewBox width to about 440 so the 11 px text scales up. |
| S2 | 8 | npVds axis ticks, "0.5 nH / 1 nH / 90 V" labels, "80 A per device"; npChart T_j / V_DS pills | about 10.5 px | Yes: the pass/fail pills and the 90 V line are the slide's argument | Keep, enlarge to 12–13 px. |
| S3 | 13, 15 | Main waveform charts: axis titles "i_D per cell [A]", "v_DS [V]", "HS v_GS", tick numbers | about 10.3 px | Yes | Keep, enlarge the axis text to 12–13 px. Axis titles can go in the legend line. |
| S4 | 3, 5, 10, 14, 16, 17, 19, 20 | All other SVG axes and labels (11 px) | 11–11.5 px | Yes (axes, device names on 5, cell boxes on 16) | Keep, raise the global svg text to 12.5–13 px. Then recheck W1 (more collisions on slide 5). |
| S5 | 9 | Image "Gate star" (gate_star.png): four matplotlib panels with labels | Text about 4–5 px, illegible | The idea yes, the printed detail no | Replace with one panel (the L1 star with Kelvin underneath), cropped and enlarged, or drop the image and keep the caption. |
| S6 | 11 | KiCad schematic images (sch_power.png etc.) in a 470 px box | Text about 3–5 px, illegible | As proof that it is a real design, yes; as content, no | Crop to one cell plus the driver star at readable size, or accept as an illustration. |
| S7 | 12 | Colour legend inside q3d_loop_dpt.png ("DC+ (DCP)" …) | about 7 px | No: the caption under the image already gives the colours | Can stay (decorative) or be cropped out. |
| S8 | 1 | Thumbnail sim_waves.png (LTspice) | Illegible | No: title-slide thumbnail | Fine as a picture. |
| S9 | 3, 6, 13, 14, 15, 16, 17, 20, 23 | .tiny notes (12.5 px) | 12.5 px, borderline | Mostly yes: they carry conditions (75 V, 322 A, R_G, V_off, model basis). Slide 15's note is 6 lines. | Keep 3, 6, 13, 16, 17 (conditions, formula), enlarge to 13.5 px. Shorten slide 15's note to two lines (drop the i_QH formula). On 23, the sentence repeats slide 21's footer and can be removed. |
| S10 | 1 | .strip figcaption (11.5 px) and agenda times (12 px) | 11.5–12 px | Captions: no (the images are self-explanatory); agenda: yes | Remove captions or enlarge to 13 px. |
| S11 | 7, 23 | .tag "INFINEON: DRIVER / DEVICE" and .chip "DONE / NOW / NEXT" | 10.5 px bold mono, readable by weight | Yes: they are the hook for this audience | Enlarge to 12 px. |
| S12 | all | Footer "KTH · SPB GaN building block · n / 23" | 11 px | Not needed in the meeting | Leave as is. |

## 5. Off-message for this audience

| # | Slide | Element | Problem | Fix |
|---|---|---|---|---|
| O1 | 1, 9, 11 (Layout and 3D tabs), 23 | Silkscreen "DESIGNED BY CLAUDE" in revb_dpt.png, v1_dpt.png, revb_dpt_top.png, v1_pcb_top.jpg (readable in the 3D render on slide 9 and the top-copper view on slide 11) | Visible tool or author credit on the board in front of an industrial partner. It invites the wrong discussion and undercuts the authorship on slide 1. | Re-render without that silkscreen line (the Alstom deck renders already had board text removed), or crop and blur. Check whether the line is on the released Gerbers too. |
| O2 | 2 | "KTH SiC inverter, 1.7 kV eTruck modules" | Reads like an internal project name, and the slide 2 brief only allowed DC link and power for the SiC inverters | "KTH SiC inverter, 1.7 kV modules" |
| O3 | 23 | "today: shunt and TI TMCS1123"; slide 2 "TI / Wolfspeed reference design" | Competitor parts named in an Infineon meeting. Acceptable as context, but the TMCS1123 line can come across as an advertisement | Optional: "today: shunt and a Hall-effect sensor IC". |
| O4 | 11, 12 | "Generated, not drawn. A Python generator writes the schematic, places and routes the board..."; "UFCS" in loop_breakdown.png | Not wrong, but it uses time on tooling, and "UFCS" is an unexplained part code | Optional: shorten to one line; caption "UFCS = coaxial 1 mΩ shunt". |
| O5 | 11 | "per-pair CM chokes", "common-mode choke" | This is the gate-supply choke, not the motor common-mode topic, but it can open the deliberately excluded common-mode discussion | Optional: "supply chokes" in the readout. |

Two-level SiC results, bearing currents, fault tolerance and pole changing do not appear. Slide 3's "0.67× vs 2-level 1700 V SiC" is from published device fits, not KTH SiC results. Slide 6 compares only part counts. Loop inductance is quoted per cell everywhere, and "per switch position" does not occur.

---

## Five most important fixes

1. Slide 20 leg loss (E1/C3). Rebase the frequency chart to the 6.25 kW leg (about 18 W at 50 kHz, 0–40 W axis). At the moment the same 99.71 % is 7.7 W here and 18.0 W on slides 6–9.
2. One Rev B story (C1, C5). Say on slide 13 that the 0.7 % spread excludes the AC take-off and that the one-bolt board splits ±15.3 % (slide 16). Give the two-bolt redraw its own name, and correct "in fabrication" on slide 1 and "released design" on slide 11 to match slide 23.
3. One gate off-state voltage (C2, C9, C12). −1.9 V on the DPT board, the rail that actually gives it (not "6 V rail, +5/−1 V"), slider defaults on 17/18 set to it, the 18 window band matching "−1.7 ± 0.3 V", and dead-time loss calibrated to 0.46 W.
4. Remove "DESIGNED BY CLAUDE" from all board renders (O1) on slides 1, 9, 11 and 23, and drop "eTruck" (O2).
5. Numbers that contradict their neighbours. Slide 7 "3 adds little" (E2), slide 12 shunt 0.12 vs 0.24 nH (E3), slide 14 E_on 36/10 vs slide 15 19/5 µJ (C4), slide 21 reference "slides 3, …" (E4), the 0.640 nH slider (E5). Then do one global pass: non-breaking spaces between numbers and units (W7–W17), <sub> instead of underscores (E13), true minus signs (E14), and SVG text at 12.5 px or more (S1–S4).