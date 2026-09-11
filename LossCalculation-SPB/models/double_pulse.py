"""LTspice ASCII waveform reader and explicitly defined DPT measurements."""
from pathlib import Path
import numpy as np


def read_raw(path):
    data = Path(path).read_bytes()
    text = data.decode('utf-16' if data.startswith(b'\xff\xfe') else 'utf-8')
    text = text.replace('\r\n', '\n')
    header, values = text.split('Values:\n', 1)
    lines = header.split('Variables:\n', 1)[1].strip().splitlines()
    names = [line.split()[1].lower() for line in lines]
    tokens = np.fromstring(values, sep=' ')
    table = tokens.reshape(-1, len(names)+1)[:, 1:]
    if not np.all(np.isfinite(table)) or np.any(np.diff(table[:, 0]) <= 0):
        raise ValueError('Nonfinite or nonmonotonic waveform')
    return dict(zip(names, table.T))


def integrate(t, y, lo, hi):
    mask = (t > lo) & (t < hi)
    x = np.concatenate(([lo], t[mask], [hi]))
    return float(np.trapezoid(np.interp(x, t, y), x))


def measure(w, c, point, times):
    t = w['time']
    vd = w['v(d)']-w['v(s)']
    vg = w['v(g)']-w['v(s)']
    current = w['i(vsense)']
    heat = w['v(pdut)']  # Numeric volts represent dissipated channel+access power in W.
    on, off = times['on2'], times['off1']
    window = c['energy_window_ns']*1e-9
    result = dict(point)
    for label, edge in [('on', on), ('off', off)]:
        mask = (t >= edge) & (t <= edge+window)
        actual_current = float(np.interp(edge, t, w['i(lload)']))
        result[f'i_{label}_a'] = actual_current
        result[f'e{label}_terminal_uj'] = integrate(t, vd*current, edge, edge+window)*1e6
        raw_heat = integrate(t, heat, edge, edge+window)
        # Subtract normal on-state channel conduction only for the turn-on window.
        if '_dc_current_a' not in c:
            raise ValueError('DPT heat subtraction requires the separately simulated DC curve')
        drop = np.interp(w['i(lload)'], c['_dc_current_a'], c['_dc_voltage_v'])
        baseline = integrate(t, drop*w['i(lload)'], edge, edge+window) if label == 'on' else 0
        result[f'e{label}_channel_raw_uj'] = raw_heat*1e6
        result[f'e{label}_channel_excess_uj'] = (raw_heat-baseline)*1e6
        result[f'max_abs_dvdt_{label}_v_per_ns'] = float(np.max(np.abs(np.gradient(vd[mask], t[mask]))))*1e-9
        result[f'max_abs_didt_{label}_a_per_ns'] = float(np.max(np.abs(np.gradient(current[mask], t[mask]))))*1e-9
        dt = c['slope_interval_ns']*1e-9
        grid = np.arange(edge+dt/2, edge+window-dt/2, dt/4)
        for key, y in [('dvdt', vd), ('didt', current)]:
            slope = (np.interp(grid+dt/2,t,y)-np.interp(grid-dt/2,t,y))/dt
            result[f'max_{key}_{label}_over_1ns'] = float(np.max(np.abs(slope)))*1e-9
        result[f'vds_peak_{label}_v'] = float(np.max(vd[mask]))
    region = (t >= off) & (t <= on+window)
    result['vgs_max_v'] = float(np.max(vg[region]))
    result['vgs_min_v'] = float(np.min(vg[region]))
    result['dut_vds_peak_v'] = max(result['vds_peak_on_v'], result['vds_peak_off_v'])
    result['freewheel_vds_peak_v'] = float(np.max((w['v(top)']-w['v(sw)'])[region]))
    result['freewheel_vgs_max_v'] = float(np.max((w['v(gh)']-w['v(sw)'])[region]))
    result['freewheel_vgs_min_v'] = float(np.min((w['v(gh)']-w['v(sw)'])[region]))
    result['vds_peak_v'] = max(result['dut_vds_peak_v'], result['freewheel_vds_peak_v'])
    result['overshoot_v'] = result['vds_peak_v']-point['bus_v']
    result['vds_design_margin_v'] = c['design_vds_ceiling_v']-result['vds_peak_v']
    result['vds_absolute_margin_v'] = c['absolute_vds_ceiling_v']-result['vds_peak_v']
    result['voltage_screen_pass'] = (result['vds_design_margin_v'] >= 0
                                    and max(result['vgs_max_v'],result['freewheel_vgs_max_v']) <= 6
                                    and min(result['vgs_min_v'],result['freewheel_vgs_min_v']) >= -4)
    result['channel_energy_pair_uj'] = result['eon_channel_excess_uj']+result['eoff_channel_excess_uj']
    result['energy_window_ns'] = c['energy_window_ns']
    return result
