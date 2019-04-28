#!/usr/bin/env python3
# coding: utf-8

from pydefcal.run_vasp import runvasp
from pydefcal.run_vasp.runvasp import clean_parse
from sagar.io.vasp import read_vasp
import time,os,shutil
from pydefcal.vasp_io.vasp_input import Incar,Kpoints,Potcar


def stru_optmization(**kw):
    if not os.path.isfile('KPOINTS'):
        kpts = Kpoints()
        kppa,kw = clean_parse(kw,'kppa',3000)
        kpts.automatic_density(structure=stru,kppa=kppa)
        kpts.write_file()
    if not os.path.isfile('POTCAR'):
        pot = Potcar()
        pot.write_file()
    with open('POTCAR') as f:
        data = f.readlines()
    enmax = 1.3*max([float(i.split()[2].replace(';','')) for i in [i for i in data if 'ENMAX' in i]])
    node_name,kw =  clean_parse(kw,'node_name','short_q')
    node_num,kw =  clean_parse(kw,'node_num',1)
    cpu_num,kw =  clean_parse(kw,'cpu_num',24)
    job_name,kw = clean_parse(kw,'job_name','job_name')
    if not os.path.isfile('INCAR'):
        incar = Incar()
        incar['ENMAX'] = enmax
        incar.update(kw)
        incar.write_file()
    job_id, stderr = runvasp.submit_job(node_name=node_name,node_num=node_num,cpu_num=cpu_num,job_name=job_name)
    # waitting for calculation completion
    while True:
        if not runvasp.is_inqueue(job_id=job_id):
            break
        time.sleep(5)


def stru_scf(**kw):
    if os.path.isdir('scf'):
        shutil.rmtree('scf')
    os.makedirs('scf')
    shutil.copy2('CONTCAR','scf/POSCAR')
    shutil.copy2('POTCAR','scf/POTCAR')
    node_name,kw =  clean_parse(kw,'node_name','short_q')
    node_num,kw =  clean_parse(kw,'node_num',1)
    cpu_num,kw =  clean_parse(kw,'cpu_num',24)
    job_name,kw = clean_parse(kw,'job_name','job_name')
    kpts = Kpoints()
    kppa,kw = clean_parse(kw,'kppa',5000)
    kpts.automatic_density(structure=stru,kppa=float(kppa))
    kpts.write_file('scf/KPOINTS')
    incar = Incar()
    incar.from_file('INCAR')
    incar['LCHARG'] = 'True'
    incar['NSW'] = 0
    incar.update(kw)
    incar.write_file('scf/INCAR')
    os.chdir('scf')
    job_id, stderr = runvasp.submit_job(node_name=node_name,node_num=node_num,cpu_num=cpu_num,job_name=job_name)
    while True:
        if not runvasp.is_inqueue(job_id=job_id):
            break
        time.sleep(5)
    os.chdir('..')


def stru_band(**kw):
    if os.path.isdir('band'):
        shutil.rmtree('band')
    os.makedirs('band')
    shutil.copy2('scf/CONTCAR','band/POSCAR')
    shutil.copy2('scf/POTCAR','band/POTCAR')
    shutil.copy2('scf/CHGCAR','band/CHGCAR')
    shutil.copy2('scf/CHG','band/')
    node_name,kw =  clean_parse(kw,'node_name','short_q')
    node_num,kw =  clean_parse(kw,'node_num',1)
    cpu_num,kw =  clean_parse(kw,'cpu_num',24)
    job_name,kw = clean_parse(kw,'job_name','job_name')
    num_kpts,kw = clean_parse(kw,'num_kpts',16)
    kpts = Kpoints()
    kpts.automatic_linemode(structure=stru,num_kpts=num_kpts)
    kpts.write_file('band/KPOINTS')
    incar = Incar()
    incar.from_file('INCAR')
    incar['LCHARG'] = 'True'
    incar['ICHARG'] = 11
    incar['NSW'] = 0
    incar.update(kw)
    incar.write_file('band/INCAR')
    os.chdir('band')
    job_id, stderr = runvasp.submit_job(node_name=node_name,node_num=node_num,cpu_num=cpu_num,job_name=job_name)
    while True:
        if not runvasp.is_inqueue(job_id=job_id):
            break
        time.sleep(5)
    os.chdir('..')


if __name__ == '__main__':
    stru = read_vasp('./POSCAR')
    stru_optmization(NSW=100,EDIFF=1e-7,job_name='stru_optmization')
    stru_scf(kppa=6000,job_name='stru_scf')
    stru_band(num_kpts=20,job_name='stru_band')
