#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.vasp import prep_vasp,run_vasp
from pydefcal.io.vasp_input import Kpoints
from pydefcal.utils import is_2d_structure
from pydefcal.io.vasp_out import ExtractValue
from sagar.io.vasp import read_vasp
from os import makedirs,path,chdir,remove
from shutil import rmtree,copy2
import numpy as np

class TestParameter():
    def __init__(self,poscar='POSCAR'):
        self.poscar = poscar
        if is_2d_structure(read_vasp(self.poscar)):
            self.dimen = 2
        else:
            self.dimen = 3

    def test_enmax(self,kw={}):
        start,end,step = kw.get('start'),kw.get('end'),kw.get('step')
        kw.pop('start');kw.pop('end');kw.pop('step')
        _kw = kw.copy()
        prep_vasp.write_potcar(poscar=self.poscar,kw=_kw)
        with open('POTCAR') as f:
            lines = f.readlines()
        en_line = [i for i in lines if 'ENMAX' in i]
        enmax = max([float(i.split()[2].replace(';','')) for i in en_line])
        enmin = min([float(i.split()[5].replace(';','')) for i in en_line])
        remove('POTCAR')
        idx = 0
        for en in np.arange(start*enmin,end*enmax,step):
            _kw = kw.copy()
            _kw.update({'ENMAX':int(en),'job_name':'test_encut'+str(idx),'NSW':0})
            prep_vasp.prep_single_vasp(poscar=self.poscar,kw=_kw)
            idx += 1
        run_vasp.run_multi_vasp(job_name='test_encut',end_job_num=idx-1,par_job_num=1)
        encut_list = []
        encut = np.arange(start*enmin,end*enmax,step)
        for ii in range(len(encut)):
            EV = ExtractValue(data_folder='test_encut'+str(ii))
            encut_list.append([encut[ii],EV.get_energy(),EV.get_cpu_time()])
        with open('test_encut.txt','w') as f:
            f.writelines('ENMAX\tEnergy\tcpu_time\n')
            for line in encut_list:
                f.writelines(str(line[0])+'\t'+str(line[1])+'\t'+str(line[2])+'\n')


    def test_kpts(self,kw={}):
        start,end,step = kw.get('start'),kw.get('end'),kw.get('step')
        kw.pop('start');kw.pop('end');kw.pop('step')
        kpts = Kpoints()
        kpts_list = set()
        for kppa in range(start,end,step):
            kpts.automatic_density(structure=read_vasp(self.poscar),kppa=kppa)
            kpts_list.add(tuple(kpts.kpts[0]))
        idx = 0
        for kpt in kpts_list:
            _kw = kw.copy()
            _kw.update({'kpts':kpt,'style':'auto','job_name':'test_kpts'+str(idx)})
            prep_vasp.prep_single_vasp(poscar=self.poscar,kw=_kw)
            idx += 1
        run_vasp.run_multi_vasp(job_name='test_kpts',end_job_num=idx-1,par_job_num=1)
        kpts_res = []
        for ii in range(len(kpts_list)):
            EV = ExtractValue(data_folder='test_kpts'+str(ii))
            kpts_list.append([kpts_list[ii],EV.get_energy(),EV.get_cpu_time()])
        with open('test_kpts.txt','w') as f:
            f.writelines('KPTS\tEnergy\tcpu_time\n')
            for line in kpts_list:
                f.writelines(str(line[0]).replace('[','').replace(']','').replace(',','')+
                   '\t'+str(line[1])+'\t'+str(line[2])+'\n')


if __name__ == '__main__':
    tp = TestParameter()
    tp.test_kpts(kw={'start':1000,'end':3000,'step':300})
