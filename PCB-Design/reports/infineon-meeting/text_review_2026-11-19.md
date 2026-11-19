# Text review of the Infineon meeting deck (index.html), 2026-11-19

Independent read-only review of `reports/infineon-meeting/index.html` (29 slides) against the renders
`scratchpad/pdf/01.png … 29.png` (default state, 2560 × 1440). Slide numbers below are the PNG numbers.
Fixed conventions (cell / switch / branch, version 1, bins (matched sets), 12.2 A wording, eTruck, Times New Roman)
are not flagged; only places that break them are.

## Top 10 (fix these first)

1. Slide 20, step 4 bullet (#81): "two 150 kW blocks per leg" contradicts the deck's leg (48 legs at 6.25 kW, slide 28). Replace: "Each leg: 4 × EPC2361 per switch, one 2EDF7275K per two branches (2 drivers per leg)."
2. Slide 24, readout "4 branches" (#93): "the branches in parallel form the 4 × EPC2361 switch" breaks the definitions (four branches form a leg). Replace: "four in parallel form one leg (4 × EPC2361 per switch)".
3. Slides 6 and 25, figure loop_breakdown.png (#20): axis labels say "loop per cell", "per cell", "mean of 4 cells", "load-test board" where the deck means branch / load board. Regenerate the plot with "branch".
4. Slide 10 (#40, #41): the Problem box quotes the four-parallel model (−3.3 V), but the slide opens on "2 parallel (block model)" and plots −2.96 V; "block model" is undefined. Make the four-parallel view the default and rename the other toggle "2 parallel (earlier layout)".
5. Slide 8 card 2 (#30): "toward the −4 V limit (−4.9 V on version 1)" — −4.9 V is beyond the limit and comes from the one-bolt AC path, not the negative bias. Replace: "(−3.3 V in the model; −4.9 V on version 1 with one AC bolt)".
6. Slide 25 title and slides 5/6 (#98, #99): "0.46 + 0.06 + 0.12 = 0.65 nH" adds to 0.64; "0.12 + 0.11 … add 0.24 nH" adds to 0.23. Fix the rounding or write "≈".
7. Slide 15 questions (#60, #61): "< 0.2 Ω" and "R_DS(on) ≈ 1.5–2 mΩ, C_oss,tr ≈ 700–900 pF" contradict the main ask "≤ 0.2 Ω", "≤ 1.5 mΩ and ≤ 900 pF".
8. Repeated numbers that differ between slides (#16, #23, #84, #105, #80): 81 A vs ≈ 80 A per transistor; 90 V "target" / "design limit" / "upper limit"; 99.7 % / 69 °C vs 99.71 % / 68.8 °C; 18.1 W vs 18.0 W per leg; off-voltage −1.65 / −1.7 / −1.9 V and on-rail +5 / +5.1 V without one sentence that says which is which.
9. Slide 9 (#33, #34, #36, #37, #39) and slide 13 (#52): bullets 2–3 repeat the Problem / Ask boxes word for word, the driver ask is copied in full into the slide 13 table, and five orphans ("supplies.", "model.", "limit.", "switch)", "≈ 1.5 Ω)") sit on this one slide. Delete bullet 2, shorten bullet 3 and the table cell.
10. Slide 22 title (#87, #69): "From one branch to a four-parallel leg board", but the earlier layout already had two branches (2 per switch). Replace: "From a two-branch block to a four-branch leg board" (and the backup-index link).

Also high on the list: slide 3 "every cell is a small, low-voltage half-bridge problem" (#9, a cell is a three-phase bridge) and slide 1 "stacked-GaN" (#1, the deck's term is stacked cell).


## Findings by slide (main talk)

Categories: U = unnecessary text, G = grammar / spelling / wording, O = orphan or split number/unit, C = inconsistency / convention break.

### Slide 1 (title)
1. [C] Lead sentence: "in a stacked-GaN 1200 V traction inverter". The deck's term is the stacked cell; "stacked-GaN" is coined here only. Replace: "in a stacked-cell 1200 V traction inverter".
2. [O] Hope card 2: "a recipe for 50 V/ns with gate / margin" ("margin" alone). Replace: "a recipe for 50 V/ns with enough gate margin" or shorter "a 50 V/ns recipe with gate margin".
3. [C] Hope card 4: "a CoolGaN part near 1.5 mΩ and 900 pF" while slides 8, 12, 13, 14 say "≤ 1.5 mΩ and ≤ 900 pF". Replace: "a CoolGaN part with ≤ 1.5 mΩ and ≤ 900 pF".

### Slide 2 (higher DC link)
4. [O] Table, Porsche row: "800 V / class" and "700 kW / (launch)" each break over two lines ("class" and "(launch)" alone). Replace "800 V class" with "≈ 800 V" and "700 kW (launch)" with "700 kW".
5. [O] Table, first row: "(HybridPACK / Drive)" ("Drive)" alone). Replace: "Infineon REF-CAV250KMT7INV" (drop the bracket) or "Infineon HybridPACK Drive reference (REF-CAV250KMT7INV)" if the column is widened.
6. [O] Bullet 2: "… 33 % less cable mass than / 800 V." ("800 V." alone). Replace: "Our 1.2 kV study: 56 % less cable loss or 33 % less cable mass than at 800 V." is still long; better: "Our 1.2 kV study vs 800 V: 56 % less cable loss or 33 % less cable mass."
7. [O] Bullet 3: range split across lines "1700– / 2000 V devices". Replace: "The cost moves to the semiconductors: a two-level 1200 V inverter needs 1.7–2 kV devices."
8. [C] Units: this slide mixes "1200 V" and "1.2 kV" (table rows "1.2 kV", bullets "1.2 kV battery", "1200 V inverter"); the rest of the deck uses "1200 V". Use "1200 V" in the KTH rows and bullets, keep kV only for device classes ("1.7 kV modules").

### Slide 3 (SPB topology)
9. [C] Last paragraph: "every cell is a small, low-voltage half-bridge problem". A cell is a three-phase bridge (three half-bridges), per the deck's own definition. Replace: "Why it suits GaN: each cell is three small low-voltage half-bridges, the problem GaN is best at."
10. [U] Caption under the figure repeats the table and the title ("Each cell is a standard two-level three-phase bridge. Cells are in series on the DC side; each feeds its own three-phase winding set."). Replace whole caption: "Proposed at KTH (Norrga et al., 2013)."
11. [C] Table mixes "Two-level" (row 1) and "identical 2-level bridge" (SPB row), "one 3-phase" vs "three-phase" in the caption. Replace "identical 2-level bridge" with "identical two-level bridge" and "one 3-phase" with "one three-phase" (or keep "3-phase" everywhere in the table only).
12. [C] Stack sketch label (JS spb()): "one block = one 75 V cell". "Block" is a second name for the cell. Replace: "one square = one 75 V cell".

### Slide 4 (why 100 V GaN)
13. [O] Readout: "device class (≤ 75 % / use)" ("use)" alone). Replace label (JS dfom()): "class at ≤ 75 % of rating" or shorter "device class (75 % rule)".
14. [C] Same slide uses "2-level" (chart label "2-level, 1200 V link (1700 V SiC)", readout "min. loss vs 2-level 1700 V SiC") and "two-level minimum" (bullet 1). Pick one; suggest "two-level" in the bullet and leave the chart labels, or change the readout to "min. loss vs two-level 1700 V SiC".
15. [G] Bullet 1: "split into 16 cells, 100 V GaN gives 0.67× the two-level minimum" — the reference is not stated in the sentence. Replace: "split into 16 cells, 100 V GaN reaches 0.67× the minimum of a two-level 1700 V SiC inverter."

### Slide 5 (building block)
16. [C] Readout (JS bbCount()): "81 A per transistor at 322 A". Everywhere else the deck says "≈ 80 A per transistor" (slides 7, 14). Replace the format with "≈ 80 A" (322/4 = 80.5 rounds up to 81 in toFixed).
17. [U] Bottom note: "Version 1: layout done, two-bolt redraw before ordering, not yet measured. Loss model: 99.71 % … 68.8 °C junction." The status already sits on the title slide KPI and the efficiency/T_j are on slide 6 tab 4. Shorten: "Version 1, not yet measured. Model: 99.71 % (semiconductors, 300 kW, 50 kHz), T_j 68.8 °C."
18. [C] Hot-spot text Branch 1 (BB_HS c1): "six bypass MLCCs at the pads", while the Q3D figure on slide 6 says "as built (6 top + 4 bottom)" and the design procedure says "40 × 1 µF" per leg (= 10 per branch). Replace: "six top and four bottom bypass MLCCs at the pads".
19. [C] Hot-spot Driver U1 (BB_HS d1): "a 5.1 V Zener splits them into +5 / −1.65 V"; slide 20 and 24 say "+5.1 V on, about −1.65 V off". Use "+5.1 / −1.65 V".

### Slide 6 (design flow, default tab 2)
20. [C] Figure loop_breakdown.png (right image, also slide 25): axis labels "loop per cell (nH), Q3D", "top-row bypass 0805 per cell", "loop inductance per cell (nH), mean of 4 cells". Here "cell" means branch, which breaks the deck's fixed definition (cell = 75 V three-phase bridge) on the slide where loop inductance is explained. Also "load-test board" vs "load board". This is a plot, not a board render: regenerate with "per branch", "mean of 4 branches", "load board".
21. [U] Caption right: "Loop per branch: 0.46 copper + 0.06 bypass ESL + 0.12 shunt = 0.65 nH; 0.41 nH without the shunt (load board); 0.7 % spread between branches." The bar chart directly above shows the same numbers. Shorten: "0.65 nH per branch with the shunt, 0.41 nH without; 0.7 % spread between branches."
22. [G] Tab 4 bullet (MC[3]): "Results go back into the layout: 2.5 Ω gives 105 V, above the rating, so we chose 3.5 Ω." Gate resistance is not layout. Replace: "Results go back into the design: 2.5 Ω gives 105 V, above the rating, so we chose 3.5 Ω."
23. [C] Tab 4 chart (mcChart): "90 V target"; slide 7 caption says "90 V design limit", slide 13 "90 V upper limit", slide 21 "V_DS ≤ 90 V" limit. Use one term: "90 V design limit".

### Slide 7 (waveforms)
24. [C] Title says "(≈ 80 A per transistor)", the caption below says "322 A double pulse (≈ 80 A per branch)". Use "per transistor" in both (it is the switching transistor current).
25. [U] Bottom caption (6 lines, smallest text on the slide) repeats the title (75 V, 322 A), the button labels (lumped gate, boards) and the readout. Replace with: "LTspice, EPC2361 vendor model, Q3D power loop and extracted gate stars of each board; equal 1 nH AC take-off per branch (one-bolt case: backup). V_off −1.9 V (DPT), 0 V (load). Dotted: 90 V limit, 100 V rating."
26. [O] Same caption, last line is "rating." alone. Fixed by the replacement in 25.
27. [O] Readout 4: "high-side gate bump peak (V_th,min / 0.8 V)" ("0.8 V)" alone). Replace label (JS revb()): "HS gate bump peak (V_th,min 0.8 V)".
28. [C] Note text "over the 90 V target" — see 23; replace "target" with "design limit".
29. [C] Load-board note (NOTE.load): "With 0 V off-state the high-side gate reaches 1.23 V", while slides 8, 10 and 13 state "1 V bump at 0 V off". Both may be right (different run), but the audience will see two numbers for the same statement. Add the condition: "… reaches 1.23 V at 2 Ω (load board), above V_th,min …".

### Slide 8 (four problems)
30. [C] Card 2 problem text: "pushes the turn-off spike toward the −4 V limit (−4.9 V on version 1)". −4.9 V is beyond the limit, and on slides 10, 11, 27 it is caused by the one-bolt AC path (problem 3), not by the negative bias. Replace: "… pushes the turn-off spike toward the −4 V limit (−3.3 V in the model; −4.9 V on version 1 with one AC bolt)."
31. [O] Card 5: "Samples and SPICE models for all / four." ("four." alone). Also unclear what "all four" refers to (four problems? four devices?). Replace: "Ask: Parts for one SPB leg, measured against our EPC2361 board on the same double-pulse bench, with SPICE models."
32. [O] Card 2: hyphenated "off- / voltage" split at the line end. Accept, or use "negative off-state bias" (no hyphen at risk).

### Slide 9 (problem 1, driver)
33. [U] Right column bullet 2: "We drive pairs: 4 per switch needs 2 channels, so the inverter needs 96 drivers and 192 isolated supplies." repeats the Problem box word for word. Delete.
34. [U] Right column bullet 3: "We would rather not add a driver per pair: one driver that sinks about 22 A … could drive all four transistors of a switch." repeats the Ask box. Shorten to: "At 0.35 Ω pull-down a four-transistor channel needs 15 A; at 0.2 Ω, 22 A." (keeps the one new number).
35. [G] Bullet 1 end: "We use two per channel; four per switch is our upper limit." The second half is unclear on a driver-sharing slide (four per switch or per channel?). Replace: "We use two per channel." (the "4 per switch" choice is shown in backup).
36. [O] Problem box: last line "supplies." alone. Replace the box text: "One 2EDF7275K channel must sink 12.2 A to turn off two EPC2361 (0.35 Ω pull-down, 0 Ω turn-off gate resistance setting); it is rated 8 A. So one channel per pair: 96 driver ICs, 192 isolated supplies." (also drops "at −1.7 V off", see 80).
37. [O] Ask box: last line "model." alone. Shorten: "… (2EDF7275K: 8 A, 460 V functional), and a current-limited SPICE model of the 2EDF7275K." or cut the bracket (it duplicates the Problem box): "… so one channel drives a whole switch of four EPC2361; plus a current-limited 2EDF7275K SPICE model."
38. [O] Bullet 1: last line "limit." alone; solved by 35.
39. [O] Readouts (JS sink()): "R_g,off,tot per transistor (R_crit / ≈ 1.5 Ω)" and "drivers in the inverter (4 per / switch)" ("switch)" alone). Replace labels: "R_g,off total per transistor (crit. 1.5 Ω)" and "driver ICs in the inverter".

### Slide 10 (problem 2, gate bump)
40. [C] The Problem box quotes the four-parallel model ("−3.3 V at 28 V/ns … with four in parallel"), but the slide opens with the toggle on "2 parallel (block model)", so the chart shows "LS turn-off: −2.96 V". The speaker's number and the plotted number differ. Make "4 parallel, two-bolt redraw" the default (aria-pressed) or quote −3.0 V for the default.
41. [C] Toggle label "2 parallel (block model)": "block" is not defined anywhere on the main slides. Replace: "2 parallel (earlier layout)".
42. [U] Bullet: "…; the pull-down hardly matters (0.05 Ω: 1.07 V, 0.5 Ω: 1.12 V)." repeats "What we tried" ("0.05 Ω: 1.07 V bump"). Replace bullet: "C_GD·dv/dt charges the off gate faster than the gate loop discharges it (τ ≈ 2.6 ns), so a stronger pull-down hardly helps."
43. [O] Same bullet: last line "1.12 V)." alone; fixed by 42.
44. [G] Readout "margin undershoot → −4 V": the Problem box calls the same thing "turn-off spike". Replace label (JS bump()): "margin of the turn-off spike to −4 V".

### Slide 11 (problem 3, current sharing)
45. [O] "What we tried": last line "progress." alone. Replace: "Kelvin source on every device, star gate routing, mirrored branches; a two-bolt redraw is in progress." (one word shorter per clause; or "…; redraw with two AC bolts under way.")
46. [G] Note text (WV gate 2/8): "so Q1 takes the load current over from the high side almost alone". Replace: "so Q1 takes over the load current from the high side almost alone".
47. [C] Note text (WV "Drain +0.3 nH", visible when that case is clicked): "the two branches then exchange current in a slow ring". This study is two paralleled devices, not branches. Replace "branches" with "devices".
48. [U] Energy bar chart in the right card renders with 5–6 px numbers at 1280 × 720 (bar labels "19.2", "4.9", "6.7", "7.4" and axis ticks); the same values are in the readouts above. Either delete the chart card or give the SVG a fixed height ≥ 150 px with preserveAspectRatio so it fills the card.

### Slide 12 (problem 4, voltage class)
49. [U] Bullet 3: "Half the cells: half the drivers, isolated supplies and stack connections." repeats the paragraph above the chart ("halves the cells, drivers and isolated supplies") and the title. Delete.
50. [C] Ask box: "16 samples" while the joint-test ask (slides 8, 14) is "parts for one SPB leg" (8 transistors at 4 per switch). State why 16: "16 samples (two legs)" or "samples for one leg".
51. Layout: x-axis title "200 V design relative to today's 100 V design" overlaps the tick labels "0.5×" and "1×". Move the label down or reduce tick font (vBars axes, m.b).

### Slide 13 (device requirements)
52. [U] Driver row, right cell repeats the slide 9 Ask box verbatim (4 lines, the longest cell). Replace: "isolated GaN driver: ≥ 22 A sink at ≤ 0.2 Ω, +5 / −1.7 V split outputs, CMTI ≥ 200 V/ns, 1200 V isolation; one channel per switch".
53. [G] Same cell starts with a capital ("An isolated GaN driver") while every other cell in the column starts lower case ("100 V, or …", "the same per device …", "higher V_th,min …"). Fixed by 52.
54. [O] Current row: "≈ 130 A peak at / turn-on" ("turn-on" alone). Replace: "≈ 57 A_rms per device (228 A_rms / 4); 130 A turn-on peak".
55. [O] Gate margin row: "−4.9 V on one-bolt version / 1; gate limit −4 V" ("1" separated from "version"). Replace: "1 V bump at 0 V off vs V_th,min 0.8 V; −1.65 V off (−1.4 to −1.9 V); turn-off spike −3.3 V (model), −4.9 V on version 1 (one bolt); limit −4 V".
56. [O] Paralleling row: "about 2 : 1, a 2 / vs 8 nH" (number "2" split from "vs 8 nH"). Replace: "4 in parallel; 2 vs 8 nH gate loops split E_on 4 : 1, a 0.3 V V_th spread about 2 : 1".
57. [C] Voltage class row: "90 V upper limit" — see 23 (one term: "90 V design limit").

### Slide 14 (thank you)
58. [O] Card 2: "…, or a device with more gate / margin?" ("margin?" alone). Replace: "Your 50 V/ns solution, with values: RC-coupled EiceDRIVER, Miller clamp, or more gate margin?" (same change on slide 8 card 2 keeps them identical).
59. [C] Status line: "version 1 layout done, ordering Nov–Dec 2026" omits the two-bolt redraw that slides 1, 5 and 29 put before ordering. Replace: "version 1 layout done, two-bolt redraw, ordering Nov–Dec 2026; …".

## Findings by slide (backup)

### Slide 15 (question list)
60. [C] Gate drivers Q1: "≥ 22 A peak sink, < 0.2 Ω pull-down" while slides 8, 9, 13, 14 say "≤ 0.2 Ω". Replace "<" with "≤".
61. [C] Devices Q4: "200 V CoolGaN roadmap: R_DS(on) ≈ 1.5–2 mΩ, C_oss,tr ≈ 700–900 pF" while the main ask (slides 8, 12, 13, 14) is "≤ 1.5 mΩ and ≤ 900 pF"; 2 mΩ fails our own break-even. Replace: "200 V CoolGaN roadmap: R_DS(on) ≤ 1.5 mΩ, C_oss,tr ≤ 900 pF, Kelvin source? Samples?"
62. [O] Gate drivers Q1: "< / 0.2 Ω" (symbol split from number). Replace: "Driver for paralleled GaN: ≥ 22 A peak sink at ≤ 0.2 Ω, one channel for 4 transistors?" and check the wrap.
63. [O] Gate drivers Q4: last line "(460 V)." alone. Replace: "Drivers for a cell 1200 V above ground: reinforced isolation, small package, CMTI ≥ 200 V/ns?" (the 460 V fact is on slides 9 and 13).
64. [O] Gate bump Q3: "(−4 / +6 V)" split inside the bracket. Replace: "Gate limits (−4 / +6 V) under repetitive ringing: lifetime data for short negative spikes?"
65. [O] Devices Q1: last line "paralleling?" alone. Replace: "V_th distribution within and between lots; bins (matched sets) or matched reels?"
66. [O] Devices Q4: range split "≈ 1.5– / 2 mΩ" and "Samples?" alone; fixed by 61.
67. [O] Thermal Q2: "in a 4- / layer board?" (hyphenated number split). Replace: "Recommended via-in-pad or blind-via landing for a low-voltage GaN source pad in a four-layer board?"
68. [G] Gate drivers Q4 (if kept): "The 2EDF7275K is functional (460 V)." reads as "the part works". Replace: "The 2EDF7275K has 460 V functional isolation."

### Slide 16 (backup index)
69. [C] Link label "From one branch to the leg board" follows the slide 22 title, which is wrong (see 87). Replace: "From the two-branch block to the leg board".

### Slide 17 (charging current)
70. [U] Card heading "Charging: current and cable loss" repeats the slide title one line above. Delete the h3.
71. [O] Readout 3: "copper section for equal loss density vs / 800 V" ("800 V" alone). Replace label (JS charging()): "copper section vs 800 V (equal loss density)".
72. [C] Slider shows "1000 kW" while slide 2 says "1 MW". Show MW for values ≥ 1000 kW, or label the slider in MW.

### Slide 18 (real devices)
73. [O] Paragraph: last line "part:" alone. Replace the last sentence: "Click a device or move the 200 V part:" (the legend already says "hypothetical 200 V part").
74. [C] Eyebrow "Backup · Why SPB · real devices" while the backup index groups this slide under "Why high voltage and 100 V GaN" and the main-talk counterpart is "Why 100 V GaN". Replace: "Backup · Why 100 V GaN · real devices" (slide 19 likewise: "Backup · Why 100 V GaN · what it buys and what it costs").
75. Layout: the "200 V?" diamond label overlaps the "EPC2071" label in the default state. Move one of the labels.

### Slide 19 (loss and part count)
76. [C] Table: "DC-link capacitor banks | 1 | 16 (MLCC, 134 µF eff. per leg)". 16 banks are per cell, the capacitance is per leg (three legs per cell). Replace: "16 (one per cell, 3 × 134 µF eff.)" or "48 (one per leg, 134 µF eff.)".
77. [C] Table row "Switch positions": the deck's term is "switch". Replace: "Switches".
78. [O] Readout 2: "per leg (4 × EPC2361 per / switch)" ("switch)" alone). Replace label: "per leg, 4 per switch".
79. [C] Caption "Analytical loss model at 1.2 kV": rest of the deck writes 1200 V (see 8).

### Cross-slide: gate supply voltages
80. [C] The off-state voltage appears as −1.65 V (Zener split: slides 10, 13, 20, 24), −1.7 V (sink calculation, slider defaults and "split outputs (+5 / −1.7 V)": slides 9, 10, 13) and −1.9 V (LTspice runs: slides 7, 20). The on-rail is "+5" (slides 9, 13, BB_HS d1) and "+5.1 V" (slides 20, 24). Keep −1.65 / +5.1 V as the design values, and add once under the slide 9 formula: "−1.7 V ≈ the −1.65 V Zener split; LTspice runs use −1.9 V (window end)."

### Slide 20 (design procedure)
81. [C] Bullet (step 4): "The 300 kW target uses two 150 kW blocks per leg: 4 × EPC2361 per switch, 2 drivers per leg." In this deck a leg is one of 48 legs at 6.25 kW (slide 28: "Per 6.25 kW leg (300 kW / 48)"), so "two 150 kW blocks per leg" contradicts the leg definition and adds a new meaning of "block". Replace: "Each leg: 4 × EPC2361 per switch, one 2EDF7275K per two branches (2 drivers per leg)."
82. [G] Bullet (step 4): "above 4 the gain is below 2.2 W" — 4 → 5 saves exactly 2.2 W (18.0 → 15.8 W). Replace: "a fifth device saves only 2.2 W, and every pair needs another driver channel."
83. [O] Step 5 card "per leg; 2.85 % ripple at / 50 kHz" ("50 kHz" alone) and step 2 card "lowest √(R·C_oss); 75 V / per cell". Replace step 5: "per leg; 2.85 % ripple" (50 kHz is in the bullet below); step 2: "lowest √(R·C_oss), 75 V cells".

### Slide 21 (devices per switch)
84. [C] Readouts (JS npar()): "99.7 %" and "69 °C" for n = 4, while slides 5, 19, 20, 22 say 99.71 % and 68.8 °C. Format efficiency with 2 decimals and T_j with 1 decimal.
85. [U] Paragraph, last sentence "More devices add switching and C_oss loss and gain little, and every pair needs another driver channel." repeats slide 20. Delete.
86. Layout: pill "✗ >150 °C" (n = 1) overflows its box. Shorten to "✗ >150" or widen the pill.

### Slide 22 (prototype)
87. [C] Title "From one branch to a four-parallel leg board": the earlier layout (left image) is "2 × EPC2361 per switch … mirrored branches", i.e. two branches. Replace: "From a two-branch block to a four-branch leg board".
88. [O] Readout 1: "loop per branch, DPT board (with / shunt)" ("shunt)" alone). Replace: "loop per branch, DPT (with shunt)".
89. Image gate_star.png: plot title cut at the right edge ("… driver U1 at the bottom) - g"). Re-export without the title (the caption says "Gate star").

### Slide 23 (voltage margin)
90. [C] Slider default di/dt = 30 A/ns, but bullet 2 quotes 36 A/ns for the chosen 3.5 Ω. Set the default to 36 A/ns so the plotted point matches the text.
91. [G] Bullet 2 ends with a fragment: "…, 37–42 A/ns at turn-off; trend with R_g." Replace: "…, 37–42 A/ns at turn-off; di/dt falls as R_g rises."
92. [O] Readout 3: "max di/dt to the 100 V / rating" ("rating" alone). Replace label: "max di/dt for 100 V".

### Slide 24 (KiCad)
93. [C] Readout "4 branches": "the branches in parallel form the 4 × EPC2361 switch". By the deck's own definitions, four branches in parallel form one leg (two switches). Replace: "one EPC2361 high side + one low side each; four in parallel form one leg (4 × EPC2361 per switch)".
94. [C] Eyebrow "Backup · Our model · 1 / 3 · KiCad": a numbering inside the text, and slide 25's eyebrow is not "2 / 3". Replace: "Backup · Our design · KiCad".
95. [C] Bullet "Supply islands: … one per high side and low side per block": "block" undefined here. Replace "per block" with "per driver".
96. [U] Bullet 4 "Two boards share the branch layout: … (0.65 nH per branch) … (0.41 nH per branch)." is stated on slides 5, 6, 13, 22, 25. Delete.
97. [U] Tiny note "Version 1 double-pulse board: 89.5 × 85.2 mm, 4 layers." repeats slide 22. Shorten to "KiCad exports of the version 1 layout (one AC bolt)."

### Slide 25 (loop budget)
98. [C] Title "0.46 copper + 0.06 ESL + 0.12 shunt = 0.65 nH per branch": the parts add to 0.64 nH. Same sum on slide 5 (Branch 1 hot spot) and slide 6 (caption). Write "≈ 0.65 nH" or give parts that add up (e.g. 0.47 + 0.06 + 0.12 if that is the correct rounding of the Q3D parts).
99. [C] Bullet 1: "The shunt (0.12 nH) and the longer copper to it (about 0.11 nH) add 0.24 nH per branch": 0.12 + 0.11 = 0.23. Replace: "add about 0.24 nH per branch (0.65 vs 0.41 nH)" or "(about 0.12 nH)" for the copper.
100. [U] Caption under the Q3D image repeats the colour legend inside the image ("DC+ (red), DC− (blue), switch node (orange) …"). Replace: "Q3D model of the four-branch DPT board copper."
101. [C] Eyebrow "Backup · our design · loop budget": lower-case "our" while slide 5 has "Our design". Replace: "Backup · Our design · Loop budget".

### Slide 26 (sharing sensitivity)
102. [G] Bullet 1: "its effect falls with 1/R_G²". Replace: "its effect falls as 1/R_G²".

### Slide 27 (one AC bolt)
103. [O] Readouts (JS bolts()): "current split between / branches" and "AC path outer / inner / branch" (single word alone). Replace labels: "turn-on current split" and "AC path, outer / inner".
104. [C] Tiny note: "assumed equal 20 nH take-off per branch" while slide 7 says "every branch has an equal 1 nH AC take-off". Same phrase, different values. Add the reason in one of them, e.g. slide 7: "an ideal equal 1 nH AC take-off".

### Slide 28 (switching frequency)
105. [C] Readout and caption "18.1 W" per leg at 50 kHz; slides 5, 19, 20, 21 say 18.0 W. Use 18.0 W (adjust the linear fit 11.9 + 0.125·f to pass through 18.0).
106. [O] Readout 3: "current ripple vs / 20 kHz" ("20 kHz" alone). Replace label: "ripple vs 20 kHz".

### Slide 29 (roadmap)
107. [G] Title: "Each step is tested before the next board, and where Infineon parts could enter" — the halves are not parallel. Replace: "Each step is tested before the next board; Infineon parts can enter at each step".
108. [O] Readout "Sensing": "(today: shunt and a Hall-effect sensor / IC)" ("IC)" alone). Replace: "coreless current sensor per branch (today: shunt and Hall-effect IC)".
109. [O] Bullet 1: "high-side gate– / Kelvin coupling" breaks at the en dash. Replace: "Kelvin coupling of the high-side gate".
110. [C] Roadmap detail, stage 2 (ROAD[1], on click): "to remove the ±15 % turn-on split between the outer branches". The split is between outer and inner branches. Replace: "… split between outer and inner branches."

### Whole deck
111. [G] British/American mix: "centre" (slides 20, 22, 27) is British, "toward" (slides 8, 10) and "paralleling/paralleled" are American. Pick British: "towards", "parallelling" (or keep American and change "centre" to "center"). Low priority.
112. [C] "Block" has five meanings: the building block (title, slide 20 "One building block"), half of the board around one driver (slide 24 "per block", gate_star image "DPT board block 1"), the earlier two-branch layout (slide 22 "Earlier block layout"), the "2 parallel (block model)" toggle (slide 10), and "two 150 kW blocks per leg" (slide 20). Keep "building block" for the concept and "earlier layout" / "driver half" elsewhere (see 41, 81, 95).

## Count of findings per category

- Unnecessary text (U): 15
- Grammar, spelling, wording (G): 12
- Orphans and split numbers/units (O): 36
- Inconsistencies, contradictions, convention breaks (C): 45
- Layout / image defects without a text category: 4 (#51, #75, #86, #89)
- Total: 112
