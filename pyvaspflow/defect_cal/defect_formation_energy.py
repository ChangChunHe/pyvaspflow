#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import warnings,sys,os
import numpy as np
from pyvaspflow.io.vasp_out import ExtractValue,get_ele_sta,read_incar
from pyvaspflow.utils import get_farther_atom_num

def get_defect_formation_energy(data_dir,defect_dirs):
    print('The main direcroty is: ', data_dir)
    f = open(os.path.join(data_dir,'defect-log.txt'),'w')
    fig, ax = plt.subplots()
    for defect_dir in defect_dirs:
        print('Reading ', defect_dir)
        f.write(defect_dir+'\n')
        SC_energy = ExtractValue(os.path.join(data_dir,'supercell/scf/')).get_energy()
        print('Energy of supcell is: '+str(SC_energy)+' eV')
        f.write('Energy of supcell is: '+str(SC_energy)+' eV\n')
        res = ExtractValue(os.path.join(data_dir,'supercell/scf/')).get_gap()
        if len(res) == 3:
            Evbm, Ecbm, gap = res
        elif len(res) == 2:
            Evbm, Ecbm, gap = res[0]
        print('Evbm, Ecbm, gap of supcell is: ', Evbm, Ecbm, gap)
        f.write('Evbm: '+str(Evbm)+' eV\n'+'Ecbm: '+str(Ecbm)+' eV\n'+'gap: '+str(gap)+' eV\n')
        chg_state = []
        f.write('charge\t\tenergy\t\tE_PA\t\tE_IC\tfar_atom_def_sys\tfar_atom_def_fr_system\n')
        for chg_fd in os.listdir(os.path.join(defect_dir)):
            if 'charge_state_' in chg_fd:
                q = chg_fd.split('_')[-1]
                e = ExtractValue(os.path.join(defect_dir,chg_fd,'scf')).get_energy()
                no_def_poscar = os.path.join(data_dir,'supercell','scf/CONTCAR')
                def_poscar = os.path.join(defect_dir,chg_fd,'POSCAR')
                num_def, num_no_def = get_farther_atom_num(no_def_poscar, def_poscar)
                pa_def = get_ele_sta(os.path.join(defect_dir,chg_fd,'scf','OUTCAR'),num_def)
                pa_no_def = get_ele_sta(os.path.join(data_dir,'supercell','scf','OUTCAR'),num_no_def)
                E_imagecor = ExtractValue(os.path.join(data_dir,'image_corr')).get_image()
                chg_state.append([int(float(q)), e, pa_def-pa_no_def, E_imagecor, num_def, num_no_def])
        ele_in_out = read_incar('element-in-out')
        incar_para = read_incar(os.path.join(data_dir,'defect-incar'))
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
    plt.savefig(os.path.join(data_dir,'defect_formation_energy.png'),dpi=450)
