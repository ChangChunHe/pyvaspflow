#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


import linecache as lc
import numpy as np
import os
import subprocess
from function_toolkit import get_farther_atom_num

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
        line = re.sub(r"\s+","",line,flags=re.UNICODE).split('=')
        res[line[0]] = line[1]
    return res


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import warnings
    import sys
    if len(sys.argv) < 3:
        raise ValueError('Not enough input parameters, you should input the main direcroty and the defect-directory')
    data_folder = sys.argv[1]
    print('The main direcroty is: ', data_folder)
    defect_dirs = sys.argv[2:]
    fig, ax = plt.subplots()
    f = open(sys.argv[1].replace("\\",'').replace("/",'')+'_log.txt','w')
    for defect_dir in  defect_dirs:
        print('Reading ', defect_dir)
        f.write(defect_dir+'\n')
        SC_energy = ExtractValue(os.path.join(data_folder,'supercell/scf/')).get_energy()
        print('Energy of supcell is: '+str(SC_energy)+' eV')
        f.write('Energy of supcell is: '+str(SC_energy)+' eV\n')
        res = ExtractValue(os.path.join(data_folder,'supercell/scf/')).get_gap()
        if len(res) == 3:
            Evbm, Ecbm, gap = res
        elif len(res) == 2:
            Evbm, Ecbm, gap = res[0]
        print('Evbm, Ecbm, gap of supcell is: ', Evbm, Ecbm, gap)
        f.write('Evbm: '+str(Evbm)+' eV\n'+'Ecbm: '+str(Ecbm)+' eV\n'+'gap: '+str(gap)+' eV\n')
        chg_state = []
        f.write('charge\t\tenergy\t\tE_PA\t\tE_IC\tfar_atom_def_sys\tfar_atom_def_fr_system\n')
        for chg_fd in os.listdir(os.path.join(defect_dir)):
            if 'charge_state' in chg_fd:
                q = chg_fd.split('_')[-1]
                e = ExtractValue(os.path.join(defect_dir,chg_fd,'scf')).get_energy()
                no_def_poscar = os.path.join(data_folder,'supercell','scf/CONTCAR')
                def_poscar = os.path.join(defect_dir,chg_fd,'POSCAR')
                num_def, num_no_def = get_farther_atom_num(no_def_poscar, def_poscar)
                pa_def = get_ele_sta(os.path.join(defect_dir,chg_fd,'scf','OUTCAR'),num_def)
                pa_no_def = get_ele_sta(os.path.join(data_folder,'supercell','scf','OUTCAR'),num_no_def)
                E_imagecor = ExtractValue(os.path.join(data_folder,'image_corr')).get_image()
                chg_state.append([int(float(q)), e, pa_def-pa_no_def, E_imagecor, num_def, num_no_def])
        ele_in_out = read_incar('element-in-out')
        incar_para = read_incar('defect-incar')
        incar_para['mu_Vacc'] = 0
        if 'epsilon' in incar_para:
            epsilon = float(incar_para['epsilon'])
        else:
            epsilon = 1e10
            warnings.warn("You should specify epsilon in your defect-incar, here we just ignore this correlation")
        chg_state = np.asarray(chg_state)
        chg_state[:,2] = chg_state[:,2]*chg_state[:,0]
        chg_state[:,3] = -2/3*chg_state[:,0]**2*chg_state[:,3]/epsilon
        for c in chg_state:
            f.write('{:2d}\t\t{:.5f}\t{:+.5f}\t{:+.5f}\t{:d}\t\t\t{:d}\n'.format(int(c[0]),c[1],c[2],c[3],int(c[4]),int(c[5])))
        mu = 0
        for key,val in ele_in_out.items():
            if 'mu_'+key in incar_para:
                mu += float(incar_para['mu_'+key])*int(val)
                f.write('chemical potential of '+key.title()+': '+str(incar_para['mu_'+key])+' eV\n')
            else:
                raise ValueError('chemical potential mu_'+key.title()+' cannot found')
        os.system('rm element-in-out')
        for key, val in ele_in_out.items():
            if int(val) == -1:
                f.writelines(key.title()+' has been doped\n')
            else:
                f.writelines(key.title()+' has been removed\n')
        f.writelines('\n')
        Ef = np.linspace(Evbm,Ecbm,1000)
        chg_state = np.asarray(chg_state)
        E = []
        for idx in range(np.shape(chg_state)[0]):
            E.append(chg_state[idx,1]-SC_energy+mu+chg_state[idx,0]*Ef+chg_state[idx,2]+chg_state[idx,3])
        E = np.asarray(E)
        ax.set_aspect('equal')
        ax.plot(Ef-Evbm,np.min(E,axis=0),label=defect_dir)
    f.close()
    plt.xlabel(r'$E_F$ (eV)')
    plt.ylabel(r'$\Delta E (eV)$')
    plt.legend()
    plt.savefig('defect_formation_energy.png',dpi=450)
