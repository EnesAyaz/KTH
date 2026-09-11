import unittest
from models.parallel_layout import equivalent_loop_nh


class ParallelLayoutTests(unittest.TestCase):
    def test_single_branch(self):
        self.assertAlmostEqual(equivalent_loop_nh(.6,1.5,.2,1),2.1)

    def test_uncoupled_branches(self):
        self.assertAlmostEqual(equivalent_loop_nh(.6,1.5,0,6),.85)

    def test_fully_coupled_branches_do_not_divide(self):
        self.assertAlmostEqual(equivalent_loop_nh(.6,1.5,1,6),2.1)

    def test_invalid_coupling(self):
        with self.assertRaises(ValueError):
            equivalent_loop_nh(.6,1.5,1.1,6)
