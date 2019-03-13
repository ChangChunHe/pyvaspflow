import linecache as lc
import numpy as np
import os
import subprocess
#%%class
class Acquire_value():
    def __init__(self,file_path='./',atomic_num=3):

        self.file = file_path
        self.atomic_num = atomic_num

    def _get_line(self,file_tmp,rematch=None):
        grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
        return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]

    def get_energy(self):

        file_out = self.file + 'OUTCAR'

        tmp_line = self._get_line(file_out,rematch='TOTEN')
        toten = float(lc.getlines(file_out)[tmp_line[-1]].split()[4])
        return toten

    def get_fermi(self):

        file_out = self.file + 'OUTCAR'

        tmp_line = self._get_line(file_out,rematch='E-fermi')
        fermi = float(lc.getlines(file_out)[tmp_line[0]].split()[2]) # read the first or last?
        return fermi

    def get_Ne_p(self):
        # get valance electrons
        file_pos = self.file + 'POSCAR'
        file_pot =  self.file + 'POTCAR'
        tmp_pos = lc.getlines(file_pos)[6].split()
        tmp_lines = self._get_line(file_pot,rematch='ZVAL')
        nelect_p = 0
        for ii in range(len(tmp_lines)):
            tmp_zval = lc.getlines(file_pot)[tmp_lines[ii]].split()[5]
            nelect_p+=round(int(tmp_pos[ii])*float(tmp_zval))
        return nelect_p

    def get_Ne_d(self):
        #get electrons number in OUTCAR
        file_out = self.file + 'OUTCAR'

        tmp_line = self._get_line(file_out,rematch='NELECT')
        nelect_d = lc.getlines(file_out)[tmp_line[0]].split()[2]
        return round(float(nelect_d))

    def get_image(self):

        file_image = self.file + 'image_cor/OUTCAR'

        tmp_line = self._get_line(file_image,rematch='Ewald')
        Ewald = lc.getlines(file_image)[tmp_line[0]].split()[4]
        return Ewald

    def get_PA(self):
        # get potential alignment correlation
        file_PA = self.file + 'OUTCAR'
        file_pos = self.file + 'POSCAR'

        tmp_atom_line = round(sum(map(int,lc.getlines(file_pos)[6].split()))/5)+3
        tmp_match_line = self._get_line(file_PA,rematch='electrostatic')

        for line in lc.getlines(file_PA)[tmp_match_line[0]:tmp_match_line[0]+tmp_atom_line]:
            if ' '+str(self.atomic_num )+' ' in line:
                if self.atomic_num %5==0:
                    return line.split()[9]
                else:
                    return line.split()[self.atomic_num %5*2-1]

    def get_gap(self):

        file_gap = self.file + 'EIGENVAL'

        nelect_vbm = int(lc.getlines(file_gap)[5].split()[0])//2
        nelect_cbm = nelect_vbm+1

        tmp_lines = self._get_line(file_gap,rematch=' '+str(nelect_vbm)+' ')
        Evbms = []
        for ii in tmp_lines:
            Evbms.append(lc.getlines(file_gap)[ii].split()[1])

        tmp_lines = self._get_line(file_gap,rematch=' '+str(nelect_cbm)+' ')
        Ecbms = []
        for ii in tmp_lines:
            Ecbms.append(lc.getlines(file_gap)[ii].split()[1])

        Ecbm, Evbm =  min(map(float,Ecbms)), max(map(float,Evbms))
        return Ecbm, Evbm, Ecbm - Evbm

    def get_miu(self):
        file_value, file_out = self.file + 'value', self.file + 'out'
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

#%% main script
files = ['N_Si','Vac_Si_defect','P_Si']
def main_Hf(files, atomic_num=None, epsilon=None):
    diff_d = {}

    for file in files:
        SC_energy = Acquire_value('scf/').get_energy()
        nelect_p = Acquire_value(file+'/').get_Ne_p()
        Ecbm, Evbm, gap = Acquire_value('scf/').get_gap()
        miu = Acquire_value(file+'/').get_miu()

        dirs = []
        for ii in os.listdir(file+'/'):
            if 'NELECT' in ii:
                dirs.append(ii)
        for path in dirs:
            nelect_d = Acquire_value(file+'/'+path+'/').get_Ne_d()
            charge_state = nelect_p - nelect_d
            D_energy = Acquire_value(file+'/'+path+'/scf/').get_energy()

            if atomic_num is None:
                V_delt = 0
            else:
                V_delt = Acquire_value(file+'/'+path+'/scf/', atomic_num=atomic_num).get_PA() -\
                            Acquire_value('scf/', atomic_num=atomic_num).get_PA()


            Ewald = Acquire_value('./').get_image()
            if epsilon is None:
                E_imagecor = 0
            else:
                E_imagecor = -2/3*charge_state**2*Ewald/epsilon


            Hf_vbm = D_energy + E_imagecor - SC_energy + miu + charge_state * (Evbm-0.5+V_delt)
            Hf_cbm = D_energy + E_imagecor - SC_energy + miu + charge_state * (Evbm+gap+0.5+V_delt)
            for ii in range(len(miu)):
                diff_d[file] = diff_d.get(file,[])
                diff_d[file].append([charge_state, D_energy, SC_energy, V_delt, E_imagecor, miu[ii], gap, Hf_vbm[ii], Hf_cbm[ii]])

            return diff_d
if __name__ == "__main__":
    Av = Acquire_value()
    count = Av._get_line(file_tmp='defect_maker.py',rematch='def')
    print(count)
