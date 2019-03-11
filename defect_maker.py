#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 15:22:33 2019

@author: hecc
"""

import numpy as np
from sagar.crystal.derive import ConfigurationGenerator
from sagar.io.vasp import read_vasp, write_vasp
from sagar.crystal.structure import symbol2number as s2n
import os
import shutil
from function_toolkit import generate_all_basis
from itertools import combinations
class DefectMaker:
    def __init__(self, no_defect='POSCAR'):
        # 初始化用 POSCAR路径？
        self.no_defect_cell = read_vasp(no_defect)
        self.lattice = self.no_defect_cell.lattice
        self.positions = self.no_defect_cell.positions
        self.atoms = self.no_defect_cell.atoms


    def extend(self, h):
        if isinstance(h, int):
            self.no_defect_cell = self.no_defect_cell.extend(np.array([[h,0,0],[0,h,0],[0,0,h]]))
        else:
            self.no_defect_cell = self.no_defect_cell.extend(np.asarray(h))
        self.lattice = self.no_defect_cell.lattice
        self.positions = self.no_defect_cell.positions
        self.atoms = self.no_defect_cell.atoms
        print('Warning: this operation will change your cell, \n',
        'and the lattice has been changed to be:\n', self.lattice)


    def get_tetrahedral_defect(self, isunique=True):
        all_basis = generate_all_basis(1,1,1)
        direct_lattice = np.array([[1,0,0],[0,1,0],[0,0,1]])
        extend_S = np.zeros((0,3))
        for basis in all_basis:
            new_basis = np.sum([(direct_lattice[ii]*basis[ii]).tolist() for ii in range(3)],axis=0)
            extend_S = np.vstack((extend_S,
            self.positions+np.tile(new_basis,len(self.atoms)).reshape((-1,3))))
        idx = np.sum((extend_S <= 1.2) &(extend_S >= -0.2),axis=1)
        idx = np.where(idx == 3)[0]
        extend_S = np.dot(extend_S[idx],self.lattice)
        n = extend_S.shape[0]
        d = np.zeros((n,n))
        for ii in range(n):
            d[ii,ii+1:] = np.linalg.norm(extend_S[ii]-extend_S[ii+1:],axis=1)
        d = d + d.T
        first_tetra,sec_tetra,third_tetra = [],[],[]
        for ii in range(n):
            temp_d = sorted(d[ii])
            idx = np.where(abs(temp_d - temp_d[1])<1.5)[0]
            if len(idx) < 3:
                continue
            for comb in combinations(idx,3):
                pass






    def get_purity_defect(self, symprec=1e-3,isunique=True,defect_atom='all',style='Vacc'):
        cg = ConfigurationGenerator(self.no_defect_cell, symprec)
        sites = _get_sites(list(self.atoms), l_sub=defect_atom, purity_atom=style)
        if defect_atom == 'all':
            confs = cg.cons_specific_cell(sites, e_num=(len(self.atoms)-1,1), symprec=symprec)
        else:
            defect_atom_num = np.where(self.atoms==s2n(defect_atom))[0].size
            confs = cg.cons_specific_cell(sites, e_num=(defect_atom_num-1,1), symprec=symprec)
        folder = style + 'defect'
        if not os.path.exists('./'+folder):
            os.mkdir('./'+folder)
        else:
            shutil.rmtree('./'+folder)
            os.mkdir('./'+folder)
        comment = 'POSCAR-'+defect_atom+'-defect'
        idx = 0
        for c, _ in confs:
            filename = '{:s}_id{:d}'.format(comment, idx)
            file = os.path.join('./'+folder, filename)
            write_vasp(c, file)
            idx += 1

def _get_sites(atoms, l_sub='all', purity_atom='Vacc'):
    if l_sub == 'all':
        return [(i, s2n(purity_atom)) for i in atoms]
    else:
        return [(i, s2n(purity_atom)) if i == s2n(l_sub) else (i,) for i in atoms]





if __name__ == "__main__":
    DM = DefectMaker('/home/hecc/Documents/python-package/Defect-Formation-Calculation/test_defect_maker/Fe16Y8.vasp')
    DM.get_tetrahedral_defect()
