"""Fundamental-cycle half-bridge screening, continuous centered SVM / SPWM.
Analytical switching assumptions only; not calibrated parallel-bank SPICE.
"""
import math
import numpy as np

def validate(c,d):
    for k in ('dc_link_v','three_phase_power_w','frequency_min_hz','frequency_max_hz','tim_thickness_mm','tim_conductivity_w_mk','tim_contact_area_mm2'):
        if not math.isfinite(c[k]) or c[k]<=0: raise ValueError(k+' must be positive')
    if not 0<c['power_factor']<=1: raise ValueError('Motoring power factor must be in (0,1]')
    if c['parallel_counts']!=[4,5,6]: raise ValueError('This design study uses 4,5,6 devices per position')
    if c['frequency_max_hz']<c['frequency_min_hz']:raise ValueError('Reversed frequency limits')
    if c['angle_samples']<360 or c['angle_samples']%2:raise ValueError('Use an even angle sample count >=360')
    if not c['coolant_c']<c['junction_limit_c']<=125:raise ValueError('Invalid thermal limits')
    if c['gate_v']!=5 or c['dc_link_v']!=c['eoss_reference_v']:raise ValueError('Update device assumptions for changed gate/bus voltage')
    for key in ('deadtime_ns','min_pulse_ns','overlap_on_ns','overlap_off_ns','coldplate_k_w_per_halfbridge','tim_contact_k_w','other_loss_w_three_phase'):
        if c[key]<0:raise ValueError(key+' must be nonnegative')
    for s in c['modulations']:
        limit={'SVM':2/math.sqrt(3),'SPWM':1}[s['method']]
        if not 0<s['m']<=limit:raise ValueError('Outside linear '+s['method']+' range')

def cycle(c,mode):
    theta=np.arange(c['angle_samples'])*2*np.pi/c['angle_samples']
    refs=mode['m']*np.sin(theta[None,:]-np.arange(3)[:,None]*2*np.pi/3)
    offset=-(refs.max(axis=0)+refs.min(axis=0))/2 if mode['method']=='SVM' else 0
    duty=(1+refs[0]+offset)/2
    vrms=mode['m']*c['dc_link_v']/(2*np.sqrt(2))
    irms=c['three_phase_power_w']/(3*vrms*c['power_factor'])
    current=np.sqrt(2)*irms*np.sin(theta-math.acos(c['power_factor']))
    return theta,duty,current,irms

def evaluate(c,d,mode,f,n,return_cycle=False):
    theta,duty,current,irms=cycle(c,mode)
    abs_i=np.abs(current); per=abs_i/n
    deadfrac=c['deadtime_ns']*1e-9*f
    # Nominal centered PWM duty with one deadtime removed from each channel interval.
    dh=np.maximum(duty-deadfrac,0);dl=np.maximum(1-duty-deadfrac,0)
    resistance=d['rds_on_max_25c_ohm']*c['rds_multiplier_at_125c']
    cond_h=(current/n)**2*resistance*dh
    cond_l=(current/n)**2*resistance*dl
    # Per-device hard-pair energy at instantaneous fundamental current.
    overlap=.5*c['dc_link_v']*per*(c['overlap_on_ns']+c['overlap_off_ns'])*1e-9
    cap=np.full_like(current,c['eoss_j']*(1+c['complementary_eoss_fraction']))
    switching=(overlap+cap)*f
    # Hard switching assigned by current polarity; approximate Coss allocation same.
    sw_h=np.where(current>=0,switching,0);sw_l=np.where(current<0,switching,0)
    reverse=2*deadfrac*c['reverse_drop_v']*per
    dead_h=np.where(current<0,reverse,0);dead_l=np.where(current>=0,reverse,0)
    ph=cond_h+sw_h+dead_h;pl=cond_l+sw_l+dead_l
    fet=n*float(np.mean(ph+pl));hot=max(float(np.mean(ph)),float(np.mean(pl)))*c['hottest_loss_factor']
    gate=2*n*d['qg_max_c']*c['gate_v']*f
    total=fet+gate+c['other_loss_w_three_phase']/3
    rtim=c['tim_thickness_mm']*1e-3/(c['tim_conductivity_w_mk']*c['tim_contact_area_mm2']*1e-6)+c['tim_contact_k_w']
    rjc=d['rth_junction_case_k_per_w'];delta=c['junction_limit_c']-c['coolant_c']
    tj=c['coolant_c']+fet*c['coldplate_k_w_per_halfbridge']+hot*(rjc+rtim)
    reqplate=(delta-hot*(rjc+rtim))/fet
    reqtim=(delta-fet*c['coldplate_k_w_per_halfbridge'])/hot-rjc
    budget=c['three_phase_power_w']*(100/c['efficiency_target_pct']-1)/3
    conduction=n*float(np.mean(cond_h+cond_l));dead=n*float(np.mean(dead_h+dead_l))
    allowed=(budget-conduction-dead-gate-c['other_loss_w_three_phase']/3)/(n*f)
    # Analytic worst-case duty, independent of angular quadrature resolution.
    minduty=(1-(math.sqrt(3)/2 if mode['method']=='SVM' else 1)*mode['m'])/2
    pulse_margin=minduty/f-(c['deadtime_ns']+c['min_pulse_ns'])*1e-9
    reasons=[]
    if total>=budget:reasons.append('efficiency')
    if tj>=c['junction_limit_c']:reasons.append('thermal')
    if math.sqrt(2)*irms/n>c['peak_device_design_a']:reasons.append('peak_current')
    if pulse_margin<=0:reasons.append('minimum_pulse')
    if c['dc_link_v']+c['assumed_overshoot_v']>d['vds_max_v']*c['voltage_utilization']:reasons.append('assumed_voltage_margin')
    r=dict(modulation=mode['method'],m=mode['m'],frequency_hz=float(f),parallel_count=n,devices_per_halfbridge=2*n,
      phase_current_rms_a=float(irms),device_peak_a=math.sqrt(2)*irms/n,
      halfbridge_conduction_w=conduction,halfbridge_overlap_w=n*float(np.mean(overlap))*f,
      halfbridge_coss_w=n*float(np.mean(cap))*f,halfbridge_deadtime_w=dead,halfbridge_gate_w=gate,
      halfbridge_fet_w=fet,halfbridge_total_w=total,three_phase_total_w=3*total,
      efficiency_pct=100*c['three_phase_power_w']/(c['three_phase_power_w']+3*total),
      high_device_average_w=float(np.mean(ph)),low_device_average_w=float(np.mean(pl)),hottest_device_w=hot,
      tim_k_w_per_device=rtim,junction_c=tj,max_coldplate_k_w_per_halfbridge=reqplate,max_tim_k_w_per_device=reqtim,
      max_tim_thickness_mm=(reqtim-c['tim_contact_k_w'])*c['tim_conductivity_w_mk']*c['tim_contact_area_mm2']*1e-3,
      loss_budget_w_per_halfbridge=budget,allowed_mean_switching_pair_uj_per_device=allowed*1e6,
      modeled_mean_switching_pair_uj_per_device=float(np.mean(overlap+cap))*1e6,
      pulse_margin_ns=pulse_margin*1e9,passes_assumption_screen=not reasons,failed_constraints=';'.join(reasons),
      evidence_status='analytical_assumptions_not_parallel_SPICE_validated')
    if return_cycle:return r,dict(angle_deg=np.degrees(theta),phase_current_a=current,duty_high=duty,high_device_carrier_average_w=ph,low_device_carrier_average_w=pl,hard_pair_energy_uj_per_device=(overlap+cap)*1e6)
    return r
