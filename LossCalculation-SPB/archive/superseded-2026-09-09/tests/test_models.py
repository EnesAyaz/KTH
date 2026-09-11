import json
from pathlib import Path
import unittest
from models.buck import evaluate, validate
from models.thermal import shared_sink

ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((ROOT/'data/inputs/buck_example.json').read_text())
        self.d = json.loads((ROOT/'data/devices/epc2361.json').read_text())

    def test_parallel_tradeoff(self):
        a, b = [evaluate(self.c, self.d, 100000, n) for n in [1, 2]]
        self.assertAlmostEqual(a['conduction_w']/2, b['conduction_w'])
        self.assertAlmostEqual(a['gate_drive_w']*2, b['gate_drive_w'])
        self.assertAlmostEqual(a['coss_w']*2, b['coss_w'])

    def test_power_balance(self):
        r = evaluate(self.c, self.d, 100000, 2)
        terms = sum(r[k] for k in ['conduction_w', 'overlap_w', 'coss_w', 'deadtime_w', 'gate_drive_w'])
        self.assertAlmostEqual(terms, r['total_modeled_loss_w'])
        self.assertAlmostEqual(2*(r['high_side_per_device_w']+r['low_side_per_device_w']), r['fet_loss_w'])

    def test_thermal_hand_calculation(self):
        temperature, required = shared_sink(20, 5, 40, 100, 0.7, 2)
        self.assertAlmostEqual(temperature, 83.5)
        self.assertAlmostEqual(required, 2.825)

    def test_reject_dcm_and_voltage(self):
        self.c['pout_w'] = 1
        self.c['assumed_overshoot_v'] = 100
        r = evaluate(self.c, self.d, 50000, 1)
        self.assertFalse(r['passes_screen'])
        self.assertIn('outside_CCM', r['failed_constraints'])
        self.assertIn('voltage_margin', r['failed_constraints'])

    def test_invalid_topology(self):
        self.c['topology'] = 'boost'
        with self.assertRaises(ValueError):
            validate(self.c, self.d)


if __name__ == '__main__':
    unittest.main()
