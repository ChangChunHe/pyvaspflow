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

    def _get_line(self,file_tmp,rematch=None):
        grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
        return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]

    def get_energy(self):
        file_outcar = os.path.join(self.data_folder,'OUTCAR')
        grep_res = subprocess.Popen(['grep','TOTEN',file_outcar],stdout=subprocess.PIPE)
        return float(subprocess.check_output(['tail','-1'],stdin=grep_res.stdout).decode('utf-8').split()[-2])

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


    def get_miu(self):
        file_value, file_out = self.data_folder + 'value', self.data_folder + 'out'
        with open (file_value,'r') as f:
            miu_i = {}
            for line in f.readlines():
                tmp = line.split()
                miu_i.update({tmp[0]:np.array([
                                float(tmp[1])+float(tmp[2]),
                                float(tmp[1])+float(tmp[3]),
                                float(tmp[1])+float(tmp[4])
                                ])})
        state_d = {}
        with open(file_out,'r')  as f:
            for line in f.readlines():
                tmp = line.split()
                state_d.update({tmp[0]:float(tmp[1])})
        miu = np.zeros((3))
        for ele,state in state_d.items():
            miu +=miu_i[ele]*(-state_d[ele])
        return miu


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


#%% main script
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    data_folder = 'Si'
    purity_in,purity_out = 'Vacc', 'Si'
    defect_dir = purity_out+'-'+purity_in+'-defect'
    epsilon = 13.36
    SC_energy = ExtractValue(os.path.join(data_folder,'supercell/scf/')).get_energy()
    Evbm, Ecbm, gap = ExtractValue(os.path.join(data_folder,'supercell/scf/')).get_gap()
    miu = SC_energy / 216
    chg_state = []
    for chg_fd in os.listdir(os.path.join(data_folder,defect_dir)):
        if 'charge_state' in chg_fd:
            q = chg_fd.split('_')[-1]
            e = ExtractValue(os.path.join(data_folder,defect_dir,chg_fd,'scf')).get_energy()
            no_def_poscar = os.path.join(data_folder,'supercell','CONTCAR')
            def_poscar = os.path.join(data_folder,defect_dir,chg_fd,'POSCAR')
            num_def, num_no_def = get_farther_atom_num(no_def_poscar, def_poscar)
            pa_def = get_ele_sta(os.path.join(data_folder,defect_dir,chg_fd,'scf','OUTCAR'),num_def)
            pa_no_def = get_ele_sta(os.path.join(data_folder,'supercell/scf','OUTCAR'),num_no_def)
            E_imagecor = ExtractValue(os.path.join(data_folder,'image_corr')).get_image()
            chg_state.append([int(float(q)), e, pa_def-pa_no_def, E_imagecor])
    chg_state = np.asarray(chg_state)
    Ef = np.linspace(Evbm,Ecbm,1000)
    chg_state = np.asarray(chg_state)
    E = []
    for idx in range(np.shape(chg_state)[0]):
        _E = chg_state[idx,1]-SC_energy+miu+chg_state[idx,0]*Ef \
        +chg_state[idx,0]*chg_state[idx,2]-2/3*chg_state[idx,0]**2*chg_state[idx,3]/epsilon
        E.append(_E)
        # plt.plot(Ef-Evbm,_E,label='charge state: '+str(int(chg_state[idx,0])))h
    E = np.asarray(E)
    plt.plot(Ef-Evbm, np.min(E,axis=0),label=data_folder)
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.xlabel(r'$E_F$ (eV)')
    plt.ylabel(r'$\Delta E (eV)$')
    plt.legend()
    plt.savefig('defect_formation_energy.png',dpi=450)
    plt.show()

    # dirs = []
    # for ii in os.listdir(data_folder+'/'):
    #     if 'NELECT' in ii:
    #         dirs.append(ii)
    # for path in dirs:
    #     nelect_d = Acquire_value(data_folder+'/'+path+'/').get_Ne_d()
    #     charge_state = nelect_p - nelect_d
    #     D_energy = Acquire_value(data_folder+'/'+path+'/scf/').get_energy()
    #
    #     if atomic_num is None:
    #         V_delt = 0
    #     else:
    #         V_delt = Acquire_value(data_folder+'/'+path+'/scf/', atomic_num=atomic_num).get_PA() -\
    #                     Acquire_value('scf/', atomic_num=atomic_num).get_PA()
    #
    #
    #     Ewald = Acquire_value('./').get_image()
    #     if epsilon is None:
    #         E_imagecor = 0
    #     else:
    #         E_imagecor = -2/3*charge_state**2*Ewald/epsilon
    #
    #
    #     Hf_vbm = D_energy + E_imagecor - SC_energy + miu + charge_state * (Evbm-0.5+V_delt)
    #     Hf_cbm = D_energy + E_imagecor - SC_energy + miu + charge_state * (Evbm+gap+0.5+V_delt)
    #     for ii in range(len(miu)):
    #         diff_d[data_folder] = diff_d.get(data_folder,[])
    #         diff_d[data_folder].append([charge_state, D_energy, SC_energy, V_delt, E_imagecor, miu[ii], gap, Hf_vbm[ii], Hf_cbm[ii]])

# if __name__ == "__main__":
#     EV = ExtractValue('/home/hecc/Desktop/supercell')
#     print(EV.get_PA(24))
