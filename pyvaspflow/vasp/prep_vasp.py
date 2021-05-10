#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pyvaspflow.utils import read_config,clean_parse
from os import path,makedirs,chdir,listdir
from shutil import rmtree,copy2
from sagar.io.vasp import read_vasp
from pyvaspflow.io.vasp_input import Incar,Kpoints,Potcar
import sys,progressbar
from pyvaspflow.vasp.schedule import Schedule


config = read_config()
schedule = Schedule()



def write_incar(incar_file=None,kw={}):
    if path.isfile('POTCAR'):
        with open('POTCAR') as f:
            data = f.readlines()
        enmax = 1.3*max([float(i.split()[2].replace(';','')) for i in [i for i in data if 'ENMAX' in i]])
    else:
        enmax = None
    incar = Incar()
    if incar_file:
        incar.from_file(incar_file)
    if enmax and 'ENCUT' not in incar:
        incar['ENCUT'] = enmax
    incar.update(kw)
    incar.write_file('INCAR')
    return kw

def write_potcar(poscar='POSCAR',kw={}):
    if not path.isfile('POTCAR'):
        functional,kw =  clean_parse(kw,'functional','paw_PBE')
        sym_potcar_map,kw =  clean_parse(kw,'sym_potcar_map',None)
        pot = Potcar(poscar=poscar,functional=functional,sym_potcar_map=sym_potcar_map)
        pot.write_file('POTCAR')
    return kw

def write_kpoints(poscar='POSCAR',kw={}):
    if not path.isfile(poscar):
        raise FileNotFoundError('Not found POSCAR')
    stru = read_vasp(poscar)
    style,kw = clean_parse(kw,'style','gamma')
    if not path.isfile('KPOINTS'):
        _kpts = Kpoints()
        if 'auto' in style.lower():
            if 'kpts' not in kw :
                kppa,kw = clean_parse(kw,'kppa',3000)
                kppa = float(kppa)
                _kpts.automatic_density(structure=stru,kppa=kppa)
                _kpts.write_file('KPOINTS')
            else:
                kpts,kw = clean_parse(kw,'kpts',(1,1,1))
                shift,kw = clean_parse(kw,'shift',(0,0,0))
                _kpts.gamma_automatic(kpts=kpts,shift=shift)
                _kpts.write_file('KPOINTS')
        elif 'gamma' in style.lower() and 'kpts' not in kw:
            kppa,kw = clean_parse(kw,'kppa',3000)
            kppa = float(kppa)
            _kpts.automatic_gamma_density(structure=stru,kppa=kppa)
            _kpts.write_file('KPOINTS')
        elif 'gamma' in style.lower() and 'kpts' in kw:
            kpts,kw = clean_parse(kw,'kpts',(1,1,1))
            shift,kw = clean_parse(kw,'shift',(0,0,0))
            _kpts.gamma_automatic(kpts=kpts,shift=shift)
            _kpts.write_file('KPOINTS')
        elif 'monk' in style.lower() and 'kpts' in kw:
            kpts,kw = clean_parse(kw,'kpts',(1,1,1))
            shift,kw = clean_parse(kw,'shift',(0,0,0))
            _kpts.monkhorst_automatic(kpts=kpts,shift=shift)
            _kpts.write_file('KPOINTS')
        elif 'band' in style.lower() or 'line' in style.lower():
            num_kpts,kw = clean_parse(kw,'num_kpts',16)
            _kpts.automatic_linemode(structure=stru,num_kpts=int(num_kpts))
            _kpts.write_file('KPOINTS')
    return kw



def prep_single_vasp(poscar='POSCAR',kw={}):
    node_name,kw = clean_parse(kw,'node_name',config['Task_Schedule']['default_node_name'])
    cpu_num,kw = clean_parse(kw,'cpu_num',config['Task_Schedule']['default_cpu_num'])
    node_num,kw = clean_parse(kw,'node_num',1)
    job_name,kw = clean_parse(kw,'job_name','task')
    if path.isdir(job_name):
        rmtree(job_name)
    makedirs(job_name)
    chdir(job_name)
    copy2('../'+poscar,'./POSCAR')
    kw = write_potcar(kw=kw)
    kw = write_kpoints(kw=kw)
    kw = write_incar(kw=kw)
    chdir('..')
    schedule.schedule_type.write_job_file(node_name=node_name,node_num=node_num,cpu_num=cpu_num,job_name=job_name)

def prep_multi_vasp(start_job_num=0,end_job_num=0,job_list=None,kw={}):
    node_name,kw = clean_parse(kw,'node_name',config['Task_Schedule']['default_node_name'])
    cpu_num,kw = clean_parse(kw,'cpu_num',config['Task_Schedule']['default_cpu_num'])
    node_num,kw = clean_parse(kw,'node_num',1)
    job_name,kw = clean_parse(kw,'job_name','task')
    _kw = kw.copy()
    if job_list is  None:
        job_list = range(start_job_num,end_job_num+1)
    toolbar_width = end_job_num - start_job_num + 1
    with progressbar.ProgressBar(max_value=toolbar_width) as bar:
        for idx,ii in enumerate(job_list):
            if path.isdir(job_name+str(ii)):
                rmtree(job_name+str(ii))
            makedirs(job_name+str(ii))
            copy2(path.join('./POSCAR'+str(ii)),path.join(job_name+str(ii),'POSCAR'))
            chdir(job_name+str(ii))
            kw = write_potcar(kw=kw)
            kw = write_kpoints(kw=kw)
            kw = write_incar(kw=kw)
            kw = _kw.copy()
            chdir('..')
            schedule.schedule_type.write_job_file(node_name=node_name,node_num=node_num,cpu_num=cpu_num,job_name=job_name+str(ii))
            bar.update(idx)
