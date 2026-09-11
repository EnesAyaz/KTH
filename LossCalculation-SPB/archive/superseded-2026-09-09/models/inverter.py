"""Balanced three-phase inverter average losses under continuous SVM.

Sinusoidal phase currents; one hard commutation per leg per carrier cycle.
Switching times are assumed independent of parallel count. Not a switching simulator.
"""
import math
from models.thermal import shared_sink


def validate(c, d):
    if c['topology'] != 'three_phase_two_level_svm':
        raise ValueError('Expected three_phase_two_level_svm')
    for key, value in c.items():
        if isinstance(value, (int, float)) and not math.isfinite(value):
            raise ValueError(f'{key} must be finite')
    for key in ['vin_v', 'pout_w', 'frequency_min_hz', 'frequency_max_hz',
                'device_peak_current_design_limit_a', 'eoss_at_bus_voltage_j']:
        if c[key] <= 0:
            raise ValueError(f'{key} must be positive')
    if not 0 < c['modulation_index'] <= 2 / math.sqrt(3):
        raise ValueError('Linear SVM requires 0 < m <= 2/sqrt(3), with Vphase_peak=m*Vdc/2')
    if not 0 < c['power_factor'] <= 1:
        raise ValueError('Motoring model requires 0 < power_factor <= 1')
    if c['frequency_max_hz'] < c['frequency_min_hz']:
        raise ValueError('Frequency bounds are reversed')
    if type(c['frequency_points']) is not int or c['frequency_points'] < 2:
        raise ValueError('frequency_points must be an integer >= 2')
    if not c['parallel_counts'] or any(type(n) is not int or n < 1 for n in c['parallel_counts']):
        raise ValueError('parallel_counts must contain positive integers')
    if not -40 <= c['coolant_temperature_c'] < c['junction_limit_c'] <= 125:
        raise ValueError('Require -40 <= coolant < junction limit <= 125 C for this screening model')
    if not 0 < c['efficiency_target_pct'] < 100 or not 0 < c['voltage_utilization_limit'] <= 1:
        raise ValueError('Invalid efficiency/voltage target')
    if c['gate_drive_v'] != 5:
        raise ValueError('Current device parameters require 5 V gate drive')
    if not math.isclose(c['vin_v'], c['eoss_reference_voltage_v']):
        raise ValueError('Update Eoss and its reference voltage from the curve when changing bus voltage')
    if c['rds_hot_multiplier'] < 1 or c['hottest_device_loss_multiplier'] < 1:
        raise ValueError('Resistance and hot-device multipliers must be >= 1')
    if not 0 <= c['assumed_low_side_eoss_dissipated_fraction'] <= 1:
        raise ValueError('Coss allowance fraction must be between 0 and 1')
    for key in ['phase_ripple_rms_a', 'phase_ripple_peak_a', 'cold_plate_to_water_k_per_w',
                'tim_k_per_w_per_device', 'assumed_overshoot_v',
                'assumed_turn_on_overlap_s', 'assumed_turn_off_overlap_s',
                'deadtime_per_edge_s', 'minimum_gate_pulse_s', 'assumed_reverse_drop_v', 'other_converter_loss_w']:
        if c[key] < 0:
            raise ValueError(f'{key} must be nonnegative')
    if c['phase_ripple_peak_a'] < c['phase_ripple_rms_a']:
        raise ValueError('Ripple peak must be >= ripple RMS')


def evaluate(c, d, frequency, n):
    vphase = c['modulation_index'] * c['vin_v'] / (2 * math.sqrt(2))
    irms = c['pout_w'] / (3 * vphase * c['power_factor'])
    ipeak = math.sqrt(2) * irms + c['phase_ripple_peak_a']
    iabs = 2 * math.sqrt(2) * irms / math.pi
    r = d['rds_on_max_25c_ohm'] * c['rds_hot_multiplier']
    conduction = 3 * (irms**2 + c['phase_ripple_rms_a']**2) * r / n
    overlap = 3 * 0.5 * c['vin_v'] * iabs * (c['assumed_turn_on_overlap_s'] + c['assumed_turn_off_overlap_s']) * frequency
    cap = 3 * n * c['eoss_at_bus_voltage_j'] * (1 + c['assumed_low_side_eoss_dissipated_fraction']) * frequency
    dead = 3 * 2 * c['deadtime_per_edge_s'] * c['assumed_reverse_drop_v'] * iabs * frequency
    gate = 6 * n * d['qg_max_c'] * c['gate_drive_v'] * frequency
    fet = conduction + overlap + cap + dead
    total = fet + gate + c['other_converter_loss_w']
    hottest = fet / (6 * n) * c['hottest_device_loss_multiplier']
    tj, required = shared_sink(fet, hottest, c['coolant_temperature_c'], c['junction_limit_c'],
                               d['rth_junction_case_k_per_w'] + c['tim_k_per_w_per_device'],
                               c['cold_plate_to_water_k_per_w'])
    efficiency = 100 * c['pout_w'] / (c['pout_w'] + total)
    budget = c['pout_w'] * (100 / c['efficiency_target_pct'] - 1)
    reasons = []
    if c['vin_v'] + c['assumed_overshoot_v'] > c['voltage_utilization_limit'] * d['vds_max_v']:
        reasons.append('voltage_margin')
    if ipeak/n > c['device_peak_current_design_limit_a']:
        reasons.append('user_peak_current_limit')
    if tj >= c['junction_limit_c']:
        reasons.append('thermal_limit')
    if efficiency <= c['efficiency_target_pct']:
        reasons.append('efficiency_target')
    # Minimum zero-vector margin at maximum line-to-line reference span.
    min_duty = (1 - math.sqrt(3)*c['modulation_index']/2) / 2
    timing_margin = min_duty/frequency - c['deadtime_per_edge_s'] - c['minimum_gate_pulse_s']
    if timing_margin <= 0:
        reasons.append('SVM_minimum_pulse_deadtime')
    return dict(frequency_hz=float(frequency), parallel_per_bank=n, total_devices=6*n,
                phase_voltage_rms_v=vphase, line_voltage_rms_v=vphase*math.sqrt(3),
                phase_current_rms_a=irms, peak_device_a=ipeak/n,
                conduction_w=conduction, overlap_w=overlap, coss_w=cap, deadtime_w=dead,
                gate_drive_w=gate, fet_loss_w=fet, total_modeled_loss_w=total,
                efficiency_estimate_pct=efficiency, hottest_device_w=hottest,
                junction_estimate_c=tj, required_max_sink_k_per_w=required,
                loss_budget_w=budget, remaining_other_loss_budget_w=budget-total,
                minimum_pulse_margin_ns=timing_margin*1e9,
                passes_screen=not reasons, failed_constraints=';'.join(reasons))

