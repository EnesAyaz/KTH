from pathlib import Path
import json,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from extract_switching_rates import extract,ROOT
FIG=ROOT/'figures';OUT=ROOT/'output/pdf'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'savefig.dpi':180})
def save(fig,name):
 for ext in ('pdf','png'):fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight')
 plt.close(fig)
def main():
 rr=extract();FIG.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 fig,axes=plt.subplots(2,2,figsize=(10,5.5),layout='constrained')
 for ax,event,key,title,unit in zip(axes.flat,['on2','off1','on2','off1'],['voltage','voltage','current','current'],['Turn-on voltage fall','First turn-off voltage rise','Turn-on terminal-current rise','First turn-off terminal-current fall'],['V/ns','V/ns','A/ns','A/ns']):
  for l,color in [(1,'#0072B2'),(3,'#D55E00'),(5,'#009E73')]:
   items=[r for r in rr if r['L_nH']==l]
   ax.plot([r['target_A'] for r in items],[abs(r['events'][event][key]['slope_per_ns']) for r in items],'o-',label=f'{l} nH',color=color)
  ax.set(title=title,xlabel='Nominal current (A)',ylabel='10-90% magnitude ('+unit+')',xticks=[15,30,45]);ax.legend(fontsize=8)
 save(fig,'switching_rate_comparison')
 example=next(r for r in rr if r['L_nH']==3 and r['target_A']==45);w=np.load(ROOT/'runs'/example['run']/'waveforms.npz')
 fig,axes=plt.subplots(1,2,figsize=(10,3.0),layout='constrained')
 for ax,event,title in zip(axes,('on2','off1'),('Second turn-on','First turn-off')):
  e=example['events'][event];t=(w['time']-e['edge_s'])*1e9;mask=(t>=-3)&(t<=35)
  for key,signal,ref,color,label in [('voltage','vds',75,'#0072B2','Vds / 75 V'),('current','current',e['Iref_A'],'#D55E00','Id / Iload(edge)')]:
   ax.plot(t[mask],w[signal][mask]/ref,color=color,label=label)
   z=e[key];ax.plot([(z['start_s']-e['edge_s'])*1e9,(z['end_s']-e['edge_s'])*1e9],[z['start_level']/ref,z['end_level']/ref],'o--',color=color,lw=1.8)
  ax.set(title=title,xlabel='Time from command edge (ns)',ylabel='Normalized amplitude');ax.legend(fontsize=8)
 save(fig,'switching_rate_windows')
 fig,ax=plt.subplots(figsize=(9.5,1.8),layout='constrained');ax.plot([.5,1,1.5,2],[109.23870625347698,107.66146068603109,102.33494822036957,96.20909508243918],'o-',color='#0072B2');ax.axhline(100,ls='--',color='#c44426');ax.set(xlabel='External Rg,off (ohm); Rg,on fixed at 0.5 ohm',ylabel='DUT peak Vds (V)',title='3 nH / 45 A: nominal-step evidence for the selected turn-off resistance',xticks=[.5,1,1.5,2]);save(fig,'roff_voltage_evidence')
 rows=[];extra=[]
 for r in rr:
  on=r['events']['on2'];off=r['events']['off1'];off2=r['events']['off2']
  vals=[on['voltage']['slope_per_ns'],on['current']['slope_per_ns'],off['voltage']['slope_per_ns'],off['current']['slope_per_ns']]
  rows.append(f"{r['L_nH']} & {r['target_A']} & {r['Ron']:g}/{r['Roff']:g} & "+' & '.join(f'{v:.2f}' for v in vals)+r' \\')
  extra.append(f"{r['L_nH']} & {r['target_A']} & {on['Iref_A']:.2f}/{off['Iref_A']:.2f}/{off2['Iref_A']:.2f} & {off2['voltage']['slope_per_ns']:.2f} & {off2['current']['slope_per_ns']:.2f}"+r' \\')
 tex=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=15mm]{geometry}\usepackage{graphicx,booktabs,amsmath,xcolor,fancyhdr,hyperref}
\definecolor{navy}{HTML}{173B51}\hypersetup{colorlinks=true,urlcolor=navy}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small EPC2361 | Selected-case switching rates}\fancyhead[R]{\small 75 V / +5,-4 V}\fancyfoot[L]{\small Saved LTspice waveforms | 0.125 ns maximum timestep}\fancyfoot[R]{\thepage}
\setlength{\headheight}{14pt}\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\newcommand{\fig}[2]{\begin{center}\includegraphics[width=\linewidth,height=#2,keepaspectratio]{#1}\end{center}}
\begin{document}
{\LARGE\bfseries\color{navy} Switching rates of selected DPT cases}\par
\textbf{Signed average slopes; DUT terminal voltage and current.}\hfill 17 September 2026

\begin{center}\begin{tabular}{rrrrrrr}\toprule
$L$ & Setpoint & External $R_{on}/R_{off}$ & \multicolumn{2}{c}{Second turn-on} & \multicolumn{2}{c}{First turn-off}\\
(nH) & (A) & ($\Omega$) & $dv/dt$ & $di/dt$ & $dv/dt$ & $di/dt$\\
 & & & (V/ns) & (A/ns) & (V/ns) & (A/ns)\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}\end{center}
\textbf{Second turn-off and actual current references}
\begin{center}\begin{tabular}{rrrrr}\toprule
$L$ (nH) & Setpoint (A) & $I_{on2}/I_{off1}/I_{off2}$ (A) & $dv/dt$ (V/ns) & $di/dt$ (A/ns)\\\midrule
'''+ '\n'.join(extra)+r'''
\bottomrule\end{tabular}\end{center}
\small No selected pair exists for 5 nH / 45 A under the previous 100 V screening criterion; no slope is presented as a passing setting for that case.\normalsize

\textbf{Why can $R_{off}$ exceed $R_{on}$?} Only 3 nH / 45 A has that external-resistor ordering. Five cases have equal 0.5 $\Omega$ external resistors, but the driver adds 0.7/0.4 $\Omega$: the drive paths are approximately 1.2/0.9 $\Omega$, before internal gate resistance. The 5 nH selections also have lower $R_{off}$.

A strong pull-down helps hold the gate off against Miller current. However, current commutation and ringing in a parasitic inductance can limit turn-off speed. The search minimized $R_{on}+R_{off}$ (ties: lower $R_{on}$) subject to DUT peak voltage, not energy, switching time, or a required resistance ratio. The plot below shows the actual voltage trade-off; it does not prove a monotonic gate-resistance/slopes relationship.
\fig{../../figures/roff_voltage_evidence.pdf}{42mm}
\small Gate-drive background: EPC AN003, pp.2--3, discusses Miller turn-on, gate-loop damping and their trade-off. \href{https://epc-co.com/epc/Portals/0/epc/documents/product-training/Using_GaN_r4.pdf}{EPC: Using Enhancement Mode GaN-on-Silicon Power FETs}.\normalsize
\newpage
{\Large\bfseries\color{navy} Measured rates and extraction windows}\par
\fig{../../figures/switching_rate_comparison.pdf}{108mm}
\small Magnitudes are plotted for readability; the tables retain signs. Each point uses its own selected resistors, so these are not fixed-resistance inductance sweeps.\normalsize
\fig{../../figures/switching_rate_windows.pdf}{62mm}
\small Example: 3 nH / 45 A, external 0.5/2 $\Omega$. Dashed chords and dots mark the extracted voltage and current intervals. Early incomplete current excursions are excluded.\normalsize

\textbf{Definition:} voltage thresholds are 7.5 and 67.5 V (10--90\% of the nominal 75 V link). Current thresholds are 10--90\% of $I_{load}$ at each command edge. Rates are signed $\Delta V/\Delta t$ and $\Delta I/\Delta t$. Within 200 ns after the command, take the first completed directed transition, using the last start-threshold crossing preceding its end-threshold crossing. Linear interpolation determines crossing times.

\textbf{Interpretation:} $I_D=I(Vsense)$ includes device capacitive/displacement current. It is not internal channel current, nor necessarily the current in $L_{layout}$. These are transition averages, not peak derivatives or settled-current slopes; ringing remains visible. Rates use the saved 0.125 ns runs and have not received a separate slope-convergence study. Settings remain 75 V, 100 $^\circ$C and +5/-4 V gate rails; the original voltage-screening limitations still apply.

\small Data and crossing times: \texttt{dut\_gate\_search/switching\_rates.csv}. Reproduce: \texttt{python build\_switching\_rates\_report.py}. The GUI and original three-page report are unchanged.
\end{document}
'''
 (OUT/'DUT_Switching_Rates.tex').write_text(tex,encoding='utf-8')
 for _ in range(2):
  p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','DUT_Switching_Rates.tex'],cwd=OUT,capture_output=True,timeout=90)
  if p.returncode:raise RuntimeError(p.stdout.decode(errors='replace')[-2500:])
 print(OUT/'DUT_Switching_Rates.pdf')
if __name__=='__main__':main()
