#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 15:22:33 2019

@author: hecc
"""

import numpy as np
from sagar.crystal.derive import ConfigurationGenerator
from sagar.io.vasp import read_vasp,_read_string
from sagar.crystal.structure import symbol2number as s2n
from pydefcal.utils import generate_all_basis, refine_points,wirite_poscar
from itertools import combinations
from sagar.crystal.structure import Cell
import os
from shutil import rmtree


class DefectMaker:
    def __init__(self, no_defect='POSCAR',no_defect_string=''):
        # 初始化用 POSCAR路径？
        if no_defect_string :
            self.no_defect_cell = _read_string(no_defect_string)
        else:
            self.no_defect_cell = read_vasp(no_defect)
        self.lattice = self.no_defect_cell.lattice
        self.positions = self.no_defect_cell.positions
        self.atoms = self.no_defect_cell.atoms


    def extend(self, h):
        if isinstance(h, int):
            self.no_defect_cell = self.no_defect_cell.extend(np.array([[h,0,0],[0,h,0],[0,0,h]]))
        else:
            self.no_defect_cell = self.no_defect_cell.extend(np.array(h))
        self.lattice = self.no_defect_cell.lattice
        self.positions = self.no_defect_cell.positions
        self.atoms = self.no_defect_cell.atoms
        print('Warning: this operation will change your cell, \n',
        'and the lattice has been changed to be:\n', self.lattice)


    def get_tetrahedral_defect(self, isunique=True, purity_in='H',min_d=1,folder='tetrahedral-defect'):
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
            idx = np.where(abs(d[ii] - temp_d[1])<1.5)[0]
            if len(idx) < 3:
                continue
            for comb in combinations(idx,3):
                comb_list = list(comb)
                tmp = d[comb_list][:,comb_list]
                comb_list.append(ii)
                if np.std(tmp[tmp>0]) < 0.001:
                    if abs(tmp[0,1]-temp_d[1]) < 0.1:
                        first_tetra.append(comb_list)
                    else:
                        sec_tetra.append(comb_list)
                else:
                    tmp = d[comb_list][:,comb_list]
                    tmp = np.triu(tmp)
                    tmp = sorted(tmp[tmp>0])
                    if (np.std(tmp[0:4]) < 0.01 or np.std(tmp[1:5]) <
                     0.01 or np.std(tmp[2:])<0.01) and np.std(tmp) < 0.5:
                        third_tetra.append(comb_list)
        all_tetra = []
        if len(first_tetra) != 0:
            first_tetra = np.unique(np.sort(first_tetra,axis=1),axis=0)
            first_tetra = refine_points(first_tetra,extend_S,self.lattice,min_d=min_d)
            all_tetra.append(first_tetra)
        if len(sec_tetra) !=0:
            sec_tetra = np.unique(np.sort(sec_tetra,axis=1),axis=0)
            sec_tetra = refine_points(sec_tetra,extend_S,self.lattice,min_d=min_d)
            all_tetra.append(sec_tetra)
        if len(third_tetra) != 0:
            third_tetra = np.unique(np.sort(third_tetra,axis=1),axis=0)
            third_tetra = refine_points(third_tetra,extend_S,self.lattice,min_d=min_d)
            all_tetra.append(third_tetra)
        if isunique:
            if not os.path.exists(folder):
                os.mkdir(folder)
            else:
                rmtree(folder)
                os.mkdir(folder)
            idx = 0
            # deg = []
            for tetra in all_tetra:
                if len(tetra) == 0:
                    continue
                new_pos = np.vstack((self.positions,tetra))
                new_atoms = np.hstack((self.atoms,s2n(purity_in)*np.ones((tetra.shape[0],))))
                new_cell = Cell(self.lattice,new_pos,new_atoms)
                equi_atoms = new_cell.get_symmetry()['equivalent_atoms']
                purity_atom_type = np.unique(equi_atoms[-tetra.shape[0]:])
                for atom_type in purity_atom_type:
                    new_uniq_pos = np.vstack((self.positions,new_pos[atom_type]))
                    new_uniq_atoms = np.hstack((self.atoms,s2n(purity_in)*np.ones((1,))))
                    new_uniq_cell = Cell(self.lattice,new_uniq_pos,new_uniq_atoms)
                    # deg.append(len(np.where(equi_atoms == atom_type)[0]))
                    wirite_poscar(new_uniq_cell,purity_in,folder,idx)
                    idx += 1
            # np.savetxt(folder+'/deg.txt',deg,fmt='%d')
        else:
            if not os.path.exists(folder):
                os.mkdir(+folder)
            else:
                rmtree(folder)
                os.mkdir(folder)
            idx = 0
            for tetra in all_tetra:
                if len(tetra) == 0:
                    continue
                new_pos = np.vstack((self.positions,tetra))
                new_atoms = np.hstack((self.atoms,s2n(purity_in)*np.ones((tetra.shape[0],))))
                new_cell = Cell(self.lattice,new_pos,new_atoms)
                wirite_poscar(new_cell,purity_in,folder,idx)
                idx += 1


    def get_purity_defect(self,symprec=1e-3,purity_out='all',purity_in='Vacc',num=1):
        cg = ConfigurationGenerator(self.no_defect_cell, symprec)
        sites = _get_sites(list(self.atoms), purity_out=purity_out, purity_in=purity_in)
        if purity_out == 'all':
            confs = cg.cons_specific_cell(sites, e_num=(len(self.atoms)-num, num), symprec=symprec)
        else:
            purity_atom_num = np.where(self.atoms==s2n(purity_out))[0].size
            confs = cg.cons_specific_cell(sites, e_num=(purity_atom_num-num, num), symprec=symprec)
        folder = purity_out + '-' + purity_in + '-defect'
        if not os.path.exists('./'+folder):
            os.mkdir('./'+folder)
        else:
            rmtree('./'+folder)
            os.mkdir('./'+folder)
        idx = 0
        for c, _ in confs:
            wirite_poscar(c,purity_out+'-'+purity_in,folder,idx)
            idx += 1


def _get_sites(atoms, purity_out='all', purity_in='Vacc'):
    if purity_out == 'all':
        return [(i, s2n(purity_in)) for i in atoms]
    else:
        return [(i, s2n(purity_in)) if i == s2n(purity_out) else (i,) for i in atoms]

# charge_state = {'Vacc': 0,
#                'H': 1, 'He': 0,
#                'Li': 1, 'Be': 2, 'B': 3, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'Ne': 0,
#                'Na': 1, 'Mg': 2, 'Al': 3, 'Si': 4, 'P': 5, 'S': 6, 'Cl': 7, 'Ar': 0,
#                'K': 1, 'Ca': 2, 'Sc': 3, 'Ti': 4, 'V': 5, 'Cr': 2, 'Mn': 2, 'Fe': 2, 'Co': 2, 'Ni': 2, 'Cu': 1, 'Zn': 2, 'Ga': 3, 'Ge': 4, 'As': 5, 'Se': 6, 'Br': 7, 'Kr': 0,
#                'Rb': 1, 'Sr': 2, 'Y': 3, 'Zr': 4, 'Nb': 3, 'Mo': 3, 'Tc': 6, 'Ru': 3, 'Rh': 4, 'Pd': 2, 'Ag': 1, 'Cd': 2, 'In': 3, 'Sn': 4, 'Sb': 5, 'Te': 6, 'I': 7, 'Xe': 0,
#                'Cs': 1, 'Ba': 2, 'Hf': 4, 'Ta': 5, 'W': 6, 'Re': 2, 'Os': 3, 'Ir': 3, 'Pt': 2, 'Au': 1, 'Hg': 1, 'Tl': 1, 'Pb': 2, 'Bi': 3, 'Po': 2, 'At': 0, 'Rn': 0,
#                'Fr': 1, 'Ra': 2}
