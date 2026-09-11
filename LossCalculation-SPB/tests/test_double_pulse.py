import tempfile
from pathlib import Path
import unittest
import numpy as np
from models.double_pulse import read_raw, integrate


class DoublePulseTests(unittest.TestCase):
    def test_integral_with_interpolated_boundaries(self):
        self.assertAlmostEqual(integrate(np.array([0.,1.,2.]),np.array([0.,2.,4.]),.25,1.75),3.)

    def test_windows_ascii_raw(self):
        text='Title: test\r\nVariables:\r\n0 time time\r\n1 V(d) voltage\r\nValues:\r\n0 0\r\n3\r\n1 1e-9\r\n4\r\n'
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.raw';path.write_bytes(text.encode())
            result=read_raw(path)
        np.testing.assert_allclose(result['v(d)'],[3,4])
        np.testing.assert_allclose(result['time'],[0,1e-9])
