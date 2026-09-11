import json
import math
from pathlib import Path
import unittest
from models.inverter import evaluate, validate

ROOT = Path(__file__).resolve().parents[1]


class InverterTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((ROOT/'data/inputs/inverter_module.json').read_text())
        self.d = json.loads((ROOT/'data/devices/epc2361.json').read_text())

    def test_rated_current_and_budget(self):
        validate(self.c, self.d)
        r = evaluate(self.c, self.d, 10000, 6)
        self.assertAlmostEqual(r['phase_current_rms_a'], 18750/(3*1.15*75/(2*math.sqrt(2))))
        self.assertAlmostEqual(r['loss_budget_w'], 94.2211055276)
        self.assertEqual(r['total_devices'], 36)

    def test_power_factor(self):
        a = evaluate(self.c, self.d, 10000, 6)
        self.c['power_factor'] = 0.8
        b = evaluate(self.c, self.d, 10000, 6)
        self.assertAlmostEqual(b['phase_current_rms_a']/a['phase_current_rms_a'], 1.25)
        self.assertAlmostEqual(b['conduction_w']/a['conduction_w'], 1.25**2)

    def test_parallel_and_balance(self):
        a, b = [evaluate(self.c, self.d, 10000, n) for n in [3, 6]]
        self.assertAlmostEqual(a['conduction_w']/2, b['conduction_w'])
        self.assertAlmostEqual(a['coss_w']*2, b['coss_w'])
        self.assertAlmostEqual(a['gate_drive_w']*2, b['gate_drive_w'])
        self.assertAlmostEqual(sum(b[k] for k in ['conduction_w','overlap_w','coss_w','deadtime_w','gate_drive_w']), b['total_modeled_loss_w'])

    def test_pulse_limit_near_svm_boundary(self):
        r = evaluate(self.c, self.d, 100000, 6)
        self.assertIn('SVM_minimum_pulse_deadtime', r['failed_constraints'])

    def test_external_losses_consume_budget(self):
        self.c['other_converter_loss_w'] = 100
        r = evaluate(self.c, self.d, 10000, 6)
        self.assertIn('efficiency_target', r['failed_constraints'])

    def test_voltage_change_requires_new_energy(self):
        self.c['vin_v'] = 80
        with self.assertRaises(ValueError):
            validate(self.c, self.d)

    def test_overmodulation_rejected(self):
        self.c['modulation_index'] = 1.2
        with self.assertRaises(ValueError):
            validate(self.c, self.d)
