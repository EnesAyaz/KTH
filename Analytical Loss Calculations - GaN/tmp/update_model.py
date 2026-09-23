from pathlib import Path
p=Path('epc2361_loss.py')
s=p.read_text()
s=s.replace('from math import sqrt','from math import sqrt, pi, isfinite')
s=s.replace('ac_rms: float = 220.0','ac_rms: float = 40.0')
s=s.replace('vgs_threshold: float = 1.5','vgs_threshold: float = 1.1').replace('vgs_plateau: float = 3.0','vgs_plateau: float = 2.1')
s=s.replace('qgs1_nc: float = 8.5','qgs1_nc: float = 6.0  # legacy name: charge to threshold').replace('qgsth_nc: float = 0.0','qgsth_nc: float = 6.0')
s=s.replace('qg_nc: float = 30.0','qg_nc: float = 28.0').replace('qgs2_nc: float = 12.0','qgs2_nc: float = 2.5  # QGS - QG(th) = 8.5 - 6')
s=s.replace('    rg_on: float', '    rg_internal: float = 0.4\n    waveform_current_a: float = 0.0  # 0 selects sinusoidal peak; independent DPT current\n    rg_on: float')
s=s.replace('rtheta_ja_c_w: float = 20.0','rtheta_ja_c_w: float = 44.0  # JEDEC board; EVB is 25 C/W')
s=s.replace('coss_nf: float = 2.0','coss_nf: float = 0.9  # small-signal estimate at 75 V; ringing only')
s=s.replace('eoss_uj: float = 0.0','eoss_uj: float = 3.2  # approximate Figure 6 value at 75 V')
s=s.replace('qoss_nc: float = 100.0','qoss_nc: float = 114.0  # approximate Figure 6 value at 75 V').replace('qoss_voltage: float = 50.0','qoss_voltage: float = 75.0')
s=s.replace('vsd: float = 1.6','vsd: float = 2.2  # approximate Figure 8 at operating current')
a=s.index('    # Gate current'); b=s.index('    di_dt_on =',a)
s=s[:a]+'''    # AN030 Figures 4/5: gate current depends on the gate-voltage segment.
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
    # AN030 Eq.16: equal-device half-bridge capacitor loss is V*Qoss*f.
    # Eoss is reported for reference, not added again. Qoss must be at VBUS.
    eoss = i.eoss_uj * 1e-6
    pcoss = i.vbus * i.qoss_nc * 1e-9 * i.fsw if i.hard_switching else 0.0
    pgate = 2.0 * i.qg_nc * 1e-9 * i.vgs * i.fsw
    dead_fraction = 2 * i.effective_dead_time_ns * 1e-9 * i.fsw
    pcond *= 1 - dead_fraction
    pdead = mean_current * i.vsd * dead_fraction
'''+s[b:]
s=s.replace('di_dt_on = peak / tcr','di_dt_on = waveform_current / tcr').replace('di_dt_off = peak / tcf','di_dt_off = waveform_current / tcf')
s=s.replace('    p_device = total / (2.0 * n)','    semiconductor_loss = pcond + poverlap + pcoss + pdead\n    p_device = semiconductor_loss / 2.0  # symmetrical line-cycle average, external losses excluded')
s=s.replace('100.0 * max(0.0, output_power - total) / output_power','100.0 * output_power / (output_power + total)')
s=s.replace('    output = dict(conduction=pcond,','    output = dict(waveform_current_a=waveform_current, mean_abs_current_a=mean_current,\n                  semiconductor_loss=semiconductor_loss, loss_per_device=p_device,\n                  threshold_time_on_ns=tgs1_on*1e9, threshold_time_off_ns=tgs1_off*1e9,\n                  post_time_on_ns=tpost_on*1e9, post_time_off_ns=tpost_off*1e9,\n                  voltage_rating_exceeded=i.vbus + overshoot > 100,\n                  conduction=pcond,')
s=s.replace('    _validate(i)','    _validate(i)',1)
a=s.index('    positive =',s.index('def _validate'))
s=s[:a]+'''    for name, value in asdict(i).items():
        if isinstance(value, (int, float)) and not isfinite(value):
            raise ValueError(f"{name} must be finite")
    if i.devices_parallel != 1:
        raise ValueError("This model uses one device per switch position")
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
    if 2*i.dead_time_ns*1e-9*i.fsw >= 1:
        raise ValueError("Two dead times must fit inside one switching period")
    if i.rds25_mohm <= 0 or i.rds_max_mohm <= 0:
        raise ValueError("On-resistances must be positive")
'''+s[a:]
s=s.replace('for name in ("qgsth_nc",','for name in ("rg_internal", "waveform_current_a", "qgsth_nc",')
p.write_text(s,encoding='utf-8')
p=Path('loss_calculator.py'); s=p.read_text()
s=s.replace('("Parallel devices / switch", "devices_parallel"), ', '')
s=s.replace('    ("RG on (ohm)",', '    ("VGS threshold (V)", "vgs_threshold"), ("VGS plateau (V)", "vgs_plateau"),\n    ("QG(th) (nC)", "qgsth_nc"), ("Internal RG (ohm)", "rg_internal"),\n    ("RG on (ohm)",')
s=s.replace('("Measured EOSS (uJ, 0=estimate)", "eoss_uj")','("EOSS at VBUS (uJ, reference)", "eoss_uj")')
s=s.replace('            values["devices_parallel"] = int(values["devices_parallel"])\n','')
# Fit controls into two columns instead of an unusably tall window.
s=s.replace('        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w")','        column, display_row = 2 * (row // 21), row % 21\n        ttk.Label(frame, text=label).grid(row=display_row, column=column, sticky="w")')
s=s.replace('grid(row=row, column=1)','grid(row=display_row, column=column+1)')
s=s.replace('column=3, rowspan=len(FIELDS)','column=4, rowspan=21').replace('width=58, height=16','width=58, height=30')
s=s.replace('row=len(FIELDS), column=0, columnspan=2','row=22, column=0, columnspan=4')
p.write_text(s,encoding='utf-8')
