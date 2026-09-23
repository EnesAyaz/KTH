from pathlib import Path
p=Path('epc2361_loss.py'); s=p.read_text(encoding='utf-8')
s=s.replace('    rds_temp_scale: float = 1.7','    rds_temp_scale: float = 1.7  # used only in manual mode\n    rds_temperature_mode: str = "iterative"  # iterative or manual')
a=s.index('\ndef calculate(')
s=s[:a]+'''
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

'''+s[a:]
a=s.index('    rds = (rds_base / 1000.0)'); b=s.index('    ploop_r =',a)
s=s[:a]+s[b:]
s=s.replace('    pcond *= 1 - dead_fraction\n','')
s=s.replace('    pdead = mean_current * i.vsd * dead_fraction','''    pdead = mean_current * i.vsd * dead_fraction
    conduction_coefficient = 2 * isw_rms**2 * (1-dead_fraction)
    rds, junction, thermal_iterations, thermal_residual, temperature_scale = solve_thermal(
        i, rds_base/1000, conduction_coefficient, poverlap + pcoss + pdead)
    pcond = conduction_coefficient * rds''')
a=s.index('    junction = (i.case_c');b=s.index('    output_voltage_rms',a);s=s[:a]+s[b:]
s=s.replace('    output = dict(waveform_current_a=', '''    output = dict(rds_on_mohm=rds*1000, rds_temperature_factor=temperature_scale,
                  thermal_iterations=thermal_iterations, thermal_residual_c=thermal_residual,
                  thermal_iteration_enabled=i.rds_temperature_mode == "iterative",
                  junction_rating_exceeded=junction > 150,
                  waveform_current_a=''')
s=s.replace('    if i.modulation !=', '    if i.rds_temperature_mode not in ("iterative", "manual"):\n        raise ValueError("rds_temperature_mode must be iterative or manual")\n    if i.modulation !=')
p.write_text(s,encoding='utf-8')
p=Path('loss_calculator.py'); s=p.read_text(encoding='utf-8')
s=s.replace('    ("RDS temperature scale", "rds_temp_scale"),','    ("RDS mode (iterative/manual)", "rds_temperature_mode"),\n    ("RDS scale (manual mode only)", "rds_temp_scale"),')
s=s.replace('row // 21), row % 21','row // 22), row % 22').replace('rowspan=21','rowspan=22').replace('row=22, column=0','row=23, column=0')
s=s.replace('{"modulation", "thermal_mode"}', '{"modulation", "thermal_mode", "rds_temperature_mode"}')
s=s.replace('if k in text_fields: values[k] = v.get()', 'if k in text_fields: values[k] = raw')
s=s.replace('            for k, v in result.items():', '''            output.insert("end", f"Junction temperature: {result['junction_temperature']:.3f} C\\n"
                          f"Updated RDS(on): {result['rds_on_mohm']:.4f} mOhm\\n"
                          f"Thermal iterations: {result['thermal_iterations']}\\n\\n")
            for k, v in result.items():''')
p.write_text(s,encoding='utf-8')
p=Path('waveform_plotter.py'); s=p.read_text(encoding='utf-8').replace('f"One EPC2361 per switch position\\n"','f"One EPC2361 per switch position\\n"\n                f"Tj / RDS(on): {result[\'junction_temperature\']:.2f} C / "\n                f"{result[\'rds_on_mohm\']:.4f} mOhm\\n"');p.write_text(s,encoding='utf-8')
p=Path('test_loss_model.py'); s=p.read_text(encoding='utf-8-sig').replace("40**2 * .0017 * .99", "40**2 * r['rds_on_ohm'] * .99")
s=s.replace("if __name__=='__main__':", '''    def test_thermal_fixed_point_and_feedback(self):
        from epc2361_loss import rds_temperature_factor
        for i in (LossInputs(), LossInputs(case_c=100),
                  LossInputs(thermal_mode='ambient', rtheta_ja_c_w=25)):
            r=calculate(i)
            reference=i.case_c if i.thermal_mode=='case' else i.ambient_c
            theta=i.rtheta_jc_c_w if i.thermal_mode=='case' else i.rtheta_ja_c_w
            self.assertLess(abs(r['junction_temperature']-reference-theta*r['loss_per_device']),1e-6)
            self.assertAlmostEqual(r['rds_on_mohm'],r['rds_base_mohm']*rds_temperature_factor(r['junction_temperature']))
            self.assertGreater(r['thermal_iterations'],0)
        cool=calculate(LossInputs()); hot=calculate(LossInputs(case_c=100))
        self.assertGreater(hot['conduction'],cool['conduction'])
        self.assertGreater(hot['rds_on_mohm'],cool['rds_on_mohm'])

    def test_thermal_solver_against_closed_form(self):
        # Default fixed point lies on the 50..75 C linear curve segment.
        i=LossInputs(); r=calculate(i)
        slope=(1.33-1.16)/25
        coefficient=40**2*.99*.001
        fixed=r['switching_overlap']+r['coss_eoss']+r['dead_time_reverse_conduction']
        expected=(50+.1*(coefficient*(1.16-slope*50)+fixed))/(1-.1*coefficient*slope)
        self.assertAlmostEqual(r['junction_temperature'],expected,places=6)

    def test_manual_mode_and_unsupported_temperature(self):
        r=calculate(LossInputs(rds_temperature_mode='manual'))
        self.assertAlmostEqual(r['rds_on_mohm'],1.7)
        self.assertEqual(r['thermal_iterations'],0)
        for i in (LossInputs(case_c=-1),LossInputs(case_c=150),
                  LossInputs(thermal_mode='ambient',rtheta_ja_c_w=100)):
            with self.assertRaisesRegex(ValueError,'outside the supported RDS curve'):
                calculate(i)

if __name__=='__main__':''')
p.write_text(s,encoding='utf-8')
