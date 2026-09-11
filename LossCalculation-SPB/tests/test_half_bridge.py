import json,unittest
from pathlib import Path
import numpy as np
from models.half_bridge import evaluate,cycle,validate
ROOT=Path(__file__).resolve().parents[1]
class HalfBridgeTests(unittest.TestCase):
 def setUp(self):
  self.c=json.loads((ROOT/'data/inputs/design.json').read_text(encoding='utf-8-sig'));self.d=json.loads((ROOT/'data/devices/epc2361.json').read_text());self.m=self.c['modulations'][0]
 def test_conduction_integral(self):
  self.c['deadtime_ns']=0
  for mode in self.c['modulations']:
   r=evaluate(self.c,self.d,mode,100000,6)
   self.assertAlmostEqual(r['halfbridge_conduction_w'],r['phase_current_rms_a']**2*.001*1.65/6,places=9)
 def test_energy_balance(self):
  r=evaluate(self.c,self.d,self.m,100000,6)
  total=sum(r[k] for k in ('halfbridge_conduction_w','halfbridge_overlap_w','halfbridge_coss_w','halfbridge_deadtime_w'))
  self.assertAlmostEqual(total,r['halfbridge_fet_w']);self.assertAlmostEqual(6*(r['high_device_average_w']+r['low_device_average_w']),total)
 def test_tim_and_thermal_boundary(self):
  r=evaluate(self.c,self.d,self.m,100000,6)
  self.assertAlmostEqual(r['tim_k_w_per_device'],.0005/(17.8*15e-6))
  self.c['coldplate_k_w_per_halfbridge']=r['max_coldplate_k_w_per_halfbridge']
  self.assertAlmostEqual(evaluate(self.c,self.d,self.m,100000,6)['junction_c'],125)
 def test_duty_and_current(self):
  for mode in self.c['modulations']:
   _,d,i,irms=cycle(self.c,mode)
   self.assertTrue(np.all((d>=0)&(d<=1)));self.assertAlmostEqual(np.mean(i*i),irms**2);self.assertAlmostEqual(np.mean(d),.5)
 def test_spwm_limit(self):
  self.c['modulations']=[{'method':'SPWM','m':1.15}]
  with self.assertRaises(ValueError):validate(self.c,self.d)
 def test_quadrature(self):
  a=evaluate(self.c,self.d,self.m,100000,6);self.c['angle_samples']*=2;b=evaluate(self.c,self.d,self.m,100000,6)
  self.assertLess(abs(a['halfbridge_total_w']/b['halfbridge_total_w']-1),1e-6)
 def test_scaling(self):
  a=evaluate(self.c,self.d,self.m,100000,4);b=evaluate(self.c,self.d,self.m,100000,6)
  self.assertAlmostEqual(a['halfbridge_conduction_w']/b['halfbridge_conduction_w'],1.5)
  self.c['power_factor']=.8;q=evaluate(self.c,self.d,self.m,100000,6)
  self.assertAlmostEqual(q['phase_current_rms_a']/b['phase_current_rms_a'],1.25)
 def test_timing_and_budget(self):
  r=evaluate(self.c,self.d,self.m,100000,6);self.assertIn('minimum_pulse',r['failed_constraints']);self.assertAlmostEqual(r['loss_budget_w_per_halfbridge'],31.4070351759)
  self.c['other_loss_w_three_phase']=100;self.assertIn('efficiency',evaluate(self.c,self.d,self.m,100000,6)['failed_constraints'])
