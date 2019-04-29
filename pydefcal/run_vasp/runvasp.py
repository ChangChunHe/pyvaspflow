#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.utils import run,read_json
from os import path,makedirs,chdir
import json,shutil
from sagar.io.vasp import read_vasp
from pydefcal.vasp_io.vasp_input import Incar,Kpoints,Potcar


def is_inqueue(job_id):
    res = run('squeue','grep '+str(job_id)).std_out_err
    if res[0] == '':
        return False
    else:
        return True

def _submit_job(node_name,cpu_num,node_num=1,job_name='job-name'):
    write_job_file(node_name,cpu_num,node_num,job_name)
    res = run('sbatch job.sh')
    std = res.std_out_err
    return std[0].split()[-1],std[1]

def job_status(job_id):
    res = run('squeue','grep '+str(job_id)).std_out_err
    stdout = res[0].split()
    if stdout == [] :
        print('Not found job_id in queue')
        return  None
    return dict(zip(['job_id','part','name','user','status','time','node','nodelist'],stdout))

def write_job_file(node_name,cpu_num,node_num,job_name):
    json_f = read_json()
    with open('job.sh','w') as f:
        f.writelines('#!/bin/bash -l\n')
        f.writelines('#SBATCH -J '+job_name+'\n')
        f.writelines('#SBATCH -p '+node_name+' -N '+ str(node_num) +' -n '+str(cpu_num)+'\n\n')
        f.writelines(json_f['job']['prepend']+'\n')
        f.writelines(json_f['job']['exec']+'\n')

def write_incar(kw={}):
    if path.isfile('POTCAR'):
        with open('POTCAR') as f:
            data = f.readlines()
        enmax = 1.3*max([float(i.split()[2].replace(';','')) for i in [i for i in data if 'ENMAX' in i]])
    else:
        enmax = None
    if not path.isfile('INCAR'):
        incar = Incar()
        if enmax:
            incar['ENMAX'] = enmax
        incar.update(kw)
        incar.write_file('INCAR')
    return kw

def write_potcar(kw={}):
    if not path.isfile('POTCAR'):
        functional,kw =  clean_parse(kw,'functional','paw_PBE')
        sym_potcar_map,kw =  clean_parse(kw,'sym_potcar_map',None)
        pot = Potcar(functional=functional,sym_potcar_map=sym_potcar_map)
        pot.write_file()
    return kw

def write_kpoints(poscar='POSCAR',kw={}):
    if not path.isfile(poscar):
        raise FileNotFoundError('Not found POSCAR')
    stru = read_vasp(poscar)
    style,kw = clean_parse(kw,'style','auto')
    if not path.isfile('KPOINTS'):
        kpts = Kpoints()
        if 'auto' in style.lower():
            kppa,kw = clean_parse(kw,'kppa',3000)
            kpts.automatic_density(structure=stru,kppa=kppa)
            kpts.write_file('KPOINTS')
        elif 'gamma' in style.lower():
            kppa,kw = clean_parse(kw,'kppa',3000)
            kpts.automatic_gamma_density(structure=stru,kppa=kppa)
            kpts.write_file('KPOINTS')
        elif 'band' in style.lower() or 'line' in style.lower():
            num_kpts,kw = clean_parse(kw,'num_kpts',16)
            kpts.automatic_linemode(structure=stru,num_kpts=num_kpts)
            kpts.write_file('KPOINTS')
    return kw

def clean_parse(kw,key,def_val):
    val = kw.get(key,def_val)
    kw.pop(key,None)
    return val,kw

def submit_job(node_name,cpu_num,node_num=1,**kw):
    job_name,kw = clean_parse(kw,'job_name','job-name')
    if path.isdir(job_name):
        shutil.rmtree(job_name)
    else:
        makedirs(job_name)
    shutil.move('POSCAR',path.join(job_name,'POSCAR'))
    chdir(job_name)
    kw = write_potcar(kw)
    kw = write_incar(kw)
    kw = write_kpoints(kw=kw)
    job_id,err = _submit_job(node_name,cpu_num,node_num=node_num,job_name=job_name)
    chdir('..')
    return job_id,err
