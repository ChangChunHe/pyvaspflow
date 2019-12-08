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
from sagar.molecule.derive import ConfigurationGenerator as mole_CG
from sagar.molecule.structure import Molecule
from pyvaspflow.utils import generate_all_basis, refine_points,write_poscar
from itertools import combinations,chain
from sagar.crystal.structure import Cell
from shutil import rmtree
import os


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


    def get_tetrahedral_defect(self, isunique=False, doped_in='H',min_d=1.5,folder='tetrahedral-defect'):
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
            idx = np.where(abs(d[ii] - temp_d[1])<min_d)[0]
            if len(idx) < 3:
                continue
            for comb in combinations(idx,3):
                comb_list = list(comb)
                tmp = d[comb_list][:,comb_list]
                comb_list.append(ii)
                if np.std(tmp[tmp>0]) < 0.01:
                    if abs(tmp[0,1]-temp_d[1]) < 0.1:
                        first_tetra.append(comb_list)
                    else:
                        sec_tetra.append(comb_list)
                else:
                    tmp = d[comb_list][:,comb_list]
                    tmp = np.triu(tmp)
                    tmp = sorted(tmp[tmp>0])
                    if (np.std(tmp[0:4]) < 0.2 or np.std(tmp[1:5]) < 0.2 or
                    np.std(tmp[2:]) < 0.2) and np.std(tmp) < 0.5:
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
                new_atoms = np.hstack((self.atoms,s2n(doped_in)*np.ones((tetra.shape[0],))))
                new_cell = Cell(self.lattice,new_pos,new_atoms)
                equi_atoms = new_cell.get_symmetry()['equivalent_atoms']
                purity_atom_type = np.unique(equi_atoms[-tetra.shape[0]:])
                for atom_type in purity_atom_type:
                    new_uniq_pos = np.vstack((self.positions,new_pos[atom_type]))
                    new_uniq_atoms = np.hstack((self.atoms,s2n(doped_in)*np.ones((1,))))
                    new_uniq_cell = Cell(self.lattice,new_uniq_pos,new_uniq_atoms)
                    # deg.append(len(np.where(equi_atoms == atom_type)[0]))
                    write_poscar(new_uniq_cell,folder,idx)
                    idx += 1
            # np.savetxt(folder+'/deg.txt',deg,fmt='%d')
        else:
            if not os.path.exists(folder):
                os.mkdir(folder)
            else:
                rmtree(folder)
                os.mkdir(folder)
            idx = 0
            for tetra in all_tetra:
                if len(tetra) == 0:
                    continue
                new_pos = np.vstack((self.positions,tetra))
                new_atoms = np.hstack((self.atoms,s2n(doped_in)*np.ones((tetra.shape[0],))))
                new_cell = Cell(self.lattice,new_pos,new_atoms)
                write_poscar(new_cell,folder,idx)
                idx += 1


    def get_point_defect(self,symprec=1e-3,doped_out='all',doped_in=['Vac'],num=[1],ip=""):
        cell = self.no_defect_cell
        cg = ConfigurationGenerator(cell, symprec)
        sites = _get_sites(list(cell.atoms), doped_out=doped_out, doped_in=doped_in)
        if num == None:
            confs = cg.cons_specific_cell(sites, e_num=None, symprec=symprec)
            comment = ["-".join(doped_in)+"-all_concentration"]
        else:
            purity_atom_num = sum([1 if len(site)>1 else 0 for site in sites])
            confs = cg.cons_specific_cell(sites, e_num=[purity_atom_num-sum(num)]+num, symprec=symprec)
            comment = list(chain(*zip(doped_in, [str(i) for i in num])))
        comment = '-'.join(doped_out) +'-'+'-'.join(comment) + '-defect'
        folder = comment
        if not os.path.isdir(folder):
            os.makedirs(folder)
        deg = []
        idx = 0
        for c, _deg in confs:
            write_poscar(c,folder,idx)
            deg.append(_deg)
            idx += 1
        np.savetxt(os.path.join(folder,"deg.txt"),deg,fmt='%d')


    def get_mole_point_defect(self,symprec=1e-3,doped_out='all',doped_in=['Vac'],num=[1]):
        pos,lat,atoms = self.positions,self.lattice,self.atoms
        mole = Molecule(np.dot(pos,lat),atoms)
        cg = mole_CG(mole, symprec)
        sites = _get_sites(list(mole.atoms), doped_out=doped_out, doped_in=doped_in)
        if num == None:
            confs = cg.get_configurations(sites, e_num=None)
            comment = ["-".join(doped_in)+"-all_concentration"]
        else:
            purity_atom_num = sum([1 if len(site)>1 else 0 for site in sites])
            confs = cg.get_configurations(sites, e_num=[purity_atom_num-sum(num)]+num)
            comment = list(chain(*zip(doped_in, [str(i) for i in num])))
        folder = '-'.join(doped_out) +'-'+'-'.join(comment) + '-defect'
        if not os.path.exists('./'+folder):
            os.mkdir('./'+folder)
        else:
            rmtree('./'+folder)
            os.mkdir('./'+folder)
        deg = []
        idx = 0
        for c, _deg in confs:
            c.lattice = lat
            c._positions = np.dot(c.positions,np.linalg.inv(lat))
            write_poscar(c,folder,idx)
            deg.append(_deg)
            idx += 1
        np.savetxt(os.path.join(folder,"deg.txt"),deg,fmt='%d')

# def _get_sites(atoms,doped_out,doped_in):
#     doped_in = [s2n(i) for i in doped_in]
#     if doped_out == 'all':
#         return  [tuple([atom]+doped_in)  for atom in atoms]
#     else:
#         doped_out = s2n(doped_out)
#         _ins = tuple([doped_out]+doped_in)
#         return [_ins if atom == doped_out else (atom,) for atom in atoms]

def _get_sites(atoms,doped_out,doped_in):
    doped_in = [s2n(i) for i in doped_in]
    if doped_out == ['all']:
        return  [tuple([atom]+doped_in)  for atom in atoms]
    elif len(doped_out) > 1:
        doped_out = [s2n(i) for i in doped_out]
        return [tuple([atom]+doped_in) if atom in doped_out else (atom,) for atom in atoms ]
    else:
        doped_out = [s2n(i) for i in doped_out]
        _ins = tuple(doped_out+doped_in)
        return [_ins if atom == doped_out else (atom,) for atom in atoms]

if __name__ == '__main__':
    dm = DefectMaker('/home/hecc/Downloads/POSCAR')
    dm.get_mole_point_defect(symprec=0.1,doped_out='C',doped_in=['Vac'],num=[2])
