"""Run the supplied EPC2361 model in LTspice, retaining netlists and waveforms."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import csv
import os
import subprocess
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from models.double_pulse import read_raw, measure
from models.gate_drive import gate_path


def prepare_model():
    source = ROOT/'data/spice/EPC2361.lib'
    text = source.read_text()
    text = text.replace('.subckt EPC2361 gatein drainin sourcein', '.subckt EPC2361_MON gatein drainin sourcein heat')
    # Observation only; no feedback into any electrical node. Excludes gate-drive loss.
    text = text.replace('.ends', 'Bheat heat 0 V=V(drain,source)*I(bswitch)+V(drainin,drain)*I(rd)+V(sourcein,source)*I(rs)\nRmonitor heat 0 1G\n.ends')
    model = ROOT/'data/spice/EPC2361_monitored.lib'
    model.write_text(text, encoding='ascii')
    return model, hashlib.sha256(source.read_bytes()).hexdigest()


def netlist(c, p, model):
    start = c['pulse_start_ns']*1e-9
    rise = c['driver_edge_ns']*1e-9
    off = start+c['load_inductance_uh']*1e-6*p['target_a']/p['bus_v']
    on = off+c['freewheel_interval_ns']*1e-9
    off2 = on+c['second_pulse_ns']*1e-9
    end = off2+200e-9
    points = [(0,0),(start,0),(start+rise,5),(off,5),(off+rise,0),
              (on,0),(on+rise,5),(off2,5),(off2+rise,0)]
    pulse = ' '.join(f'{t:.12g} {v}' for t,v in points)
    deck = f'''EPC2361 DPT: single device, fixed temperature, assumed parasitics
.include "{model.as_posix()}"
Vbus dc 0 {p['bus_v']}
Lloop dc lp {p['loop_nh']}n Rser=1m
Rloop lp top {c['power_loop_resistance_ohm']}
Lload dc sw {c['load_inductance_uh']}u Rser=1m
Xfree gh top sw pfree EPC2361_MON
Roff gh sw {c['freewheel_gate_resistance_ohm']}
Vsense sw d 0
Xdut g d s pdut EPC2361_MON
Lsource s 0 {c['common_source_inductance_nh']}n Rser=0.1m
Vdrive drive 0 PWL({pulse})
{gate_path(c, p)}
Lg gx g {c['gate_loop_inductance_nh']}n Rser=10m
.temp {c['temperature_c']}
.options plotwinsize=0 numdgt=15 reltol=1e-4
.save V(d) V(s) V(g) V(gh) V(top) V(sw) I(Vsense) I(Lload) V(pdut) V(pfree)
.tran 0 {end:.12g} 0 {c['max_timestep_ns']}n
.end
'''
    return deck, dict(on2=on, off1=off)


def simulate(c, p, model, exe, out):
    out.mkdir(parents=True, exist_ok=True)
    deck, times = netlist(c,p,model)
    path = out/'test.cir'
    path.write_text(deck,encoding='ascii')
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    subprocess.run([str(exe), '-b', '-ascii', str(path)], cwd=out, check=True,
                   timeout=120, startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
    w = read_raw(path.with_suffix('.raw'))
    return measure(w,c,p,times), w, times


def dc_reference(c, model, exe, out):
    """Obtain on-state drop at 5 V from the same model and temperature."""
    out.mkdir(parents=True,exist_ok=True)
    path=out/'dc_reference.cir'
    maximum=max(c['target_currents_a'])+50
    path.write_text(f'''EPC2361 5 V DC reference for conduction subtraction
.include "{model.as_posix()}"
Vgate g 0 5
Itest 0 d 0
Xdut g d 0 heat EPC2361_MON
.temp {c['temperature_c']}
.save V(d)
.dc Itest 0 {maximum} 0.5
.options numdgt=15
.end
''',encoding='ascii')
    startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    subprocess.run([str(exe),'-b','-ascii',str(path)],cwd=out,check=True,timeout=120,
                   startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
    data=read_raw(path.with_suffix('.raw'))
    axis=next(iter(data))
    return dict(c,_dc_current_a=data[axis].tolist(),_dc_voltage_v=data['v(d)'].tolist())


def main(config, nominal_only=False):
    c = json.loads(config.read_text(encoding='utf-8'))
    for key in ['bus_voltages_v','target_currents_a','external_gate_resistances_ohm','power_loop_inductances_nh']:
        if not c[key] or any(v <= 0 for v in c[key]):
            raise ValueError(f'{key} requires positive values')
    if c['energy_window_ns'] >= min(c['freewheel_interval_ns'],c['second_pulse_ns']):
        raise ValueError('Energy windows must fit between edges')
    exe = Path(os.environ.get('LTSPICE_EXE', Path(os.environ['LOCALAPPDATA'])/'Programs/ADI/LTspice/LTspice.exe'))
    if not exe.is_file():
        raise SystemExit('Set LTSPICE_EXE to the installed LTspice executable')
    model, digest = prepare_model()
    out = ROOT/'results/double_pulse'
    out.mkdir(parents=True,exist_ok=True)
    measurement_config=dc_reference(c,model,exe,out/'dc_reference')
    points = [dict(zip(['bus_v','target_a','rg_external_ohm','loop_nh'], p)) for p in itertools.product(c['bus_voltages_v'],c['target_currents_a'],c['external_gate_resistances_ohm'],c['power_loop_inductances_nh'])]
    if nominal_only:
        points = [dict(bus_v=75,target_a=40,rg_external_ohm=1,loop_nh=2)]
    rows = []
    nominal = None
    for index,p in enumerate(points):
        key = f"v{p['bus_v']}_i{p['target_a']}_rg{p['rg_external_ohm']}_l{p['loop_nh']}"
        row,w,times = simulate(measurement_config,p,model,exe,out/key)
        rows.append(row)
        if p == dict(bus_v=75,target_a=40,rg_external_ohm=1,loop_nh=2):
            nominal = (w,times,p)
        if index%8 == 0 or index == len(points)-1:
            print(f'DPT {index+1}/{len(points)} finished',flush=True)
    with (out/'switching_table.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    (out/'summary.json').write_text(json.dumps(dict(config=c,model_sha256=digest,simulator=str(exe),points=rows),indent=2))
    (out/'dc_reference.json').write_text(json.dumps(dict(current_a=measurement_config['_dc_current_a'],voltage_v=measurement_config['_dc_voltage_v']),indent=2))
    if nominal:
        w,times,p = nominal
        fig,axes=plt.subplots(3,2,figsize=(11,8))
        for j,(label,edge) in enumerate([('First turn-off',times['off1']),('Second turn-on',times['on2'])]):
            mask=(w['time']>=edge-20e-9)&(w['time']<=edge+150e-9)
            t=(w['time'][mask]-edge)*1e9
            for ax,y,ylabel in zip(axes[:,j],[w['v(d)']-w['v(s)'],w['i(vsense)'],w['v(g)']-w['v(s)']],['Vds (V)','Drain terminal current (A)','Vgs (V)']):
                ax.plot(t,y[mask]);ax.set_ylabel(ylabel);ax.grid(alpha=.25);ax.set_xlabel('Time from command (ns)')
            axes[0,j].set_title(label)
            axes[0,j].plot(t,(w['v(top)']-w['v(sw)'])[mask],linestyle='--',label='Complementary Vds')
            axes[0,j].axhline(100,color='red',linestyle=':',label='100 V rating')
            axes[0,j].legend(fontsize=7)
        fig.suptitle('EPC2361 DPT: 75 V, target 40 A, external Rg=1 ohm, loop L=2 nH, 125 C')
        fig.tight_layout();fig.savefig(out/'nominal_waveforms.png',dpi=150);fig.savefig(out/'nominal_waveforms.pdf');plt.close(fig)
    from plot_double_pulse import main as plot_sensitivity
    plot_sensitivity()
    print(f'Results: {out}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',type=Path,default=ROOT/'data/inputs/double_pulse.json')
    parser.add_argument('--nominal-only',action='store_true')
    args=parser.parse_args()
    main(args.config,args.nominal_only)
