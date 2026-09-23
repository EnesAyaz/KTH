"""Plot saved LTspice sweeps and compile the simulation datasheet with local LaTeX."""
from pathlib import Path
import csv, json, hashlib, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from datasheet_sweep import ROOT
OUT=ROOT/'output/pdf';FIG=ROOT/'figures'
CONFIGS=[('A',2,.5,1),('B',2,.5,5),('C',5,2,1),('D',5,.5,1),('E',2,2.5,1)]
COLORS=['#0072B2','#D55E00','#009E73','#CC79A7','#8A6900']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'figure.dpi':120,'savefig.dpi':190})

def savefig(fig,name):
 fig.savefig(FIG/(name+'.png'),bbox_inches='tight');fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight');plt.close(fig)

def escape(s):
 return str(s).replace('\\',r'\textbackslash{}').replace('_',r'\_').replace('%',r'\%').replace('&',r'\&').replace('#',r'\#')
def fnum(x,n=3):return f'{x:.{n}f}' if x is not None and np.isfinite(x) else '--'
def config(r):return next((i for i,(_,a,b,l) in enumerate(CONFIGS) if (r['rgon'],r['rgoff'],r['L_nH'])==(a,b,l)),None)
def main():
 OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(exist_ok=True)
 all_results=json.loads((ROOT/'results.json').read_text());assert len(all_results)==30,'Complete the 30-run sweep first.'
 rows=[r for r in all_results if r['status']=='ok'];rows.sort(key=lambda r:(config(r),r['target_A']))
 ref=next(r for r in rows if config(r)==0 and r['target_A']==50)
 w=np.load(ROOT/'runs'/ref['name']/'waveforms.npz');t=w['time'];a=float(w['A']);b=float(w['B'])
 # Full sequence: both blocking voltages, load/DUT current, both gate voltages.
 fig,ax=plt.subplots(3,1,figsize=(10.3,7),sharex=True,layout='constrained')
 ax[0].plot(t*1e6,w['vds'],label='DUT Vds',color=COLORS[0],lw=.8);ax[0].plot(t*1e6,w['vhs'],label='Upper Vds',color=COLORS[1],lw=.8)
 ax[0].axhline(100,color='k',ls=':',lw=.8);ax[0].set_ylabel('Drain-source voltage (V)');ax[0].legend(ncol=2)
 ax[1].plot(t*1e6,w['current'],label='DUT drain current',color=COLORS[0],lw=.8);ax[1].plot(t*1e6,w['load_current'],label='Load current',color=COLORS[2],lw=1.2);ax[1].set_ylabel('Current (A)');ax[1].legend(ncol=2)
 ax[2].plot(t*1e6,w['vgs'],label='DUT Vgs',color=COLORS[0],lw=.8);ax[2].plot(t*1e6,w['vgh'],label='Upper Vgs',color=COLORS[1],lw=.8);ax[2].axhline(-4,color='k',ls=':',lw=.8);ax[2].set_ylabel('Gate-source voltage (V)');ax[2].set_xlabel('Time (us)');ax[2].legend(ncol=2)
 for axis in ax:axis.set_xlim(t.min()*1e6,t.max()*1e6)
 fig.suptitle('Configuration A | nominal 50 A | 75 V DC link | +5 / -4 V drive')
 savefig(fig,'waveforms')
 # Switch edge views and explicit integration window.
 fig,axes=plt.subplots(4,2,figsize=(10.3,8.2),layout='constrained')
 for col,(edge,title) in enumerate([(a,'First turn-off (Eoff)'),(b,'Second turn-on (Eon)')]):
  mask=(t>=edge-50e-9)&(t<=edge+250e-9);x=(t[mask]-edge)*1e9
  axes[0,col].plot(x,w['vds'][mask],label='DUT',color=COLORS[0]);axes[0,col].plot(x,w['vhs'][mask],label='Upper',color=COLORS[1]);axes[0,col].set_title(title);axes[0,col].legend(fontsize=8)
  axes[1,col].plot(x,w['current'][mask],color=COLORS[0]);axes[1,col].plot(x,w['load_current'][mask],color=COLORS[2],ls='--')
  axes[2,col].plot(x,w['vgs'][mask],color=COLORS[0]);axes[2,col].plot(x,w['vgh'][mask],color=COLORS[1]);axes[2,col].axhline(-4,color='k',ls=':',lw=.7)
  tt=np.r_[edge-20e-9,t[(t>edge-20e-9)&(t<edge+250e-9)],edge+250e-9]
  pp=np.interp(tt,t,w['power']);integ=np.r_[0,np.cumsum((pp[1:]+pp[:-1])/2*np.diff(tt))]*1e6
  axes[3,col].plot((tt-edge)*1e9,integ,color=COLORS[4]);axes[3,col].set_xlabel('Time relative to command edge (ns)')
  for axis in axes[:,col]:axis.axvspan(-20,100,color='#DCE8EE',alpha=.5);axis.axvline(100,color='#657A88',ls='--',lw=.7);axis.set_xlim(-50,250)
 for axis,label in zip(axes[:,0],['Vds (V)','Current (A)','Vgs (V)','Cumulative energy (uJ)']):axis.set_ylabel(label)
 savefig(fig,'edges')
 # Energy characteristics: measured pre-event current; no-load isolated open squares.
 fig,ax=plt.subplots(2,1,figsize=(10.3,7.1),layout='constrained')
 for i,(letter,on,off,l) in enumerate(CONFIGS):
  rr=[r for r in rows if config(r)==i];loaded=[r for r in rr if r['target_A']>0]
  label=f'{letter}: Rg,on={on:g}, Rg,off={off:g} ohm, L={l:g} nH'
  for axis,ykey,xkey in [(ax[0],'Eon_uJ','Ion_A'),(ax[1],'Eoff_uJ','Ioff_A')]:
   axis.plot([r[xkey] for r in loaded],[r[ykey] for r in loaded],'-o',color=COLORS[i],label=label,ms=4)
   for r in rr:
    if r['target_A']==0:axis.plot(r[xkey],r[ykey],marker='s',mfc='white',mec=COLORS[i],ms=6)
 ax[0].set_ylabel('Eon, signed window energy (uJ)');ax[1].set_ylabel('Eoff, signed window energy (uJ)')
 for axis in ax:axis.set_xlim(-1,51);axis.set_xlabel('Measured load current immediately before event (A)');axis.axhline(0,color='grey',lw=.7)
 ax[0].legend(fontsize=8,ncol=2);fig.suptitle('Switching-window energy vs current | -20 ns to +100 ns')
 savefig(fig,'energy_current')
 # Device stress across all current settings.
 fig,ax=plt.subplots(2,1,figsize=(10.3,7),sharex=True,layout='constrained')
 for i,(letter,on,off,l) in enumerate(CONFIGS):
  rr=[r for r in rows if config(r)==i]
  for axis,key in [(ax[0],'Vds_LS_peak'),(ax[1],'Vds_HS_peak')]:axis.plot([r['target_A'] for r in rr],[r[key] for r in rr],'-o',label=letter,color=COLORS[i],ms=4)
 for axis in ax:axis.axhline(100,color='k',ls='--',lw=.8,label='100 V');axis.axhline(120,color='red',ls=':',lw=.8,label='120 V conditional');axis.set_xlim(-1,51)
 ax[0].set_ylabel('DUT maximum Vds (V)');ax[1].set_ylabel('Upper maximum Vds (V)');ax[1].set_xlabel('Nominal current setting (A)');ax[0].legend(ncol=7,fontsize=8)
 savefig(fig,'voltage_stress')
 fig,ax=plt.subplots(2,1,figsize=(10.3,6.6),sharex=True,layout='constrained')
 for i,(letter,on,off,l) in enumerate(CONFIGS):
  rr=[r for r in rows if config(r)==i]
  for axis,key in [(ax[0],'Vgs_LS_min'),(ax[1],'Vgs_HS_min')]:axis.plot([r['target_A'] for r in rr],[r[key] for r in rr],'-o',label=letter,color=COLORS[i],ms=4)
 for axis in ax:axis.axhline(-4,color='red',ls='--',lw=1);axis.set_xlim(-1,51)
 ax[0].set_ylabel('DUT minimum Vgs (V)');ax[1].set_ylabel('Upper minimum Vgs (V)');ax[1].set_xlabel('Nominal current setting (A)');ax[0].legend(ncol=5)
 savefig(fig,'gate_stress')
 # Setup schematic.
 fig,ax=plt.subplots(figsize=(10.3,4.1));ax.set(xlim=(0,10),ylim=(0,4.2));ax.axis('off')
 def wire(xs,ys):ax.plot(xs,ys,color='#30475B',lw=1.5,zorder=0)
 def box(x,y,width,height,label):ax.add_patch(Rectangle((x,y),width,height,facecolor='white',edgecolor='#187399',lw=1.5));ax.text(x+width/2,y+height/2,label,ha='center',va='center',fontsize=9)
 wire([.6,.6,9],[2,3.6,3.6]);wire([.6,.6,9],[1.5,.3,.3]);ax.add_patch(Circle((.6,1.75),.25,fill=False));ax.text(.6,1.75,'+\n-',ha='center',va='center');ax.text(.2,1,'75 V')
 box(1,3.43,1.3,.34,'Rcharge 10 ohm');wire([2.8,2.8],[3.6,.3]);box(2.2,2.5,1.2,.65,'ESR 5 mOhm\nESL 0.2 nH');box(2.35,1.2,.9,.55,'Cin\n470 uF')
 box(3.7,3.38,1.6,.44,'Llayout 1 or 5 nH');ax.text(4.5,4.02,'Rloop = 5 mOhm',ha='center',fontsize=8)
 wire([6.2,6.2],[3.6,.3]);box(5.75,2.65,.9,.45,'Upper FET');box(5.8,2.15,.8,.25,'CSI 0.1 nH');box(5.75,.95,.9,.45,'DUT');box(5.8,.5,.8,.25,'CSI 0.1 nH')
 wire([8.5,8.5,6.2],[3.6,1.9,1.9]);box(8.0,2.55,1,.55,'Load\n20 uH');ax.text(7.95,2.18,'Rload = 20 mOhm',ha='right',fontsize=8)
 ax.text(6.4,1.9,'sw',va='center');box(3.65,2.63,1.5,.5,'Upper held off\n-4 V, RgHS=0.9');wire([5.15,5.75],[2.88,2.88]);box(3.55,.9,1.6,.6,'DUT driver\n+5 / -4 V');wire([5.15,5.75],[1.2,1.2]);ax.text(4.35,.58,'Rg,on / Rg,off swept',ha='center',fontsize=8)
 ax.text(5,.04,'Driver returns: upper to sw; DUT to ground. CSI is shared with the respective gate loop.',ha='center',fontsize=8)
 savefig(fig,'setup')
 # LaTeX content with intentional page breaks for predictable layout.
 count_over100=sum(max(r['Vds_LS_peak'],r['Vds_HS_peak'])>100 for r in rows)
 count_over120=sum(max(r['Vds_LS_peak'],r['Vds_HS_peak'])>120 for r in rows)
 count_gate=sum(min(r['Vgs_LS_min'],r['Vgs_HS_min'])< -4.001 for r in rows)
 cov=json.loads((ROOT/'convergence.json').read_text()) if (ROOT/'convergence.json').exists() else {}
 tex=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=18mm]{geometry}
\usepackage{graphicx,booktabs,array,xcolor,amsmath,fancyhdr,hyperref}
\definecolor{navy}{HTML}{183D54}
\definecolor{teal}{HTML}{007F86}
\hypersetup{colorlinks=true,urlcolor=teal,linkcolor=navy}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small EPC2361 | DPT simulation study}\fancyhead[R]{\small 75 V / 0--50 A}\fancyfoot[L]{\small Simulation results -- not a manufacturer datasheet}\fancyfoot[R]{\thepage}
\setlength{\headheight}{14pt}\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}
\newcommand{\fig}[2]{\begin{center}\includegraphics[width=\linewidth,height=#2,keepaspectratio]{#1}\end{center}}
\begin{document}
{\Huge\bfseries\color{navy} EPC2361}\par
{\LARGE\color{teal} Double-pulse simulation datasheet}\par
{\large Setup, waveforms and switching-energy comparisons}\par
16 September 2026\hfill Revision 1\par
\medskip
\colorbox{navy}{\parbox{0.96\linewidth}{\color{white}\textbf{Study conditions:} 75 V DC supply, fixed 100 $^\circ$C model temperature, +5 / -4 V gate-drive rails. Five example configurations; nominal 0, 10, 20, 30, 40 and 50 A.}}
\section*{Purpose and interpretation}
This report characterizes the supplied EPC2361 SPICE model in a low-side double-pulse test (DPT). It retains the existing GUI and library. It is a reproducible simulation comparison, not measured hardware data, a guaranteed device specification, or a qualified 75 V / 50 A design.
\section*{Example configurations}
The resistances below are external gate resistors. The driver adds 0.7 $\Omega$ pull-up and 0.4 $\Omega$ pull-down resistance; the EPC library also contains its own device model.
\begin{center}\begin{tabular}{clrrr}\toprule
ID & Comparison & $R_{g,on}$ ($\Omega$) & $R_{g,off}$ ($\Omega$) & $L_{layout}$ (nH)\\\midrule
A & Reference & 2 & 0.5 & 1\\
B & Higher layout inductance & 2 & 0.5 & 5\\
C & Higher on/off resistances & 5 & 2 & 1\\
D & Isolate on-resistance change & 5 & 0.5 & 1\\
E & Isolate off-resistance change & 2 & 2.5 & 1\\\bottomrule
\end{tabular}\end{center}
\section*{Limits that affect these results}
The EPC2361 datasheet specifies 100 V continuous drain-source voltage and 120 V repetitive transient voltage only at a duty factor of at most 1\%. Gate-source limits are +6 / -4 V. Thus the requested -4 V off rail leaves no negative-undershoot margin. A SPICE model can still return numbers beyond these limits; those numbers do not establish device survival or accuracy outside the ratings [1].
'''
 tex+=f"Of {len(rows)} completed runs, {count_over100} exceed 100 V, {count_over120} exceed 120 V on at least one device, and {count_gate} cross below -4 V gate-source voltage. See the stress graphs and per-run CSV for details.\\par\n"
 tex+=r'''\section*{What is included}
A setup explanation, full switching waveforms, event zooms, signed $E_{on}$/$E_{off}$ versus measured current, both-device voltage stress, gate undershoot, numerical checks and tabulated data. Each event integral uses the explicitly specified window; it must not be substituted uncritically for datasheet loss values.
\newpage
\section*{1. DPT setup and measurement definition}
\fig{../../figures/setup.pdf}{78mm}
The load inductor connects DC+ to the switching node. The lower EPC2361 is the DUT. Its first pulse builds load current, the off interval commutates current through the upper device in reverse conduction, and the second pulse measures loaded turn-on. The upper gate stays at -4 V relative to its driver return; no synchronous upper pulse is applied.
\begin{center}\begin{tabular}{lr@{\qquad}lr}\toprule
Quantity & Setting & Quantity & Setting\\\midrule
Supply / temperature & 75 V / 100 $^\circ$C & Load inductance / DCR & 20 $\mu$H / 20 m$\Omega$\\
DC-link capacitance & 470 $\mu$F & Capacitor ESR / ESL & 5 m$\Omega$ / 0.2 nH\\
Charging resistance & 10 $\Omega$ & Layout resistance & 5 m$\Omega$\\
CSI per device & 0.1 nH & Upper off-state gate R & 0.9 $\Omega$\\
Initial delay / off gap & 1 / 1 $\mu$s & Second pulse / tail & 1 / 2 $\mu$s\\
Command rise / fall & 2 / 2 ns & Nominal maximum step & 0.5 ns\\\bottomrule
\end{tabular}\end{center}
The capacitor charges through the finite supply resistance during the DC operating-point solution. The first pulse is estimated as $T_1=I_{target}L/V_{DC}$. Parasitic drops, finite edges and reverse conduction mean that actual current differs from the nominal setting. Each graph uses the measured current immediately before its corresponding event.
\textbf{Energy definition.} $E_{off}$ is from the first turn-off; $E_{on}$ is from the second turn-on. With $t_e$ the start of the corresponding command edge:
\[E_{event}=10^6\int_{t_e-20\,\mathrm{ns}}^{t_e+100\,\mathrm{ns}}v_{DS,DUT}(t)i_{D,DUT}(t)\,dt\quad[\mu\mathrm{J}].\]
Current is positive into the DUT drain. These signed terminal-energy integrals include capacitive exchange, ringing and a small conduction contribution. No absolute-value rectification or forced monotonic fitting is used. Gate-driver energy and upper-device energy are excluded.
\textbf{Nominal 0 A.} A separate no-load companion uses a 1 MH load approximation. It is shown with isolated open-square markers. Without load current, the DUT may not recover the blocking voltage before pulse 2; this is not a zero-current 75 V hard-switching loss measurement.
\newpage
\section*{2. Full switching waveforms}
\fig{../../figures/waveforms.pdf}{183mm}
'''
 tex+=f"Reference A, nominal 50 A: measured first-turn-off current {ref['Ioff_A']:.3f} A and second-turn-on current {ref['Ion_A']:.3f} A. The upper-device waveform is its drain-to-source voltage, not its drain voltage relative to ground.\\par\n"
 tex+=r'''The negative gate rail applies to both off-state gate drivers. The upper device must remain off while the lower device is on. Adding an upper on-command at the instant of low-side turn-on would short the DC link; synchronous freewheeling is a different switching sequence and requires dead time.
\newpage
\section*{3. Switching transitions and energy accumulation}
\fig{../../figures/edges.pdf}{201mm}
Shading identifies the integration window. The cumulative-energy trace continues to +250 ns to expose any remaining oscillatory energy exchange; the reported value is sampled at +100 ns. A different endpoint can change the signed energy, even when peak voltage is nearly unchanged.
\newpage
\section*{4. Switching energy versus current}
\fig{../../figures/energy_current.pdf}{182mm}
Lines connect the 10--50 A nominal settings, plotted at actual pre-event current. Open squares near 0 A are the separate no-load companion runs. Resistance values are in ohms. The curves are raw signed-window simulation results, including runs that exceed the device ratings; they are not qualified loss specifications.
Increasing gate resistance changes transition duration as well as voltage overshoot. Increasing layout inductance changes resonant energy exchange. A smaller signed energy in a high-overshoot case does not establish improved efficiency.
\newpage
\section*{5. Drain-source voltage stress}
\fig{../../figures/voltage_stress.pdf}{185mm}
Peak values cover the entire DPT sequence, including first turn-on and the observation tail. The 120 V line is shown for context only; its datasheet duty-factor condition has not been qualified here. A curve below 100 V in this study alone does not establish worst-case voltage margin for a physical half-bridge.
The load-current targets, pulse widths and gate resistors do not define actual PCB inductance. The selected 1--5 nH values and 0.2 nH capacitor ESL are circuit assumptions that need layout extraction or measurement.
\newpage
\section*{6. Gate stress with -4 V off drive}
\fig{../../figures/gate_stress.pdf}{172mm}
The horizontal line is the negative gate-source rating, not a recommended design target. Actual Vgs includes common-source inductance and capacitive coupling; a -4 V source setting does not clamp device-terminal Vgs to -4 V. The positive peaks and all per-run limit flags are also included in the CSV.
EPC identifies 0 V as the typical off drive and notes that negative bias increases reverse drain-source voltage. The requested -4 V case is retained here as a simulation experiment, not recommended as a gate-drive design [1].
\newpage
\section*{7. Numerical checks and interpretation}
Gear integration is used consistently for the sweep, with maximum timestep 0.5 ns, relative tolerance $10^{-4}$, absolute current tolerance $10^{-9}$ A, voltage tolerance $10^{-6}$ V, and waveform compression disabled. Binary waveforms are stored in double precision. Energies are recomputed with trapezoidal integration after interpolating the exact window endpoints.
'''
 if cov.get('status')=='ok':
  tex+=r'\begin{center}\begin{tabular}{lrrr}\toprule Quantity & 0.5 ns & 0.25 ns & Change (\%)\\\midrule'+'\n'
  for key,label in [('Eon_uJ',r'$E_{on}$ ($\mu$J)'),('Eoff_uJ',r'$E_{off}$ ($\mu$J)'),('Vds_LS_peak','DUT peak (V)'),('Vds_HS_peak','Upper peak (V)')]:
   base=ref[key];fine=cov[key];change=(fine-base)/abs(base)*100 if base else 0
   tex+=f'{label} & {base:.4f} & {fine:.4f} & {change:+.2f}\\\\\n'
  tex+=r'\bottomrule\end{tabular}\end{center}'+'\n'
 else:tex+='The finer-step check did not complete; no timestep-convergence claim is made.\\par\n'
 tex+=r'\textbf{Window sensitivity at 50 A nominal, configuration A:}\par'+'\n'
 tex+=f"$E_{{on}}$: {ref['Eon_uJ']:.4f} $\\mu$J at +100 ns versus {ref['Eon_200ns_uJ']:.4f} $\\mu$J at +200 ns.\\par\n"
 tex+=f"$E_{{off}}$: {ref['Eoff_uJ']:.4f} $\\mu$J at +100 ns versus {ref['Eoff_200ns_uJ']:.4f} $\\mu$J at +200 ns.\\par\n"
 tex+=r'''Agreement in one case is not convergence of every configuration. Continuing ringing and window dependence limit how confidently these values can be interpreted as dissipated switching loss. No semiconductor failure, dynamic self-heating, load-inductor saturation, model variation or full repetitive converter operation is established by this study.
\subsection*{Relating the study to the GUI}
The existing GUI is unchanged. It can still load saved settings and run individual DPTs. This report uses a separate sweep script, with its numerical options recorded in each saved netlist and schematic. The GUI's frequency-based power estimate is $P_{sw}=(E_{on}+E_{off})f_{sw}$ after converting microjoules to joules; it is an event-energy extrapolation, not a full converter loss simulation.
For conduction, the GUI uses independently entered ON-interval RMS current, ON fractions and operating-temperature Rds(on). That estimate is distinct from these signed switching integrals and from reverse conduction during this DPT.
\subsection*{Reproduction}
Run \texttt{python datasheet\_sweep.py} followed by \texttt{python build\_datasheet.py}. Successful case results are cached; use \texttt{--force} to rerun. Each run retains its JSON settings, ASC schematic, CIR netlist, LTspice log/raw data, reduced NPZ waveform and result JSON. Summary data are in \texttt{results.csv}. SHA-256 hashes of the model and GUI are recorded in \texttt{provenance.json}.
\newpage
\section*{8. Numerical data: configurations A--C}
'''
 for i,(letter,on,off,l) in enumerate(CONFIGS):
  if i==3:tex+=r'\newpage\section*{9. Numerical data: configurations D--E}'+'\n'
  tex+=f'\\subsection*{{{letter}: $R_{{g,on}}={on:g}$ $\\Omega$, $R_{{g,off}}={off:g}$ $\\Omega$, $L_{{layout}}={l:g}$ nH}}\n'
  tex+=r'\begin{center}\small\begin{tabular}{rrrrrrr}\toprule Target & $I_{on}$ & $I_{off}$ & $E_{on}$ & $E_{off}$ & DUT peak & Upper peak\\ A & A & A & $\mu$J & $\mu$J & V & V\\\midrule'+'\n'
  for r in [r for r in rows if config(r)==i]:tex+=' & '.join([str(r['target_A'])]+[fnum(r[k]) for k in ['Ion_A','Ioff_A','Eon_uJ','Eoff_uJ','Vds_LS_peak','Vds_HS_peak']])+r'\\'+'\n'
  tex+=r'\bottomrule\end{tabular}\end{center}'+'\n'
 tex+=r'''\subsection*{Source documents}
[1] Efficient Power Conversion, \emph{EPC2361 eGaN FET datasheet}, revision July 20, 2026, pp. 1--3. \url{https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf}. Accessed September 16, 2026. The supplied library version is identified by its hash, not assumed to match this datasheet revision.

[2] Wolfspeed, \emph{Power Module SPICE Models User Guide}, PRD-07913 Rev. 2, December 2023, pp. 7--8, supplied PDF. Used for the clamped-inductive DPT arrangement and external-parasitic interpretation; no Wolfspeed SiC model was substituted.

[3] D. Levett, Z. Zheng and T. Frank, Infineon, \emph{Double Pulse Testing: The How, What and Why}, Bodo's Power Systems, April 2020, supplied PDF, pp. 1 and 4. Used for the pulse sequence and measurements of current, voltage and switching behavior.
\end{document}
'''
 (OUT/'EPC2361_DPT_Report.tex').write_text(tex,encoding='utf-8')
 for _ in range(2):
  proc=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','EPC2361_DPT_Report.tex'],cwd=OUT,capture_output=True,timeout=90)
  (OUT/'compile-output.txt').write_bytes(proc.stdout+proc.stderr)
  if proc.returncode:raise RuntimeError(proc.stdout.decode(errors='replace')[-4000:])
 print(OUT/'EPC2361_DPT_Report.pdf')
if __name__=='__main__':main()
