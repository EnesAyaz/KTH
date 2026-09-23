"""Numerical regression checks for the analytical model and waveform integration."""
import unittest
from dataclasses import replace
import numpy as np
from epc2361_loss import LossInputs, calculate
from waveform_plotter import build_waveforms, _parse_inputs

class LossModelTests(unittest.TestCase):
    def test_default_components(self):
        i = LossInputs(); r = calculate(i)
        self.assertEqual((i.vbus, i.ac_rms, i.devices_parallel), (75, 40, 1))
        self.assertAlmostEqual(r['conduction'], 40**2 * r['rds_on_ohm'] * .99)
        self.assertAlmostEqual(r['coss_eoss'], 75 * 114e-9 * 100e3)
        self.assertAlmostEqual(r['efficiency'], 100*r['output_power']/(r['output_power']+r['total_loss']))
        self.assertTrue(r['voltage_rating_exceeded'])

    def test_waveform_energy_and_endpoints(self):
        i=LossInputs(); r=calculate(i)
        t, von, ion, gon, voff, ioff, goff=build_waveforms(i,r)
        integrate = getattr(np,'trapezoid', None) or np.trapz
        self.assertAlmostEqual(integrate(von*ion,t),r['eon_overlap_j'],places=12)
        self.assertAlmostEqual(integrate(voff*ioff,t),r['eoff_overlap_j'],places=12)
        self.assertEqual((gon[0], gon[-1], goff[0], goff[-1]), (0,5,5,0))
        self.assertAlmostEqual(r['switching_overlap'],(r['eon_overlap_j']+r['eoff_overlap_j'])*i.fsw*2/np.pi)

    def test_external_loss_not_in_junction(self):
        a=calculate(LossInputs()); b=calculate(LossInputs(optional_loop_r_mohm=2))
        self.assertEqual(a['junction_temperature'],b['junction_temperature'])
        self.assertGreater(b['total_loss'],a['total_loss'])

    def test_plot_current_independent_of_rms_loss(self):
        a=calculate(LossInputs()); b=calculate(LossInputs(waveform_current_a=40))
        self.assertEqual(a['total_loss'],b['total_loss'])
        self.assertEqual(b['waveform_current_a'],40)
        self.assertLess(b['eon_overlap_j'],a['eon_overlap_j'])

    def test_invalid_inputs(self):
        for change in ({'driver_source_a':0}, {'ac_rms':float('nan')},
                       {'devices_parallel':2}, {'qg_nc':3}, {'modulation':'dc'},
                       {'qoss_voltage':50}, {'effective_dead_time_ns':6000}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                calculate(replace(LossInputs(),**change))
        calculate(LossInputs(effective_dead_time_ns=60))

    def test_zero_post_charge_and_zero_inductance(self):
        i=LossInputs(qg_nc=12.5, loop_inductance_nh=0)
        with np.errstate(all='raise'):
            waves=build_waveforms(i,calculate(i),include_ringing=True)
        self.assertTrue(all(np.isfinite(w).all() for w in waves))

    def test_gui_inputs_are_not_overwritten(self):
        class Field:
            def __init__(self,v): self.v=str(v)
            def get(self): return self.v
        i=_parse_inputs({k:Field(v) for k,v in {'qg_nc':31,'qgsth_nc':5,'vgs_threshold':1.2,'vgs_plateau':2.3,'coss_nf':1.1}.items()})
        self.assertEqual((i.qg_nc,i.qgsth_nc,i.vgs_threshold,i.vgs_plateau,i.coss_nf),(31,5,1.2,2.3,1.1))

    def test_thermal_fixed_point_and_feedback(self):
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
        self.assertAlmostEqual(r['junction_temperature'],expected,delta=1e-6)

    def test_manual_mode_and_unsupported_temperature(self):
        r=calculate(LossInputs(rds_temperature_mode='manual'))
        self.assertAlmostEqual(r['rds_on_mohm'],1.7)
        self.assertEqual(r['thermal_iterations'],0)
        for i in (LossInputs(case_c=-1),LossInputs(case_c=150),
                  LossInputs(thermal_mode='ambient',rtheta_ja_c_w=100)):
            with self.assertRaisesRegex(ValueError,'outside the supported RDS curve'):
                calculate(i)

if __name__=='__main__': unittest.main()
