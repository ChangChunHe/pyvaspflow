#!/usr/bin/env python3
# coding: utf-8

import unittest
from pyvaspflow.io import vasp_input
from pyvaspflow.vasp.prep_vasp import write_incar
class Test_io(unittest.TestCase):

    def test_incar(self):
        incar = vasp_input.Incar()
        incar['EDIFF'] = '1e-7'
        incar['NSW'] = 1000.00
        incar['LCHGCAR'] = 'True'
        self.assertEqual(incar['EDIFF'],1e-7)
        self.assertEqual(incar['NSW'],1000)
        self.assertEqual(incar['LCHGCAR'],True)

    def test_auto_kpoints(self):
        kpoints = vasp_input.Kpoints()
        kpoints.automatic([1,2,3])
        self.assertEqual(kpoints.kpts[0][0],[1,2,3])

    def test_gamma_kpoints(self):
        kpoints = vasp_input.Kpoints()
        kpoints.gamma_automatic([1,1,1],[0.5,0.5,0.5])
        self.assertEqual(kpoints.kpts_shift,[0.5,0.5,0.5])
        self.assertEqual(kpoints.kpts[0],[1,1,1])

    def test_potcar(self):
        pass


if __name__ == '__main__':
    unittest.main()
