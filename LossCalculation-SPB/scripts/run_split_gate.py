"""Sweep independent gate source/sink resistances and build a separate report."""
from pathlib import Path
import argparse, csv, itertools, json, math, os, shutil, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_double_pulse import ROOT, prepare_model, dc_reference, simulate
from models.double_pulse import measure


def csv_write(path, rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows,c):
    pairs=[]
    for v,l,a,b in itertools.product(c['bus_voltages_v'],c['power_loop_inductances_nh'],c['rg_on_values_ohm'],c['rg_off_values_ohm']):
        group=[r for r in rows if (r['bus_v'],r['loop_nh'],r['rg_on_ohm'],r['rg_off_ohm'])==(v,l,a,b)]
        if len(group)!=len(c['target_currents_a']): raise ValueError('Incomplete current sweep')
        pairs.append(dict(bus_v=v,loop_nh=l,rg_on_ohm=a,rg_off_ohm=b,
            passes_all_target_currents=all(r['voltage_screen_pass'] for r in group),
            worst_vds_v=max(r['vds_peak_v'] for r in group),
            minimum_design_margin_v=min(r['vds_design_margin_v'] for r in group),
            worst_vgs_max_v=max(max(r['vgs_max_v'],r['freewheel_vgs_max_v']) for r in group),
            worst_vgs_min_v=min(min(r['vgs_min_v'],r['freewheel_vgs_min_v']) for r in group),
            worst_channel_energy_pair_uj=max(r['channel_energy_pair_uj'] for r in group)))
    return pairs


def audit(c,model,exe,out,p):
    runs=[]
    keys=['channel_energy_pair_uj','vds_peak_v','max_dvdt_on_over_1ns','max_didt_on_over_1ns']
    for step in [.2,.1,.05]:
        row,w,times=simulate(dict(c,max_timestep_ns=step),p,model,exe,out/f'convergence_{step}')
        runs.append(dict(timestep_ns=step,metrics=row))
    errors={k:abs(runs[0]['metrics'][k]-runs[-1]['metrics'][k])/max(abs(runs[-1]['metrics'][k]),1e-12) for k in keys}
    energies=[measure(w,dict(c,energy_window_ns=n),p,times)['channel_energy_pair_uj'] for n in [100,150,200]]
    spread=(max(energies)-min(energies))/max(abs(energies[1]),1e-12)
    equal_c=dict(c,driver_source_resistance_ohm=.5,driver_sink_resistance_ohm=.5,driver_resistance_ohm=.5,max_timestep_ns=.1)
    a,_,_=simulate(equal_c,dict(bus_v=75,target_a=40,loop_nh=.5,rg_on_ohm=4,rg_off_ohm=4),model,exe,out/'equal_split')
    b,_,_=simulate(equal_c,dict(bus_v=75,target_a=40,loop_nh=.5,rg_external_ohm=4),model,exe,out/'equal_original')
    equal={k:abs(a[k]-b[k])/max(abs(b[k]),1e-12) for k in keys}
    result=dict(point=p,timestep_runs=runs,relative_changes=errors,window_relative_spread=spread,
        equal_path_relative_changes=equal,fine_timestep_voltage_screen_pass=runs[-1]['metrics']['voltage_screen_pass'],
        numerical_checks_pass=max(errors.values())<.05 and spread<.05 and max(equal.values())<.05)
    (out/'validation.json').write_text(json.dumps(result,indent=2))
    return result


def report(out):
    saved=json.loads((out/'summary.json').read_text())
    c,pairs=saved['config'],saved['pairs']
    on,off=c['rg_on_values_ohm'],c['rg_off_values_ohm']
    figures=[]
    for v in c['bus_voltages_v']:
        fig,axes=plt.subplots(2,len(c['power_loop_inductances_nh']),figsize=(11,8),squeeze=False)
        for j,l in enumerate(c['power_loop_inductances_nh']):
            group=[p for p in pairs if p['bus_v']==v and p['loop_nh']==l]
            for i,key,label in [(0,'worst_vds_v','Worst Vds across both FETs (V)'),(1,'worst_channel_energy_pair_uj','Worst DUT excess energy pair (uJ)')]:
                values=np.array([[next(p[key] for p in group if p['rg_on_ohm']==a and p['rg_off_ohm']==b) for b in off] for a in on])
                ax=axes[i,j]
                im=ax.imshow(values,origin='lower',aspect='auto',cmap='viridis')
                fig.colorbar(im,ax=ax,label=label)
                ax.set_xticks(range(len(off)),off);ax.set_yticks(range(len(on)),on)
                ax.set_xlabel('External Rg,off (ohm)');ax.set_ylabel('External Rg,on (ohm)')
                ax.set_title(f'{v:g} V, Lbus={l:g} nH')
                for y,a in enumerate(on):
                    for x,b in enumerate(off):
                        p=next(p for p in group if p['rg_on_ohm']==a and p['rg_off_ohm']==b)
                        flag='' if p['passes_all_target_currents'] else '\nFAIL'
                        ax.text(x,y,f'{values[y,x]:.1f}{flag}',ha='center',va='center',color='white',fontsize=8,
                            bbox=dict(facecolor='black',alpha=.35,edgecolor='none',pad=1))
        fig.suptitle(f"Independent gate resistors, {c['temperature_c']} C; worst over target currents")
        fig.tight_layout()
        name=f'split_gate_{v:g}v'
        fig.savefig(out/f'{name}.pdf');fig.savefig(out/f'{name}.png',dpi=160);plt.close(fig)
        figures.append(name)
    tex=(ROOT/'reports/templates/split_gate_report.tex').read_text()
    setup='\n'.join(label+' & '+str(c[key])+r' \\' for key,label in [
        ('bus_voltages_v','Bus voltages (V)'),('target_currents_a','Target currents (A)'),
        ('rg_on_values_ohm','External Rg,on (ohm)'),('rg_off_values_ohm','External Rg,off (ohm)'),
        ('power_loop_inductances_nh','Bus loop L (nH)'),('temperature_c','Fixed temperature (C)'),
        ('driver_source_resistance_ohm','Driver source R (ohm)'),('driver_sink_resistance_ohm','Driver sink R (ohm)'),
        ('common_source_inductance_nh','Additional common-source L (nH)'),('gate_loop_inductance_nh','Gate-loop L (nH)')])
    passing=[p for p in pairs if p['passes_all_target_currents']]
    table='\n'.join(f"{p['bus_v']:g} & {p['loop_nh']:g} & {p['rg_on_ohm']:g} & {p['rg_off_ohm']:g} & {p['worst_vds_v']:.2f} & {p['worst_channel_energy_pair_uj']:.2f}"+r' \\' for p in passing)
    if not passing: table=r'\multicolumn{6}{c}{No pair passed every target current.} \\'
    check=json.loads((out/'validation.json').read_text())
    checks=(f"Audited point: {check['point']['bus_v']:g} V, target {check['point']['target_a']:g} A, "
        f"Lbus={check['point']['loop_nh']:g} nH, Rg,on={check['point']['rg_on_ohm']:g} ohm, "
        f"Rg,off={check['point']['rg_off_ohm']:g} ohm. Timestep sensitivity: at most {100*max(check['relative_changes'].values()):.2f}\\%. "
        f"Window sensitivity: {100*check['window_relative_spread']:.2f}\\%. "
        f"Equal-resistance comparison: at most {100*max(check['equal_path_relative_changes'].values()):.2f}\\%. "
        f"Numerical checks passed: {check['numerical_checks_pass']}. "
        f"Audited point passes the finest-timestep voltage screen: {check['fine_timestep_voltage_screen_pass']}.")
    plots='\n'.join(r'\clearpage\noindent\includegraphics[width=\linewidth]{../../results/split_gate/'+n+'.pdf}' for n in figures)
    for token,value in {'@SETUP@':setup,'@PASSING@':table,'@CHECKS@':checks,'@PLOTS@':plots,
        '@COUNT@':str(len(saved['points'])),'@PAIRCOUNT@':str(len(passing))}.items(): tex=tex.replace(token,value)
    dest=ROOT/'reports/generated';dest.mkdir(parents=True,exist_ok=True)
    (dest/'split_gate_report.tex').write_text(tex,encoding='utf-8')
    fallback=Path(os.environ['LOCALAPPDATA'])/'Programs/MiKTeX/miktex/bin/x64/pdflatex.exe'
    latex=os.environ.get('PDFLATEX') or shutil.which('pdflatex') or str(fallback)
    for _ in range(2): subprocess.run([latex,'-interaction=nonstopmode','-halt-on-error','split_gate_report.tex'],cwd=dest,check=True)
    print(f"Report: {dest/'split_gate_report.pdf'}",flush=True)


def main(config,smoke=False,report_only=False):
    out=ROOT/'results/split_gate'
    if report_only: report(out);return
    c=json.loads((ROOT/'data/inputs/double_pulse.json').read_text())
    c.update(json.loads(config.read_text()))
    for key in ['bus_voltages_v','target_currents_a','rg_on_values_ohm','rg_off_values_ohm','power_loop_inductances_nh']:
        if not c[key] or any(not math.isfinite(v) or v<=0 for v in c[key]): raise ValueError(f'Invalid {key}')
    for key in ['driver_source_resistance_ohm','driver_sink_resistance_ohm']:
        if not math.isfinite(c[key]) or c[key]<0: raise ValueError(f'Invalid {key}')
    if not -40<=c['temperature_c']<=150: raise ValueError('Temperature outside range')
    if c['energy_window_ns']>=min(c['freewheel_interval_ns'],c['second_pulse_ns']): raise ValueError('Window overlaps next edge')
    if c['slope_interval_ns']!=1: raise ValueError('Slope fields require a 1 ns interval')
    exe=Path(os.environ.get('LTSPICE_EXE',Path(os.environ['LOCALAPPDATA'])/'Programs/ADI/LTspice/LTspice.exe'))
    model,digest=prepare_model();out.mkdir(parents=True,exist_ok=True)
    m=dc_reference(c,model,exe,out/'dc_reference')
    if smoke:
        row,_,_=simulate(m,dict(bus_v=75,target_a=40,loop_nh=.5,rg_on_ohm=4,rg_off_ohm=1),model,exe,out/'smoke')
        print(json.dumps(row,indent=2));return
    points=[dict(zip(['bus_v','target_a','loop_nh','rg_on_ohm','rg_off_ohm'],values)) for values in
        itertools.product(c['bus_voltages_v'],c['target_currents_a'],c['power_loop_inductances_nh'],c['rg_on_values_ohm'],c['rg_off_values_ohm'])]
    rows=[]
    for i,p in enumerate(points):
        name=f"v{p['bus_v']}_i{p['target_a']}_l{p['loop_nh']}_on{p['rg_on_ohm']}_off{p['rg_off_ohm']}"
        row,_,_=simulate(m,p,model,exe,out/name);rows.append(row)
        if i%8==0 or i==len(points)-1: print(f'Split-gate DPT {i+1}/{len(points)} complete',flush=True)
    pairs=summarize(rows,c)
    csv_write(out/'switching.csv',rows);csv_write(out/'pairs.csv',pairs)
    (out/'summary.json').write_text(json.dumps(dict(config=c,model_sha256=digest,points=rows,pairs=pairs),indent=2))
    passing=[p for p in pairs if p['passes_all_target_currents']]
    selected=min(passing,key=lambda p:p['worst_channel_energy_pair_uj']) if passing else pairs[0]
    p={key:selected[key] for key in ['bus_v','loop_nh','rg_on_ohm','rg_off_ohm']}
    p['target_a']=max(c['target_currents_a'])
    check=audit(m,model,exe,out,p)
    print(json.dumps(dict(passing_pairs=len(passing),selected_for_audit=p,numerical_checks_pass=check['numerical_checks_pass']),indent=2),flush=True)
    report(out)
    if not check['numerical_checks_pass']: raise SystemExit('Numerical audit failed; inspect validation.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path,default=ROOT/'data/inputs/split_gate.json')
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--report-only',action='store_true')
    a=parser.parse_args();main(a.config,a.smoke,a.report_only)
