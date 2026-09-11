"""Numerical convergence checks for the nominal double-pulse measurement."""
import json
from run_double_pulse import ROOT, prepare_model, simulate, dc_reference
from models.double_pulse import measure
from pathlib import Path
import os


def main():
    config=json.loads((ROOT/'data/inputs/double_pulse.json').read_text())
    exe=Path(os.environ.get('LTSPICE_EXE',Path(os.environ['LOCALAPPDATA'])/'Programs/ADI/LTspice/LTspice.exe'))
    model,_=prepare_model()
    config=dc_reference(config,model,exe,ROOT/'results/double_pulse/convergence_dc')
    point=dict(bus_v=75,target_a=40,rg_external_ohm=1,loop_nh=2)
    rows=[]
    for step in [0.2,0.1,0.05]:
        c=dict(config,max_timestep_ns=step)
        row,w,times=simulate(c,point,model,exe,ROOT/f'results/double_pulse/convergence_{step}')
        rows.append(dict(timestep_ns=step,metrics=row))
    errors={}
    for key in ['channel_energy_pair_uj','vds_peak_v','max_dvdt_on_over_1ns','max_didt_on_over_1ns']:
        errors[key]=abs(rows[-1]['metrics'][key]-rows[0]['metrics'][key])/abs(rows[-1]['metrics'][key])
    windows=[]
    for window in [100,150,200]:
        windows.append(dict(window_ns=window,metrics=measure(w,dict(config,energy_window_ns=window),point,times)))
    energy=[r['metrics']['channel_energy_pair_uj'] for r in windows]
    window_spread=(max(energy)-min(energy))/abs(energy[1])
    summary=dict(timestep_runs=rows,relative_changes=errors,window_runs=windows,window_relative_spread=window_spread,
                 passed=max(errors.values()) < .05 and window_spread < .05)
    (ROOT/'results/double_pulse/convergence.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(dict(relative_changes=errors,window_relative_spread=window_spread,passed=summary['passed']),indent=2))
    if not summary['passed']:
        raise SystemExit('DPT numerical sensitivity exceeds 5%; inspect convergence.json')


if __name__=='__main__':main()
