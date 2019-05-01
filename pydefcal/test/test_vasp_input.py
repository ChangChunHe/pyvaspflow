#!/usr/bin/env python3
# coding: utf-8

import unittest
from pydefcal.vasp_io import vasp_input
class TestVasp_io(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()