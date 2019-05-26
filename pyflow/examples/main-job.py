#!/usr/bin/env python3
# coding: utf-8

from sagar.io.vasp import read_vasp,write_vasp
from sagar.crystal.structure import Cell
import numpy as np
from pyflow.utils import generate_all_basis
from sagar.crystal.derive import PermutationGroup as PG
from sagar.toolkit.mathtool import is_int_np_array
from itertools import combinations
import os

def get_perms(cell,symprec=1e-3):
    latt = cell.lattice
    pos = cell.positions
    pos = np.dot(pos,latt)
    n = pos.shape[0]
    pcell = cell.get_primitive_cell()
    lat_pcell = pcell.lattice
    mat = np.matmul(latt, np.linalg.inv(lat_pcell))
    if is_int_np_array(mat):
        mat = np.around(mat).astype('intc')
    else:
        print("cell:\n", lat_cell)
        print("primitive cell:\n", lat_pcell)
        raise ValueError(
        "cell lattice and its primitive cell lattice not convertable")
    hfpg = PG(pcell, mat)
    return  hfpg.get_symmetry_perms(symprec)


def get_min_serial(perms,num):
    return np.unique(np.sort(perms[:,num],axis=1),axis=0)[0].tolist()


cell = read_vasp('POSCAR')
perms = get_perms(cell)
latt = cell.lattice
pos = cell.positions
pos = np.dot(pos,latt)
n = pos.shape[0]
basis = generate_all_basis(1,1,0)
extend_pos = np.zeros((9*n,3))
idx = 0
for ii in basis:
    extend_pos[n*idx:n*(idx+1),:] = (pos+ii[0]*latt[0]+ii[1]*latt[1]+ii[2]*latt[2])
    idx += 1

neig_list = np.zeros((n,6))
for ii in range(pos.shape[0]):
    d = np.linalg.norm(pos[ii]-extend_pos,axis=1)
    idx = np.where(abs(d-d[np.argsort(d)[1]])<0.01)[0]
    neig_list[ii] = idx%n

pos = np.dot(pos,np.linalg.inv(latt))
vac_str = [np.array([0])]
for vac in range(2,6):
    last_vac_str = vac_str[-1]
    tmp_vac_str = []
    n_prev = last_vac_str.shape[0]
    for i in range(n_prev):
        each_str = last_vac_str[i]
        idx = np.setdiff1d(np.setdiff1d(range(n),each_str),neig_list[each_str][:])
        for ii in idx:
            tmp_vac_str.append(get_min_serial(perms,np.hstack((each_str,ii))))
    vac_str.append(np.unique(tmp_vac_str,axis=0))
    idx = 0
    os.makedirs('vac-'+str(vac))
    for _str in vac_str[-1]:
        _pos = pos[np.setdiff1d(range(n),_str),:]
        _latt,_atoms = latt,np.ones((n-vac,))*5
        write_vasp(Cell(_latt,_pos,_atoms),'vac-'+str(vac)+'/POSCAR'+str(idx))
        idx += 1
    print(vac_str[-1].shape)
