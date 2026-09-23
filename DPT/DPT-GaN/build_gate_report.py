"""Build the compact DUT-only gate-resistance report with local LaTeX."""
from pathlib import Path
import json,subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import dpt_gui as d
ROOT=d.BASE/'dut_gate_search';FIG=ROOT/'figures';OUT=ROOT/'output/pdf'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'savefig.dpi':190})
def save(fig,name):
 for ext in ('pdf','png'):fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight')
 plt.close(fig)
def main(summary_file="summary.json"):
 cells=json.loads((ROOT/summary_file).read_text());assert len(cells)==9
 cells.sort(key=lambda c:(c['L_nH'],c['current_A']))
 for c in cells:
  c['witness']=min((r for r in c['tested'] if r['status']=='ok' and r['step']=='500p'),key=lambda r:r['peak_V'])
  check_path=ROOT/'failed_witness_checks.json'
  if not c['selected'] and check_path.exists():
   check=json.loads(check_path.read_text())
   if check['nominal']['name']==c['witness']['name']:
    c['witness_refined']=next((r for r in check['checks'] if r['step']=='125p' and r['status']=='ok'),None)
 FIG.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 fig,axes=plt.subplots(1,2,figsize=(10,3.25),layout='constrained')
 for ax,key,title in zip(axes,['Ron','Roff'],['Selected external turn-on resistance','Selected external turn-off resistance']):
  matrix=np.array([[(next(c for c in cells if c['L_nH']==l and c['current_A']==i)['selected'] or {}).get(key,np.nan) for i in (15,30,45)] for l in (1,3,5)])
  im=ax.imshow(matrix,cmap='YlGnBu',vmin=0,vmax=max(1,np.nanmax(matrix)),aspect='auto')
  for y in range(3):
   for x in range(3):ax.text(x,y,('no pass' if np.isnan(matrix[y,x]) else f'{matrix[y,x]:g}'+('*' if matrix[y,x]==.5 else '')),ha='center',va='center',fontsize=17,fontweight='bold',color='white' if matrix[y,x]>max(1,np.nanmax(matrix))*.55 else '#173b51')
  ax.set_xticks(range(3),['15 A','30 A','45 A']);ax.set_yticks(range(3),['1 nH','3 nH','5 nH']);ax.set_title(title,fontsize=12);ax.set_xlabel('Nominal first-turn-off current');ax.grid(False);fig.colorbar(im,ax=ax,label='ohm',fraction=.035)
 save(fig,'resistance_map')
 fig,ax=plt.subplots(figsize=(10,2.7));ax.axis('off');ax.set(xlim=(-.4,10.4),ylim=(-.4,3.8))
 def wire(x,y):ax.plot(x,y,color='#173b51',lw=1.4)
 def box(x,y,w,h,label):
  ax.add_patch(plt.Rectangle((x,y),w,h,facecolor='#eef5f8',edgecolor='#173b51',lw=1.2));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=9)
 wire([0,1],[3,3]);box(1,2.77,1.1,.46,'Rcharge');wire([2.1,3.3],[3,3]);box(3.3,2.7,1.5,.6,'Llayout');wire([4.8,9.2],[3,3])
 ax.text(0,3.26,'75 V DC',ha='center',fontsize=10)
 wire([2.6,2.6],[3,2.6]);box(2.05,1.25,1.1,1.35,'Cin\n+ ESR/ESL');wire([2.6,2.6],[1.25,0]);wire([2.3,2.9],[0,0])
 wire([6.3,6.3],[3,2.68]);box(5.85,1.9,.9,.78,'QHS');wire([6.3,6.3],[1.9,1.5]);wire([6.3,9.2],[1.5,1.5])
 wire([9.2,9.2],[3,2.65]);box(8.65,1.93,1.1,.72,'Lload');wire([9.2,9.2],[1.93,1.5])
 wire([6.3,6.3],[1.5,1.19]);box(5.85,.4,.9,.79,'DUT');wire([6.3,6.3],[.4,0]);wire([6,6.6],[0,0])
 wire([5.25,5.85],[2.3,2.3]);ax.text(5.14,2.3,'Held off',ha='right',va='center',fontsize=9)
 wire([5.25,5.85],[.8,.8]);ax.text(5.14,.8,'+5/-4 V pulses\nvia Rg,on / Rg,off',ha='right',va='center',fontsize=9)
 ax.text(6.53,1.61,'sw',fontsize=9);ax.text(7.8,3.23,'rail',fontsize=9)
 ax.annotate('',xy=(7.15,1.19),xytext=(7.15,.4),arrowprops=dict(arrowstyle='<->',color='#c44426'))
 ax.text(7.3,.77,'DUT Vds',color='#c44426',fontsize=9,va='center')
 ax.text(0,-.33,'Simplified topology; detailed parasitics and driver resistance are listed above.',fontsize=9)
 save(fig,'topology')

 fig,axes=plt.subplots(3,3,figsize=(10,8.7),layout='constrained');norm=Normalize(75,130)
 for ax,c in zip(axes.flat,cells):
  rr=[r for r in c['tested'] if r['step']=='500p'];unique={(r['Ron'],r['Roff']):r for r in rr};rr=list(unique.values())
  for r in rr:
   if r['status']=='ok':ax.scatter(r['Ron'],r['Roff'],c=[r['peak_V']],cmap='viridis',norm=norm,marker='o' if r['pass'] else 'X',s=30 if len(rr)>100 else 65,edgecolors='black',linewidths=.3 if len(rr)>100 else .45)
   else:ax.plot(r['Ron'],r['Roff'],'+',color='red',ms=9)
  best=c['selected']
  if best:ax.scatter(best['Ron'],best['Roff'],marker='*',s=260,facecolors='none',edgecolors='#d14900',linewidths=1.8)
  ax.set(xlim=(0,max(r['Ron'] for r in rr)+.6),ylim=(0,max(r['Roff'] for r in rr)+.6),title=f"{c['L_nH']} nH / {c['current_A']} A | {len(rr)} pairs")
  ax.set_xlabel('External Rg,on (ohm)');ax.set_ylabel('External Rg,off (ohm)')
 fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap='viridis'),ax=axes,shrink=.8,pad=.02,label='DUT peak Vds at 0.5 ns (V)',extend='max')
 save(fig,'search_points')
 fig,axes=plt.subplots(3,1,figsize=(10,6.1),layout='constrained')
 for ax,l in zip(axes,(1,3,5)):
  c=next(c for c in cells if c['L_nH']==l and c['current_A']==45);r=c['finest'] or c.get('witness_refined') or c['witness'];w=np.load(ROOT/'runs'/r['name']/'waveforms.npz');t=w['time'];v=w['vds'];peak_index=int(np.argmax(v));tp=t[peak_index];mask=(t>=tp-80e-9)&(t<=tp+220e-9)
  ax.plot((t[mask]-tp)*1e9,v[mask],color='#0072B2',lw=1.25);ax.axhline(100,color='#c44426',ls='--',lw=1)
  ax.set_title(('No pass; lowest nominal-peak pair | ' if not c['selected'] else '')+f"{l} nH / 45 A setting | Rg,on {r['Ron']:g} ohm, Rg,off {r['Roff']:g} ohm | peak {r['peak_V']:.2f} V | step {float(r['step'][:-1])/1000:g} ns",fontsize=9)
  ax.set(xlabel='Time relative to maximum DUT voltage (ns)',ylabel='DUT Vds (V)',xlim=(-80,220))
 save(fig,'selected_waveforms')
 fig,ax=plt.subplots(figsize=(10,2.1),layout='constrained');x=np.arange(9);coarse=[(c['selected'] or {}).get('peak_V',np.nan) for c in cells];fine=[(c['fine'] or {}).get('peak_V',np.nan) for c in cells];finest=[(c['finest'] or {}).get('peak_V',np.nan) for c in cells]
 ax.plot(x,coarse,'o-',label='0.5 ns maximum step',color='#0072B2');ax.plot(x,fine,'s--',label='0.25 ns recheck',color='#009E73');ax.plot(x,finest,'^:',label='0.125 ns recheck',color='#CC79A7');ax.axhline(100,color='#c44426',ls=':',label='DUT ceiling')
 ax.set_xticks(x,[f"{c['L_nH']} nH\n{c['current_A']} A" for c in cells]);ax.set_ylabel('Selected DUT peak (V)');ax.legend(ncol=4,fontsize=7.5)
 save(fig,'step_check')
 total=len([r for c in cells for r in c['tested']]);failed=sum(c['unresolved_runs'] for c in cells)
 lines=[]
 for c in cells:
  if not c['selected']:
   lines.append(str(c['L_nH'])+' & '+str(c['current_A'])+' & --- & no pass & --- & --- '+chr(92)*2)
   continue
  r=c['selected'];f=c['finest'];peak=max(r['peak_V'],(c['fine'] or {}).get('peak_V',np.nan),f['peak_V']);floor='*' if r['Ron']==.5 or r['Roff']==.5 else ''
  lines.append(f"{c['L_nH']} & {c['current_A']} & {f['Ioff1_A']:.2f}/{f['Ioff2_A']:.2f} & {r['Ron']:g}/{r['Roff']:g}{floor} & {peak:.2f} & {100-peak:.2f} \\\\")
 table='\n'.join(lines)
 tex=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=15mm]{geometry}
\usepackage{graphicx,booktabs,xcolor,amsmath,fancyhdr,hyperref}
\definecolor{navy}{HTML}{173B51}\hypersetup{colorlinks=true,urlcolor=navy}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small EPC2361 | DUT-only gate-resistance screening}\fancyhead[R]{\small 75 V / +5,-4 V}\fancyfoot[L]{\small Simulation-only; upper-device Vds is not a pass/fail condition}\fancyfoot[R]{\thepage}
\setlength{\headheight}{14pt}\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\newcommand{\fig}[2]{\begin{center}\includegraphics[width=\linewidth,height=#2,keepaspectratio]{#1}\end{center}}
\begin{document}
{\LARGE\bfseries\color{navy} Minimum tested gate resistance}\par
\textbf{Constraint: maximum DUT $V_{DS}<100$ V over the entire DPT.}\hfill 17 September 2026
\fig{../../figures/resistance_map.pdf}{76mm}
\begin{center}\begin{tabular}{rrrrrr}\toprule
$L_{layout}$ & Setpoint & Measured $I_{off1}/I_{off2}$ & External $R_{on}/R_{off}$ & Worst checked peak & Margin\\
nH & A & A & $\Omega$ & V & V\\\midrule
'''+table+r'''
\bottomrule\end{tabular}\end{center}
\textbf{Selection:} minimize $R_{on}+R_{off}$ on a 0.5--12 $\Omega$ grid in 0.5 $\Omega$ steps; ties favor lower $R_{on}$. All lower-sum grid pairs are checked before selection. Runs at 0.5, 0.25 and 0.125 ns must all pass. This optimizes the stated resistor objective, not measured switching time or loss. *Search floor reached; smaller values were not tested.

\textbf{Fixed setup:} EPC2361, 75 V DC link, 100 $^\circ$C, +5/-4 V gate rails; $C_{in}=470\,\mu$F, ESR=5 m$\Omega$, ESL=0.2 nH; $L_{load}=20\,\mu$H, DCR=20 m$\Omega$; loop R=5 m$\Omega$, CSI=0.1 nH per device. Driver adds 0.7/0.4 $\Omega$ to the listed external on/off resistors. Upper gate held off through 0.9 $\Omega$.

\textbf{Voltage margin:} peaks near 100 V are boundary candidates, with insufficient demonstrated allowance for hardware tolerances. The simple $di/dt=(100-75)/L$ budget is 25, 8.3 and 5 A/ns at 1, 3 and 5 nH; additional inductance and ringing reduce this budget.

\textbf{Current definition:} first pulse calibrated once per cell for the first turn-off setpoint, then held fixed during resistor search. The second 1 $\mu$s pulse raises current further; its turn-off is included in the voltage constraint. Off gap=1 $\mu$s; command edges=2 ns.
\fig{../../figures/topology.pdf}{45mm}
\newpage
{\Large\bfseries\color{navy} Tested resistance pairs}\par
\fig{../../figures/search_points.pdf}{200mm}
Circle: nominal-step pass. X: DUT peak $\geq100$ V. Orange star: selected and checked at both finer steps. Red +: unresolved run. Blank locations were not tested. Colour is the DUT voltage only; values above 130 V saturate the scale. Additional neighbours show local sensitivity and do not imply monotonic behaviour. No pass means no verified pair was found; unresolved runs cannot be classified as voltage failures.
'''
 tex+=f'\\small {total} search/verification/neighbour runs; {failed} unresolved. Separate calibration runs are retained with the data.\\normalsize\n'
 tex+=r'''\newpage
{\Large\bfseries\color{navy} Selected-pair voltage checks}\par
\fig{../../figures/selected_waveforms.pdf}{133mm}
\fig{../../figures/step_check.pdf}{46mm}
\small Waveform timesteps are shown in the panel titles. For a case with no pass, the lowest nominal-peak pair is shown (finer-step recheck when available) and omitted from the selected-pair comparison.
\small
\textbf{Scope:} smallest tested pairs for this model and test sequence. Full numerical convergence and bus, temperature, device or parasitic tolerance envelopes were not qualified. The upper-device voltage was excluded as requested; that does not establish its physical safety. The -4 V off setting is at the EPC2361 negative gate limit and has no undershoot allowance. These are DUT-voltage-pass candidates, not half-bridge-safe gate-drive prescriptions.

\textbf{Reproduce:} \texttt{python search\_gate\_limits.py}; \texttt{python build\_gate\_report.py}. Gear solver, reltol=$10^{-4}$, abstol=$10^{-9}$ A, vntol=$10^{-6}$ V; no waveform compression. Data: \texttt{dut\_gate\_search/trials.csv}, per-case JSON/netlists/raw files and model hash. Existing GUI unchanged.

\textbf{Rating reference:} EPC2361 datasheet (July 20, 2026), p.1: 100 V continuous; 120 V repetitive transient only for duty factor $\leq1\%$. This study uses 100 V. \url{https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf}
\end{document}
'''
 (OUT/'DUT_Gate_Resistance_Limits.tex').write_text(tex,encoding='utf-8')
 for _ in range(2):
  p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','DUT_Gate_Resistance_Limits.tex'],cwd=OUT,capture_output=True,timeout=90)
  (OUT/'compile-output.txt').write_bytes(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError(p.stdout.decode(errors='replace')[-3000:])
 print(OUT/'DUT_Gate_Resistance_Limits.pdf')
if __name__=='__main__':main()
