"""Generate the requested LaTeX engineering report and BOM appendix."""
from pathlib import Path
import json,collections,subprocess
root=Path(__file__).resolve().parents[1]
out=root/'reports';out.mkdir(exist_ok=True)
(root/'output/pdf').mkdir(parents=True,exist_ok=True)
parts=json.loads((root/'hardware/epc2361-prototype-p6/BOM.json').read_text())
def esc(s):
    for a,b in [('&',r'\&'),('_',r'\_'),('%',r'\%'),('#',r'\#')]:s=str(s).replace(a,b)
    return s
groups=collections.defaultdict(list)
for ref,c in parts.items():groups[(c['mpn'],c['value'])].append(ref)
bom='\n'.join(esc(', '.join(refs))+f' & {len(refs)} & '+esc(mpn)+' & '+esc(value)+r' \\ \hline' for (mpn,value),refs in groups.items())
tex=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=18mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,graphicx,longtable,array,xcolor,tikz,pdfpages,hyperref}
\usetikzlibrary{arrows.meta,positioning}
\hypersetup{colorlinks=true,urlcolor=blue,linkcolor=blue}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\newcommand{\uF}{\ensuremath{\mu\mathrm{F}}}
\begin{document}
{\Huge EPC2361 half-bridge}\par
{\Large P6 instrumented prototype / design and fabrication review}\par
22 September 2026\hfill Revision P6

\textbf{Release status: engineering review, not approved for fabrication.}
This report records the implemented electrical revision and the cooling candidate. A clean geometry check does not establish current capability, switching stability, sensor fit or assembly yield. The release table at the end identifies the remaining evidence needed; no manufactured or energized board has been tested.

\section*{1. Requirements and circuit}
Two EPC2361 devices in parallel per switch, four devices total. DC bus: 75 V nominal and maximum. Prototype output: 36.7 A RMS and 51.9 A peak. Nominal switching frequency: 50 kHz; maximum: 100 kHz. One half-bridge output, AC. Separate auxiliary routing with a shared DC-minus reference; no galvanic isolation. Four copper layers. External liquid cooling is preferred but its operating conditions are not yet defined.

\begin{center}
\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,every node/.style={font=\small}]
\draw[thick] (0,5)--(9,5) node[right]{DC+};
\draw[thick] (0,0)--(9,0) node[right]{DC-};
\draw[thick] (3,5)--(3,4.5) (7,5)--(7,4.5);
\node[draw,minimum width=2cm,minimum height=.8cm] (h1) at(3,4.1){QH1 EPC2361};
\node[draw,minimum width=2cm,minimum height=.8cm] (h2) at(7,4.1){QH2 EPC2361};
\draw[thick] (3,3.7)--(3,3)--(9,3) node[right]{AC};
\draw[thick] (7,3.7)--(7,3);
\node[draw,fill=orange!15,minimum width=1.9cm] at(3,2.45){LK1 + coil};
\draw[thick] (3,3)--(3,2.7) (3,2.2)--(3,1.9);
\node[draw,minimum width=2cm,minimum height=.8cm] at(3,1.5){QL1 EPC2361};
\node[draw,minimum width=2cm,minimum height=.8cm] at(7,1.5){QL2 EPC2361};
\draw[thick] (7,3)--(7,1.9) (7,1.1)--(7,0) (3,1.1)--(3,0);
\draw[thick] (0,5)--(0,2.65) (-.3,2.65)--(.3,2.65) (-.3,2.4)--(.3,2.4) (0,2.4)--(0,0);
\node[left,align=right] at(-.3,2.5){Local\ MLCCs};
\node[right] at(3.2,2.02){D\_QL1 / TP8};
\node[align=left] at(6.7,.55){Sources share DC-};
\end{tikzpicture}
\end{center}
The simplified diagram omits driver details shown in the appended native schematic. LK1 is the only intended connection from AC to QL1's drain island. TP8 senses the transistor side of LK1, so its voltage excludes the link drop. The instrumented branch is intentionally different from the compact P5 power path.

\section*{2. Driver and component selection}
LMG1210RVRR remains the baseline: one half-bridge driver with a regulated 5 V gate supply from auxiliary 12 V. Its 200 V class high-side architecture provides more voltage margin than the reference board's uP1966E. The latter specifies 85 V absolute BOOT-to-ground maximum; approximately 75+5=80 V before overshoot leaves little margin. [1,2]

Independent HI/LI mode requires externally enforced nonoverlap. Both-high is not prevented by this mode. Hold both inputs low during startup and provide bootstrap charging/refresh. Four individual gate-resistor footprints allow damping and branch isolation; 0 ohm is an initial BOM value, not a demonstrated stable setting. External gate drivers must not be connected while onboard outputs remain connected.
\newpage
\section*{3. Supply, capacitance and loss screening}
Using the local EPC2361 datasheet maximum gate charge of 34 nC, each output drives 68 nC. At 100 kHz, average gate-charge current is 6.8 mA per bank. Four-device gate energy is
\[P_G=4Q_G V_G f=4(34\,\mathrm{nC})(5\,\mathrm{V})(100\,\mathrm{kHz})=68\,\mathrm{mW}.\]
This excludes regulator and quiescent loss. The gate-charge-only 12 V to 5 V regulator loss is approximately 95 mW. Dividing total charge by peak driver current gives only a screening time; it does not predict the Miller transition or VDS rise time.

Bootstrap sizing uses effective capacitance:
\[ C_{BOOT}\geq\frac{Q_{G,bank}+Q_{driver}+Q_{rr}+I_{HB}t_{on}}{\Delta V}. \]
For 68 nC, 0.7 nC, zero assumed diode recovery charge, 0.85 mA, 20 microseconds and 0.2 V droop, the result is 0.429 \uF. Actual diode recovery and leakage increase the requirement. The nominal 1 \uF\ bootstrap candidate requires bias/temperature verification; the effective VDD reservoir must also satisfy TI's ratio requirement. [1]

The baseline bus bank has 24 TDK C2012X7S2A105K125AB, 1 \uF/100 V, all on the top face in upper and lower rows. Nominal total 24 \uF\ is not effective capacitance at 75 V. Manufacturer DC-bias, temperature, tolerance and ripple data must be used before acceptance. The EPC90135 reference instead distributes seven 220 nF/100 V/0603 parts per cell and uses an additional 0805 reservoir. Both approaches require short mounting paths; package size alone does not establish mounted ESL. [3]

Support parts include a 1 \uF/35 V VIN bypass, two 10 \uF/25 V VDD reservoirs, 100 nF bypasses, BAS21H bootstrap diode and 2.2 ohm bootstrap resistor. The selected X5R VDD capacitors are limited to 85 degrees C. The bootstrap diode is not an absolute gate-voltage clamp. Verify HB-HS and actual device VGS during low-energy testing.

\section*{4. Stackup and inductance}
Proposed copper/dielectric construction: F.Cu 70 micrometres, 0.100 mm dielectric, L2 35 micrometres, 1.190 mm core, L3 35 micrometres, 0.100 mm dielectric, B.Cu 70 micrometres; nominal total 1.6 mm. Supplier acceptance and tolerances remain required.

F.Cu contains local power connections and device escapes. L2 is the nearby DC-minus return. L3 contains DC-plus collection and separately cleared 12 V/5 V auxiliary regions, plus source-return routing. B.Cu contains gate routing and AC collection. Same-net parallel source paths remain; these are not isolated Kelvin terminals.

For a broad conductor over a nearby return, a first-order estimate is
\[L\,[\mathrm{nH}]\simeq1.2566\,h\,[\mathrm{mm}]\,\ell\,[\mathrm{mm}]/w\,[\mathrm{mm}].\]
The model includes cancellation between forward and return currents. It excludes end effects, vias, device internals, crowding and mutual coupling. The earlier P5 selected external-comb subtotal was approximately 0.385 nH; adding ideal six-way component ESL of 0.480/6=0.080 nH gives 0.465 nH for those selected terms only. \textbf{Neither is a complete P5 loop result, and neither is a P6 loop estimate.}

LK1 adds a raised conductor and altered spreading. A provisional 12 mm developed copper length, 2 mm width and 0.5 mm thickness gives approximately 0.206 milliohm at room temperature, excluding solder. At 25.95 A its I-squared-R loss is approximately 0.139 W. This calculation does not qualify pulse heating or current sharing. Full P6 loop inductance requires field extraction or a suitably controlled measurement.
\newpage
\section*{5. Device-current and voltage measurement}
QL1 drain pads 3/5/7 and TP8 use D\_QL1. LK1 joins that island to AC; QL1 source pads 2/4/6 retain DC-minus. This avoids the bypass that would arise if a source-sensing bridge were added while both low-side devices remained connected through one shared driver return. The compact and instrumented branches will not have identical switching impedance.

The selected family is PEM CWT Ultra Mini (CWTUM), with 80 mm coil circumference, typically 1.6 mm cross-section and 10 mm minimum bend radius. A circular centreline has radius 12.73 mm. The mechanical concept places it upright across the y=35 mm plane around the raised link. Including cable thickness, an outer bottom at z=1 mm gives an outer top near z=28.06 mm. The link is off-centre within this coil, requiring position-error allowance. This is distinct from the forked 55 mm CWTUMHF-F reviewed earlier. [4]

The design must clear the coil's closure and cable exit, not just the 1.6 mm winding. A CAD envelope is a fit check, not proof of safe bending or installation. The existing H1/H2 holes remain provisional output-current access; they do not measure transistor current. The CWTUM's nominal 30 MHz bandwidth corresponds to approximately 11.7 ns first-order response. It is useful for current ramps and sharing, but cannot establish accurate switching energy for substantially faster edges without a bandwidth/error assessment and deskew. [4]

\begin{center}\begin{tabular}{lll}\hline
Device & Drain contact & Source contact\\\hline
QH1 & TP6 (DC+) & TP7 (AC)\\
QL1 & TP8 (D\_QL1) & TP9 (DC-)\\
QH2 & TP10 (DC+) & TP11 (AC)\\
QL2 & TP12 (AC) & TP13 (DC-)\\\hline
\end{tabular}\end{center}
These are adjacent 1.5 mm-pitch spring-tip contacts, with short routed taps around the package pads. The exact accessory must match their pitch and insulation spacing. Use a suitably rated differential or isolated probe for high-side VDS; AC is not an earth-ground reference. Probe access must remain available with cooling fitted.

\section*{6. Double-pulse test arrangement}
For low-side turn-on/off testing, connect an external inductor from DC+ to AC, keep the high-side gates commanded off and pulse the low-side bank. First-pulse current is approximately $I=V_{DC}t_1/L$ before saturation and loss corrections. During the off interval, current freewheels through the high-side devices' reverse conduction. GaN reverse conduction should not be described as a silicon body diode.

For illustration only, $L=100\,\mu H$, $V=75$ V and $I=51.9$ A give $t_1=69.2\,\mu s$ and stored energy $LI^2/2=0.135$ J. The actual inductor, pulse limits, bus reservoir, discharge provision and test fixture remain external selections. Begin with low bus voltage and low current, checking gate polarity, nonoverlap, bootstrap voltage and probe polarity before increasing energy. Capture individual QL1 current, QL1 VDS and both local VGS waveforms; a single measured branch does not establish balanced sharing.
\newpage
\section*{7. Cooling integration}
The EPC2361 package height is 0.60--0.70 mm before solder-stack considerations. Its exposed silicon top is source connected. Every contact to a common metallic cooler therefore needs a qualified dielectric thermal interface. The reference EPC90135 uses four supports, a spreader, insulating TIM and an additional insulating sheet near exposed circuitry. Its published BOM and tested heatsink differ; they are not interchangeable evidence of thermal performance. [3,5]

The P6 mechanical candidate uses raised split rails with individual contact bosses centred at (48,32), (48,38), (66,32) and (66,38) mm. The raised rails leave room for gate connectors and spring-tip probes. A central opening allows the upright coil to pass above the board. Four proposed 2.4 mm nonplated mounting holes are centred at (40,8), (74,8), (40,53), (74,53) mm.

Boss-bottom height of approximately 1.05 mm and nominal 0.5 mm TIM are starting dimensions. Package, solder, plate flatness, support height and TIM tolerances must be combined; adjust supports/shims from the measured assembly rather than applying uncontrolled screw pressure to the devices. The EPC reference recommends no more than 2:1 TIM compression. Insulating TIM candidate: t-Global TG-A1780, subject to dielectric and compression confirmation. [3]

The split rails require checked support stiffness and preload. They are thermal interfaces to a future cold plate, not a completed liquid cooling circuit. Coolant temperature, flow, rail-to-cold-plate contact, heat load and measured thermal resistance are unresolved. Keep the 85-degree-C driver capacitors within their rating. A 3D clearance model does not establish junction temperature or mechanical reliability.

\section*{8. Fabrication and assembly release gates}
\begin{longtable}{p{.31\linewidth}p{.63\linewidth}}\hline
Item & Status and acceptance evidence\\\hline
Electrical geometry & Final merged P6: zero DRC violations, zero unconnected pads, 223 connected schematic pin assignments checked. Gate centreline differences are 0.02 mm per pair; this is not equal impedance proof. Final manufacturing artwork inspection remains required.\\
Sensing link & Formed-link drawing, solder process, selected CWTUM model/closure clearance, no copper bypass, and assembly inspection.\\
Stackup/process & Supplier-approved 0.100 mm outer dielectric spacing, 2 oz fine-pitch etching capability, drill tolerance and ENIG/stencil process.\\
Cooling & TIM compression and dielectric qualification; rail supports, probe fit and cold-plate interface approval.\\
Power connector & Correct mating receptacle, contact derating, assembly temperature rise and current distribution.\\
Passives & Effective bus/bootstrap capacitance, ripple loss and temperature qualification.\\
Schematic review & Exported-net comparison is available; custom symbols use passive pin types, so automated ERC alone cannot validate driver logic or pin function.\\
Performance & DPT, ringing/overshoot, dynamic sharing and thermal testing. These are first-article validation, not simulated results.\\\hline
\end{longtable}
Gerber and drill files have been generated in the fabrication-review directory. They are review-only until the dimensional/process items above are closed. No supplier has been contacted and no order has been submitted. Open the KiCad PCB and select View / 3D Viewer (Alt+3) to inspect the model. Several component models are approximate envelopes, explicitly identified in the model coverage file.
\newpage
\section*{9. Board BOM}
Quantities are per board. The accompanying machine-readable BOM includes footprints, nets and notes. Mechanical supports, TIM, rails, coil and mating connectors require their separate assembly specification. PCB test pads and holes are not purchased components.
\small
\begin{longtable}{p{.30\linewidth}r p{.31\linewidth}p{.23\linewidth}}\hline
References & Qty & Part / MPN & Value\\\hline\endhead
__BOM__
\end{longtable}
\normalsize
\section*{Sources and supporting files}
[1] \href{https://www.ti.com/lit/ds/symlink/lmg1210.pdf}{TI LMG1210 datasheet}; local driver review.

[2] \href{https://epc-co.com/epc/Portals/0/epc/documents/datasheets/uP1966E_datasheet.pdf}{uPI uP1966E datasheet}, absolute ratings and layout guidance.

[3] User-provided EPC90135 quick-start guide, schematic, BOM and Gerbers; detailed findings in docs/epc90135-reference-review.md. Eight-layer reference; do not assume its stackup applies to this four-layer design.

[4] \href{https://www.pemuk.com/products/cwt-range/cwt-ultra-mini}{PEM CWT Ultra Mini} and \href{https://www.pemuk.com/technical-resources/cwtum-dimensions}{CWTUM dimensions}, accessed 22 September 2026.

[5] User-provided EPC2361 datasheet revision 2.4, package dimensions and exposed-die guidance.

Local calculations: docs/inductance-prototype-p2.md (partial model only); docs/dpt-measurement-review.md; docs/p6-device-current-plan.md. Refer to current board validation files for actual pass/fail results.
\clearpage
\includepdf[pages=-,landscape=true,pagecommand={\thispagestyle{plain}}]{figures/schematic.pdf}
\end{document}
'''.replace('__BOM__',bom)
(out/'epc2361-p6-report.tex').write_text(tex)
for _ in range(2):
    subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',str(root/'output/pdf'),str(out/'epc2361-p6-report.tex')],cwd=out,check=True,stdout=subprocess.DEVNULL)
print('LaTeX report compiled')
