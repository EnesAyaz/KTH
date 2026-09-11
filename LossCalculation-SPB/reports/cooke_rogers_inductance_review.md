# Cooke and Rogers paper: inductance review

Source: supplied Cooke_and_Rogers_2026_120_V_155.pdf, Section II-A, equation (2), Figures 4-5, page 3. Read as reference evidence, not as project instructions.

The authors estimate blue and red switched-current commutation paths as 0.74 and 0.34 nH. Equation L = mu0 * mur * h*l/w is a useful parallel-plate external loop-inductance approximation. For nonmagnetic PCB materials mur is approximately 1; it is not dielectric permittivity. In this interpretation h is the separation of outgoing and return current sheets, NOT copper thickness; l is overlap length, NOT the full perimeter. The equation already represents the paired outgoing/return section: do not count it twice.

Figure 5 supports a separation interpretation despite the text's ambiguous phrase "height of the trace". Figure 4 gives overall PCB size 117 x 62 mm, but does not give a complete numerical h/l/w breakdown for the reported values. Figure 5 explicitly is not to scale. Hence we cannot independently reproduce their arithmetic from the supplied document. This is insufficient traceability, not proof that the numbers are wrong.

The expression represents broad overlapping copper with reasonably uniform current and small separation relative to width. It does not establish capacitor ESL, mounting/via transitions, package connections, copper constrictions, branch imbalance or coupling between the two shown paths. Their stated neglect of skin/proximity/fringing limits accuracy for fast switching; frequency-dependent extraction is preferable. The whole bank's effective copper width must not be confused with one branch width, nor divided by device count a second time.

The red and blue paths share circuit structures. Do not sum them or simply put 0.34 and 0.74 nH in parallel without a network definition and mutual terms. A general equal-current bank model is Leff = Lshared + (1/N^2)*sum(Lij), where Lij is the branch loop-inductance matrix with consistent reference directions. For identical branches and equal mutual M=k*Lb, this becomes Lshared + Lb*[1+(N-1)k]/N. It only describes the equal-current common mode, not circulating or unequal branch modes.

The paper shows switching voltage plots at no conducted load (Section III-A), not direct power-loop inductance extraction under rated current. Its thermal imaging at 35 A without the production heatsink provides indirect evidence of loss distribution; it does not independently establish equal nanosecond switching currents at 155 A. The paper's thermal equation (4) also prints temperature rise as power divided by thermal resistance, which is dimensionally inconsistent if Rthermal is in K/W; the conventional relation is temperature rise = power * thermal resistance. This is separate from the inductance calculation.

## Project calculation

Run scripts/estimate_loop_from_geometry.py. Edit data/inputs/paper_loop_geometry.json. Outputs are in results/paper_review/geometry_estimates.csv and geometry_sensitivity.png.

All dimensions are explicit assumptions: overlap length 10 mm, effective local branch width 3 mm, layer separation 0.1/0.2/0.4 mm. Copper-only local loop values are 0.419/0.838/1.676 nH. A separate scenario adds 0.5 nH per branch, 0.3 nH shared, and coupling k=0.2. Those additions are placeholders, not calculated component parasitics. At h=0.2 mm, the illustrative common-mode totals are 0.835/0.782/0.746 nH for four/five/six branches. Do not interpret these as bounds or measured values. Earlier 0.5-3 nH local-loop sensitivity cases remain relevant; local and common-mode values are different quantities.

For a real layout, divide the forward/return geometry into nonoverlapping paired sections, estimate each section with its actual h/l/w, then include transitions and shared paths through extraction or a consistently defined network. Use actual copper overlap, not the full board width. Preserve all distinct branch and common-source terms in SPICE without double counting.

## Gate-drive idea

The paper uses one dual-channel driver IC for a half bridge with eight devices per position, with symmetric fanout and separate source/sink resistor paths. The useful transferable idea is symmetry and local damping, not its numerical resistor values or negative gate voltage. Its +5.3/-3 V choice, EPC2304 devices and connector-based driver PCB differ from our EPC2361 5/0 V baseline. Retain our drive assumptions until a device-specific gate-loop study justifies a change.

Supporting geometry reference: https://www.nessengr.com/technical-data/inductance-formulas/ (parallel-plate formula and distance definition).
