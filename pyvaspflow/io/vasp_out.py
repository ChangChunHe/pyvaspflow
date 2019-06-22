#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


import linecache as lc
import numpy as np
import os
from sagar.io.vasp import read_vasp
import subprocess


class ExtractValue():
    def __init__(self,data_folder='./',atomic_num=3):

        self.data_folder = data_folder
        self.atomic_num = atomic_num

    def get_energy(self):
        file_osz = os.path.join(self.data_folder,'OSZICAR')
        return float(subprocess.run(['tail','-1',file_osz],stdout=subprocess.PIPE).stdout.decode('utf-8').split()[4])


    def get_fermi(self):
        # read from scf calculation
        file_outcar = os.path.join(self.data_folder,'OUTCAR')
        grep_res = subprocess.Popen(['grep','E-fermi',file_outcar],stdout=subprocess.PIPE)
        return float(subprocess.check_output(['tail','-1'],stdin=grep_res.stdout).decode('utf-8').split()[2])

    def get_Ne_defect_free(self):
        # you can get valance electrons in your defect-free system
        file_pos = os.path.join(self.data_folder, 'POSCAR')
        file_pot = os.path.join(self.data_folder, 'POTCAR')
        ele_num_atom = [float(i) for i in  subprocess.run(['grep','ZVAL',file_pot],stdout=subprocess.PIPE).stdout.decode('utf-8').split()[5::9]]
        atom_num = [float(i) for i in lc.getlines(file_pos)[6].split()]
        return int(np.dot(atom_num,ele_num_atom))

    def get_Ne_defect(self):
        #get all valance electrons number in OUTCAR
        file_outcar = os.path.join(self.data_folder,'OUTCAR')
        grep_res = subprocess.run(['grep','NELECT',file_outcar],stdout=subprocess.PIPE)
        return int(float(grep_res.stdout.decode('utf-8').split()[2]))

    def get_image(self):
        file_image = os.path.join(self.data_folder,'OUTCAR')
        return float(subprocess.run(['grep','Ewald',file_image],stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0].split()[-1])

    def get_cpu_time(self):
        file_outcar = os.path.join(self.data_folder,'OUTCAR')
        with open(file_outcar) as f:
            lines = f.readlines()
        cpu_line = [line for line in lines if 'CPU' in line]
        return  float(cpu_line[0].split()[-1])

    def get_gap(self):
        file_eig = os.path.join(self.data_folder,'EIGENVAL')
        line6 = np.genfromtxt(file_eig,skip_header=5,max_rows=1)
        kpt_num, eig_num = int(line6[1]), int(line6[2])
        if  len(lc.getlines(file_eig)[8].split()) == 3:
            isspin = False
        elif len(lc.getlines(file_eig)[8].split()) == 5:
            isspin = True
        if not isspin:
            all_eigval = np.zeros((eig_num, kpt_num*2))
            for ii in range(kpt_num):
                 all_eigval[:,2*ii:2*ii+2] = np.genfromtxt(file_eig,
                 skip_header=8+eig_num*int(ii)+2*ii,
                 max_rows=eig_num,usecols=(1,2))
        else:
            all_eigval = np.zeros((eig_num, kpt_num*4))
            for ii in range(kpt_num):
                 all_eigval[:,4*ii:4*ii+4] = np.genfromtxt(file_eig,
                 skip_header=8+eig_num*int(ii)+2*ii,
                 max_rows=eig_num,usecols=(1,2,3,4))
        if not isspin:
            elec_num =  np.mean(all_eigval[:,1::2],axis=1)
            idx1 = np.where(elec_num > 0.8)
            idx2 = np.where(elec_num < 0.2)
            if idx1[0][-1] - idx2[0][0] == -1:
                vbm = np.max(all_eigval[idx1[0][-1],::2])
                cbm = np.min(all_eigval[idx2[0][0],::2])
                gap = cbm - vbm
            else:
                print('The gap of this system can not be obtained from this progrmme',
                'I suggest you carefully check the EIGENVAL by yourself')
                return
            return (vbm, cbm, gap)
        else:
            all_eigval_up = all_eigval[:,0::2]
            all_eigval_down = all_eigval[:,1::2]
            elec_num_up = np.mean(all_eigval_up[:,1::2],axis=1)
            idx1 = np.where(elec_num_up > 0.8)
            idx2 = np.where(elec_num_up < 0.2)
            if idx1[0][-1] - idx2[0][0] == -1:
                vbm_up = np.max(all_eigval_up[idx1[0][-1],::2])
                cbm_up = np.min(all_eigval_up[idx2[0][0],::2])
                gap_up = cbm_up - vbm_up
            else:
                print('The gap of this system can not be obtained from this progrmme',
                'I suggest you carefully check the EIGENVAL by yourself')
                return
            elec_num_down =  np.mean(all_eigval_down[:,1::2],axis=1)
            idx1 = np.where(elec_num_down > 0.8)
            idx2 = np.where(elec_num_down < 0.2)
            if idx1[0][-1] - idx2[0][0] == -1:
                vbm_down = np.max(all_eigval_down[idx1[0][-1],::2])
                cbm_down = np.min(all_eigval_down[idx2[0][0],::2])
                gap_down = cbm_down - vbm_down
            else:
                print('The gap of this system can not be obtained from this progrmme',
                'I suggest you carefully check the EIGENVAL by yourself')
                return
            return (vbm_up, cbm_up, gap_up), (vbm_down, cbm_down, gap_down)


def get_ele_sta(no_defect_outcar,number):
    number = int(number)
    tmp_match_line = _get_line(no_defect_outcar,rematch='electrostatic')
    rows = number // 5
    col =  number - rows * 5 - 1
    if col == -1:
        rows -= 1
        col = 4
    tmp_line = lc.getlines(no_defect_outcar)[tmp_match_line[0]+rows+3].split()
    return float(tmp_line[2*col+1])

def _get_line(file_tmp,rematch=None):
    grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
    return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]

def read_incar(incar):
    import re
    res = {}
    with open(incar,'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.strip() is '':
            continue
        line = re.sub(r"\s+","",line,flags=re.UNICODE).split('=')
        res[line[0]] = line[1]
    return res

def read_doscar(wd):
    c = read_vasp(os.path.join(wd,'POSCAR'))
    line6 = np.genfromtxt(os.path.join(wd,'DOSCAR'),skip_header=5,max_rows=1)
    n_dos = int(line6[2])
    sum_dos = np.genfromtxt(os.path.join(wd,'DOSCAR'),skip_header=6,max_rows=n_dos)
    np.savetxt(os.path.join(wd,'sum_dos.txt'),sum_dos,fmt="%.5f")
    incar = read_incar(os.path.join(wd,'INCAR'))
    if 'LORBIT' not in incar:
        return
    if int(incar['LORBIT']) == 11:
        for ii in range(c.atoms.shape[0]):
            p_dos = np.genfromtxt(os.path.join(wd,'DOSCAR'),skip_header=6+(1+n_dos)*(ii+1),max_rows=n_dos)
            np.savetxt(os.path.join(wd,'p_dos'+str(ii)+'.txt'),p_dos,fmt="%.5f")
