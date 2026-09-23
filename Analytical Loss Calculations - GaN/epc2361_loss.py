"""Analytical loss model for an EPC2361 hard-switched half bridge.

The model intentionally exposes its assumptions: it is a first-order design
estimate, not a replacement for double-pulse testing or a SPICE model.
"""
from dataclasses import dataclass, asdict
from math import sqrt, pi, isfinite
from typing import Dict


@dataclass
class LossInputs:
    vbus: float = 75.0
    ac_rms: float = 40.0
    fsw: float = 100e3
    devices_parallel: int = 1
    modulation: str = "sinusoidal"
    modulation_index: float = 1.0
    power_factor: float = 1.0
    waveform_factor: float = 1.0  # multiplier on sinusoidal switch RMS current
    rds25_mohm: float = 0.75
    rds_max_mohm: float = 1.0
    use_rds_max: bool = True
    rds_temp_scale: float = 1.7  # used only in manual mode
    rds_temperature_mode: str = "iterative"  # iterative or manual
    vgs: float = 5.0
    vgs_threshold: float = 1.1
    vgs_plateau: float = 2.1
    qgs1_nc: float = 6.0  # legacy name: charge to threshold
    qgsth_nc: float = 6.0
    qg_nc: float = 28.2  # 28 nC at 50 V plus estimated QGD increment
    qgd_nc: float = 4.0  # ~3.8 + integral(CRSS, 50..75 V), Figure 5b
    qgs2_nc: float = 2.5  # QGS - QG(th) = 8.5 - 6
    rg_internal: float = 0.4
    waveform_current_a: float = 0.0  # 0 selects sinusoidal peak; independent DPT current
    rg_on: float = 1.0
    rg_off: float = 1.0
    driver_source_r: float = 0.5
    driver_sink_r: float = 0.5
    driver_source_a: float = 2.0
    driver_sink_a: float = 2.0
    dead_time_ns: float = 50.0
    effective_dead_time_ns: float = 50.0
    loop_inductance_nh: float = 2.0
    thermal_mode: str = "case"  # case or ambient
    ambient_c: float = 25.0
    case_c: float = 50.0
    rtheta_jc_c_w: float = 0.2
    rtheta_ja_c_w: float = 44.0  # JEDEC board; EVB is 25 C/W
    target_junction_c: float = 125.0
    coss_nf: float = 0.9  # small-signal estimate at 75 V; ringing only
    eoss_uj: float = 3.2  # approximate Figure 6 value at 75 V
    qoss_nc: float = 114.0  # approximate Figure 6 value at 75 V
    qoss_voltage: float = 75.0
    vsd: float = 2.2  # approximate Figure 8 at operating current
    hard_switching: bool = True
    optional_loop_r_mohm: float = 0.0


# Approximate graphical readings of EPC2361 datasheet p3, Figure 9.
# Normalized to RDS(on) at 25 C and 5 V gate; no extrapolation outside 0..150 C.
RDS_TEMPERATURE_CURVE = ((0., .84), (25., 1.), (50., 1.16), (75., 1.33),
                         (100., 1.49), (125., 1.65), (150., 1.80))


def rds_temperature_factor(temperature_c):
    """Piecewise-linear interpolation of typical normalized resistance."""
    if not isfinite(temperature_c) or not 0 <= temperature_c <= 150:
        raise ValueError("Junction temperature is outside the supported RDS curve (0..150 C); "
                         "no valid thermal solution within this range. Review cooling and losses.")
    for (t0, k0), (t1, k1) in zip(RDS_TEMPERATURE_CURVE, RDS_TEMPERATURE_CURVE[1:]):
        if temperature_c <= t1:
            return k0 + (k1-k0)*(temperature_c-t0)/(t1-t0)
    return RDS_TEMPERATURE_CURVE[-1][1]


def solve_thermal(i, rds_base_ohm, conduction_coefficient, fixed_semiconductor_loss):
    """Solve Tj = Tref + Rtheta * Psemiconductor(Tj)/2 for equal FETs.

    A valid result has thermal residual below 1e-6 C. Failure or leaving the
    datasheet curve range raises ValueError instead of reporting a false solution.
    """
    reference = i.case_c if i.thermal_mode == "case" else i.ambient_c
    resistance = i.rtheta_jc_c_w if i.thermal_mode == "case" else i.rtheta_ja_c_w
    if i.rds_temperature_mode == "manual":
        rds = rds_base_ohm * i.rds_temp_scale
        junction = reference + resistance*(conduction_coefficient*rds + fixed_semiconductor_loss)/2
        return rds, junction, 0, 0.0, i.rds_temp_scale
    junction = reference
    for iteration in range(1, 201):
        scale = rds_temperature_factor(junction)
        rds = rds_base_ohm * scale
        updated = reference + resistance*(conduction_coefficient*rds + fixed_semiconductor_loss)/2
        residual = updated - junction
        if abs(residual) < 1e-6:
            return rds, junction, iteration, abs(residual), scale
        junction = updated
    raise ValueError("Thermal iteration did not converge within 200 iterations")


def calculate(i: LossInputs) -> Dict[str, float]:
    """Return loss components (W), stress and intermediate values.

    For sinusoidal load, each device carries I_AC,rms/sqrt(2).  ``waveform_factor``
    scales the assumed sinusoidal amplitude. Two commutations per switching
    cycle contribute dead-time loss. AN030 V*Qoss accounts for both output
    capacitors once per hard-switching PWM cycle.
    """
    _validate(i)
    n = i.devices_parallel
    isw_rms = i.ac_rms / sqrt(2.0) * i.waveform_factor
    peak = i.ac_rms * sqrt(2.0) * i.waveform_factor
    per_device_rms = isw_rms / n
    rds_base = max(i.rds25_mohm, i.rds_max_mohm) if i.use_rds_max else i.rds25_mohm
    ploop_r = isw_rms * isw_rms * i.optional_loop_r_mohm / 1000.0 * 2.0
    # AN030 Figures 4/5: gate current depends on the gate-voltage segment.
    ron = i.rg_on + i.driver_source_r + i.rg_internal
    roff = i.rg_off + i.driver_sink_r + i.rg_internal
    ion = min((i.vgs - i.vgs_plateau) / ron, i.driver_source_a)
    ioff = min(i.vgs_plateau / roff, i.driver_sink_a)
    vmean = (i.vgs_threshold + i.vgs_plateau) / 2
    ion_cr = min((i.vgs - vmean) / ron, i.driver_source_a)
    ioff_cf = min(vmean / roff, i.driver_sink_a)
    qgsth_nc = i.qgsth_nc if i.qgsth_nc > 0 else i.qgs1_nc
    qpost_nc = i.qg_nc - qgsth_nc - i.qgs2_nc - i.qgd_nc
    # Segment-average gate voltage approximates the RC charging/discharging.
    tgs1_on = qgsth_nc * 1e-9 / min((i.vgs-i.vgs_threshold/2)/ron, i.driver_source_a)
    tgs1_off = qgsth_nc * 1e-9 / min((i.vgs_threshold/2)/roff, i.driver_sink_a)
    tpost_on = qpost_nc * 1e-9 / min((i.vgs-i.vgs_plateau)/2/ron, i.driver_source_a)
    tpost_off = qpost_nc * 1e-9 / min((i.vgs+i.vgs_plateau)/2/roff, i.driver_sink_a)
    tcr = i.qgs2_nc * 1e-9 / ion_cr
    tvf = i.qgd_nc * 1e-9 / ion
    tvr = i.qgd_nc * 1e-9 / ioff
    tcf = i.qgs2_nc * 1e-9 / ioff_cf
    waveform_current = i.waveform_current_a or peak
    mean_current = 2 * peak / pi
    eon_overlap = 0.5 * i.vbus * waveform_current * (tcr + tvf)
    eoff_overlap = 0.5 * i.vbus * waveform_current * (tvr + tcf)
    # One hard turn-on/off pair per PWM period for the half bridge; opposite
    # device commutates softly. Average |sin| over the electrical period.
    poverlap = 0.5 * i.vbus * mean_current * (tcr+tvf+tvr+tcf) * i.fsw
    if not i.hard_switching:
        poverlap = 0.0
    # AN030 Eqs.17-18: equal-device half-bridge capacitor loss is V*Qoss*f.
    # Eoss is reported for reference, not added again. Qoss must be at VBUS.
    eoss = i.eoss_uj * 1e-6
    pcoss = i.vbus * i.qoss_nc * 1e-9 * i.fsw if i.hard_switching else 0.0
    pgate = 2.0 * i.qg_nc * 1e-9 * i.vgs * i.fsw
    dead_fraction = 2 * i.effective_dead_time_ns * 1e-9 * i.fsw
    pdead = mean_current * i.vsd * dead_fraction
    conduction_coefficient = 2 * isw_rms**2 * (1-dead_fraction)
    rds, junction, thermal_iterations, thermal_residual, temperature_scale = solve_thermal(
        i, rds_base/1000, conduction_coefficient, poverlap + pcoss + pdead)
    pcond = conduction_coefficient * rds
    di_dt_on = waveform_current / tcr
    di_dt_off = waveform_current / tcf
    overshoot_on = i.loop_inductance_nh * 1e-9 * di_dt_on
    overshoot_off = i.loop_inductance_nh * 1e-9 * di_dt_off
    overshoot = max(overshoot_on, overshoot_off)
    total = pcond + ploop_r + poverlap + pcoss + pgate + pdead
    semiconductor_loss = pcond + poverlap + pcoss + pdead
    p_device = semiconductor_loss / 2.0  # symmetrical line-cycle average, external losses excluded
    output_voltage_rms = i.modulation_index * i.vbus / (2.0 * sqrt(2.0))
    output_power = output_voltage_rms * i.ac_rms * i.power_factor
    output = dict(rds_on_mohm=rds*1000, rds_temperature_factor=temperature_scale,
                  thermal_iterations=thermal_iterations, thermal_residual_c=thermal_residual,
                  thermal_iteration_enabled=i.rds_temperature_mode == "iterative",
                  junction_rating_exceeded=junction > 150,
                  waveform_current_a=waveform_current, mean_abs_current_a=mean_current,
                  semiconductor_loss=semiconductor_loss, loss_per_device=p_device,
                  threshold_time_on_ns=tgs1_on*1e9, threshold_time_off_ns=tgs1_off*1e9,
                  post_time_on_ns=tpost_on*1e9, post_time_off_ns=tpost_off*1e9,
                  voltage_rating_exceeded=i.vbus + overshoot > 100,
                  conduction=pcond, optional_loop_resistance=ploop_r,
                  switching_overlap=poverlap, coss_eoss=pcoss,
                  gate_drive=pgate, dead_time_reverse_conduction=pdead,
                  layout_inductance_overshoot=overshoot, total_loss=total,
                  output_voltage_rms=output_voltage_rms, output_power=output_power,
                  efficiency=100.0 * output_power / (output_power + total),
                  switch_rms=per_device_rms, rise_time_ns=tcr * 1e9, fall_time_ns=tcf * 1e9,
                  gate_rise_time_ns=(tgs1_on + tcr + tvf + tpost_on) * 1e9,
                  gate_fall_time_ns=(tpost_off + tvr + tcf + tgs1_off) * 1e9,
                  post_plateau_charge_nc=qpost_nc,
                  threshold_gate_charge_nc=qgsth_nc,
                  current_rise_time_ns=tcr * 1e9, voltage_fall_time_ns=tvf * 1e9,
                  voltage_rise_time_ns=tvr * 1e9, current_fall_time_ns=tcf * 1e9,
                  eon_overlap_j=eon_overlap, eoff_overlap_j=eoff_overlap,
                  dvdt_on_v_ns=i.vbus / (tvf * 1e9),
                  dvdt_off_v_ns=i.vbus / (tvr * 1e9),
                  didt_on_a_ns=di_dt_on / 1e9,
                  didt_off_a_ns=di_dt_off / 1e9,
                  gate_current_on=ion, gate_current_off=ioff, junction_temperature=junction,
                  thermal_limit_exceeded=junction > i.target_junction_c,
                  overshoot_voltage=overshoot, overshoot_on_voltage=overshoot_on,
                  overshoot_off_voltage=overshoot_off,
                  stress_voltage=i.vbus + overshoot,
                  coss_energy_per_device_j=eoss, coss_energy_switch_bank_j=eoss * n,
                  rds_on_ohm=rds, rds_base_mohm=rds_base)
    return output


def _validate(i: LossInputs) -> None:
    for name, value in asdict(i).items():
        if isinstance(value, (int, float)) and not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if i.devices_parallel != 1:
        raise ValueError("This model uses one device per switch position")
    if i.rds_temperature_mode not in ("iterative", "manual"):
        raise ValueError("rds_temperature_mode must be iterative or manual")
    if i.modulation != "sinusoidal":
        raise ValueError("Only sinusoidal modulation is implemented")
    if i.driver_source_a <= 0 or i.driver_sink_a <= 0:
        raise ValueError("Driver current limits must be positive")
    if i.rg_on+i.driver_source_r+i.rg_internal <= 0 or i.rg_off+i.driver_sink_r+i.rg_internal <= 0:
        raise ValueError("Total gate-path resistances must be positive")
    qth = i.qgsth_nc if i.qgsth_nc > 0 else i.qgs1_nc
    if qth+i.qgs2_nc+i.qgd_nc > i.qg_nc:
        raise ValueError("Gate-charge segments cannot exceed total QG")
    if abs(i.qoss_voltage-i.vbus) > 1e-6:
        raise ValueError("Enter QOSS and EOSS at VBUS and set QOSS reference voltage to VBUS")
    if 2*max(i.dead_time_ns,i.effective_dead_time_ns)*1e-9*i.fsw >= 1:
        raise ValueError("Two dead times must fit inside one switching period")
    if i.rds25_mohm <= 0 or i.rds_max_mohm <= 0:
        raise ValueError("On-resistances must be positive")
    positive = ("vbus", "ac_rms", "fsw", "rds_temp_scale", "vgs", "vgs_threshold",
                "vgs_plateau", "qgs1_nc", "qg_nc", "qgd_nc",
                "qgs2_nc", "qoss_voltage", "rtheta_jc_c_w", "rtheta_ja_c_w")
    for name in positive:
        if getattr(i, name) <= 0:
            raise ValueError(f"{name} must be greater than zero")
    if i.devices_parallel < 1 or int(i.devices_parallel) != i.devices_parallel:
        raise ValueError("devices_parallel must be a positive integer")
    if i.waveform_factor <= 0 or i.waveform_factor > 2:
        raise ValueError("waveform_factor must be in (0, 2]")
    if i.vgs_threshold >= i.vgs_plateau or i.vgs_plateau >= i.vgs:
        raise ValueError("vgs_threshold < vgs_plateau < vgs must hold")
    if not 0 < i.modulation_index <= 1:
        raise ValueError("modulation_index must be in (0, 1]")
    if not 0 < i.power_factor <= 1:
        raise ValueError("power_factor must be in (0, 1]")
    for name in ("rg_internal", "waveform_current_a", "qgsth_nc", "rg_on", "rg_off", "driver_source_r", "driver_sink_r", "driver_source_a", "driver_sink_a",
                 "dead_time_ns", "effective_dead_time_ns", "loop_inductance_nh", "coss_nf", "eoss_uj",
                 "qoss_nc", "vsd", "optional_loop_r_mohm"):
        if getattr(i, name) < 0:
            raise ValueError(f"{name} cannot be negative")
    if i.thermal_mode not in ("case", "ambient"):
        raise ValueError("thermal_mode must be 'case' or 'ambient'")


if __name__ == "__main__":
    print(calculate(LossInputs()))
