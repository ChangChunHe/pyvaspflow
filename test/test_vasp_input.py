#!/usr/bin/env python3
# coding: utf-8

import unittest
from pydefcal.io import vasp_input
from pydefcal.vasp.prep_vasp import write_incar
class Test_io(unittest.TestCase):

    def test_incar(self):
        incar = vasp_input.Incar()
        incar['EDIFF'] = '1e-7'
        incar['NSW'] = 1000.00
        incar['LCHGCAR'] = 'True'
        self.assertEqual(incar['EDIFF'],1e-7)
        self.assertEqual(incar['NSW'],1000)
        self.assertEqual(incar['LCHGCAR'],True)

    def test_kpoints(self):
        pass

    def test_potcar(self):
        pass


if __name__ == '__main__':
    unittest.main()
