"""Separate SPICE characterization: new temperature DC runs and saved DPT data."""
from pathlib import Path
import csv
import hashlib
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_double_pulse import ROOT, prepare_model, dc_reference


def write_csv(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    settings = json.loads((ROOT/'data/inputs/spice_characterization.json').read_text())
    saved = json.loads((ROOT/'results/double_pulse/summary.json').read_text())
    source = ROOT/'data/spice/EPC2361.lib'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if saved['model_sha256'] != digest:
        raise ValueError('Saved DPT model hash differs: rerun run_double_pulse.py first.')
    for t in settings['rds_temperatures_c']:
        if not np.isfinite(t) or not -40 <= t <= 150:
            raise ValueError('DC temperatures must be within -40 to 150 C')
    c = saved['config']
    out = ROOT/'results/spice_characterization'
    out.mkdir(parents=True, exist_ok=True)
    exe = Path(os.environ.get('LTSPICE_EXE', Path(os.environ['LOCALAPPDATA'])/'Programs/ADI/LTspice/LTspice.exe'))
    model, _ = prepare_model()
    dc_rows = []
    for temperature in settings['rds_temperatures_c']:
        dc = dc_reference(dict(c, temperature_c=temperature), model, exe, out/f'dc_{temperature}c')
        for current, voltage in zip(dc['_dc_current_a'], dc['_dc_voltage_v']):
            if current > 0:
                dc_rows.append(dict(temperature_c=temperature, current_a=current,
                                    vds_v=voltage, rds_on_mohm=1000*voltage/current))
        print(f'DC characterization at {temperature} C complete', flush=True)
    write_csv(out/'rds_on.csv', dc_rows)
    write_csv(out/'switching.csv', saved['points'])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for current in settings['rds_plot_currents_a']:
        series = [r for r in dc_rows if np.isclose(r['current_a'], current)]
        if len(series) != len(settings['rds_temperatures_c']):
            raise ValueError('Requested Rds current is outside the DC grid')
        axes[0].plot([r['temperature_c'] for r in series], [r['rds_on_mohm'] for r in series], marker='o', label=f'{current} A')
    for temperature in settings['rds_temperatures_c']:
        series = [r for r in dc_rows if r['temperature_c'] == temperature]
        axes[1].plot([r['current_a'] for r in series], [r['rds_on_mohm'] for r in series], label=f'{temperature} C')
    axes[0].set_xlabel('Fixed junction temperature (C)')
    axes[1].set_xlabel('Drain current (A)')
    for ax in axes:
        ax.set_ylabel('Model Vds / Ids (mohm)'); ax.grid(alpha=.25); ax.legend(fontsize=8)
    fig.suptitle('EPC2361 model DC on-resistance at Vgs = 5 V (no self-heating)')
    fig.tight_layout(); fig.savefig(out/'rds_on.pdf'); fig.savefig(out/'rds_on.png', dpi=160); plt.close(fig)
    metrics = [
        ('eon_channel_excess_uj', 'Turn-on excess channel energy (uJ)', 'i_on_a'),
        ('eoff_channel_excess_uj', 'Turn-off channel energy (uJ)', 'i_off_a'),
        ('max_dvdt_on_over_1ns', 'Turn-on max absolute 1 ns dv/dt (V/ns)', 'i_on_a'),
        ('max_dvdt_off_over_1ns', 'Turn-off max absolute 1 ns dv/dt (V/ns)', 'i_off_a'),
        ('max_didt_on_over_1ns', 'Turn-on max absolute 1 ns di/dt (A/ns)', 'i_on_a'),
        ('max_didt_off_over_1ns', 'Turn-off max absolute 1 ns di/dt (A/ns)', 'i_off_a'),
        ('vds_peak_v', 'Maximum Vds across either FET (V)', 'i_on_a')]
    voltages = sorted(set(r['bus_v'] for r in saved['points']))
    inductances = sorted(set(r['loop_nh'] for r in saved['points']))
    resistances = sorted(set(r['rg_external_ohm'] for r in saved['points']))
    for key, label, current_key in metrics:
        fig, axes = plt.subplots(len(voltages), len(inductances), figsize=(12, 7), squeeze=False)
        for i, voltage in enumerate(voltages):
            for j, inductance in enumerate(inductances):
                ax = axes[i,j]
                for resistance in resistances:
                    series = sorted([r for r in saved['points'] if r['bus_v']==voltage and r['loop_nh']==inductance and r['rg_external_ohm']==resistance], key=lambda r:r[current_key])
                    ax.plot([r[current_key] for r in series], [r[key] for r in series], marker='o', label=f'Rg={resistance:g} ohm')
                    failed = [r for r in series if not r['voltage_screen_pass']]
                    ax.scatter([r[current_key] for r in failed], [r[key] for r in failed], marker='x', color='red', s=50, zorder=5)
                ax.set_title(f'{voltage:g} V; bus loop L={inductance:g} nH')
                ax.set_xlabel('Actual inductor current at edge (A)'); ax.set_ylabel(label); ax.grid(alpha=.25)
                if key == 'vds_peak_v':
                    ax.axhline(c['design_vds_ceiling_v'],color='black',linestyle='--')
                    ax.axhline(c['absolute_vds_ceiling_v'],color='red',linestyle=':')
        axes[0,0].legend(fontsize=7)
        fig.suptitle(f"EPC2361 DPT at {c['temperature_c']:g} C; red crosses fail a voltage screen")
        fig.tight_layout(); fig.savefig(out/f'{key}.pdf'); fig.savefig(out/f'{key}.png',dpi=160); plt.close(fig)
    summary = dict(settings=settings, dpt_config=c, model_sha256=digest,
                   dpt_source_sha256=hashlib.sha256((ROOT/'results/double_pulse/summary.json').read_bytes()).hexdigest(),
                   switching_cases=len(saved['points']), failed_cases=sum(not r['voltage_screen_pass'] for r in saved['points']),
                   rds_at_50a=[r for r in dc_rows if r['current_a']==50], figures=[dict(file=key, label=label) for key,label,_ in metrics])
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(f'Characterization data and figures: {out}',flush=True)


if __name__=='__main__': main()
