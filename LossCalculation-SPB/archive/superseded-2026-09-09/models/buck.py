"""First-order hard-switched CCM buck screening, evaluated at design-limit Rds.

No transient SOA, parasitic ringing, unequal sharing or driver-current model.
"""
import math
from models.thermal import shared_sink


def validate(c, d):
    if c['topology'] != 'synchronous_buck_ccm':
        raise ValueError('Only synchronous_buck_ccm is implemented.')
    for key, value in c.items():
        if isinstance(value, (float, int)) and not math.isfinite(value):
            raise ValueError(f'{key} must be finite')
    for key in ['vin_v', 'vout_v', 'pout_w', 'inductance_h', 'frequency_min_hz',
                'frequency_max_hz', 'device_peak_current_design_limit_a']:
        if c[key] <= 0:
            raise ValueError(f'{key} must be positive')
    if not 0 < c['vout_v'] < c['vin_v']:
        raise ValueError('Buck requires 0 < Vout < Vin.')
    if c['frequency_max_hz'] < c['frequency_min_hz']:
        raise ValueError('Frequency bounds are reversed.')
    if type(c['frequency_points']) is not int or c['frequency_points'] < 2:
        raise ValueError('frequency_points must be an integer >= 2')
    if not c['parallel_counts'] or any(type(n) is not int or n < 1 for n in c['parallel_counts']):
        raise ValueError('parallel_counts must contain positive integers')
    if not -40 <= c['ambient_c'] < c['junction_limit_c'] < 125:
        raise ValueError('This screening model requires -40 <= ambient < junction limit < 125 C.')
    if not 0 < c['efficiency_target_pct'] <= 100 or not 0 < c['voltage_utilization_limit'] <= 1:
        raise ValueError('Invalid efficiency or voltage utilization target.')
    if c['gate_drive_v'] != 5:
        raise ValueError('Device parameters are characterized at 5 V gate drive; use 5 V.')
    if not 0 <= c['assumed_low_side_eoss_dissipated_fraction'] <= 1:
        raise ValueError('Eoss fraction must be between 0 and 1')
    for key in ['sink_to_ambient_k_per_w', 'case_to_sink_k_per_w_per_device',
                'assumed_overshoot_v', 'assumed_turn_on_overlap_s',
                'assumed_turn_off_overlap_s', 'deadtime_per_edge_s',
                'assumed_reverse_drop_v', 'assumed_rds_temperature_coefficient_per_c',
                'other_converter_loss_w']:
        if c[key] < 0:
            raise ValueError(f'{key} must be nonnegative')


def evaluate(c, d, frequency, n):
    duty = c['vout_v'] / c['vin_v']
    current = c['pout_w'] / c['vout_v']
    ripple = (c['vin_v'] - c['vout_v']) * duty / (c['inductance_h'] * frequency)
    imin, imax = current - ripple / 2, current + ripple / 2
    irms2 = current**2 + ripple**2 / 12
    # Fixed hot resistance avoids reporting optimistic cold conduction losses.
    r = d['rds_on_max_25c_ohm'] * (1 + c['assumed_rds_temperature_coefficient_per_c'] * (c['junction_limit_c'] - 25))
    hs_cond = irms2 * r * duty / n
    ls_cond = irms2 * r * (1 - duty) / n
    overlap = 0.5 * c['vin_v'] * (max(imin, 0) * c['assumed_turn_on_overlap_s'] + imax * c['assumed_turn_off_overlap_s']) * frequency
    # Stored energy estimate; using the 50 V equivalent C at other voltages is flagged.
    eoss = 0.5 * d['coss_energy_0_to_50v_f'] * c['vin_v']**2
    hs_cap = n * eoss * frequency
    ls_cap = n * eoss * frequency * c['assumed_low_side_eoss_dissipated_fraction']
    dead = 2 * c['deadtime_per_edge_s'] * c['assumed_reverse_drop_v'] * current * frequency
    gate = 2 * n * d['qg_max_c'] * c['gate_drive_v'] * frequency
    hs = hs_cond + overlap + hs_cap
    ls = ls_cond + dead + ls_cap
    fet = hs + ls
    total = fet + gate + c['other_converter_loss_w']
    tj, required = shared_sink(fet, max(hs, ls) / n, c['ambient_c'], c['junction_limit_c'],
                               d['rth_junction_case_k_per_w'] + c['case_to_sink_k_per_w_per_device'],
                               c['sink_to_ambient_k_per_w'])
    efficiency = 100 * c['pout_w'] / (c['pout_w'] + total)
    reasons = []
    if imin <= 0:
        reasons.append('outside_CCM')
    if 2 * c['deadtime_per_edge_s'] * frequency >= min(duty, 1 - duty):
        reasons.append('deadtime_exceeds_duty_window')
    if c['vin_v'] + c['assumed_overshoot_v'] > c['voltage_utilization_limit'] * d['vds_max_v']:
        reasons.append('voltage_margin')
    if imax / n > min(c['device_peak_current_design_limit_a'], 133):
        reasons.append('current_limit')
    if tj > c['junction_limit_c']:
        reasons.append('thermal_limit')
    if efficiency < c['efficiency_target_pct']:
        reasons.append('efficiency_target')
    return dict(frequency_hz=float(frequency), parallel_per_bank=n, total_devices=2*n,
                ripple_pp_a=ripple, peak_device_a=imax/n, conduction_w=hs_cond+ls_cond,
                overlap_w=overlap, coss_w=hs_cap+ls_cap, deadtime_w=dead, gate_drive_w=gate,
                fet_loss_w=fet, total_modeled_loss_w=total, efficiency_estimate_pct=efficiency,
                high_side_per_device_w=hs/n, low_side_per_device_w=ls/n,
                junction_estimate_c=tj, required_max_sink_k_per_w=required,
                coss_voltage_approximation=not math.isclose(c['vin_v'], 50),
                passes_screen=not reasons, failed_constraints=';'.join(reasons))
