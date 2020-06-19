#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pyvaspflow.utils import read_json
from os import path,makedirs,chdir,listdir
from shutil import rmtree,copy2
from sagar.io.vasp import read_vasp
from pyvaspflow.io.vasp_input import Incar,Kpoints,Potcar
import progressbar


def write_job_file(node_name,cpu_num,node_num,job_name):
    json_f = read_json()
    with open('job.lsf','w') as f:
        f.writelines('#!/bin/bash \n')
        f.writelines('#BSUB -J '+job_name+'\n')
        f.writelines('#BSUB -q '+node_name +' -n '+str(int(cpu_num))+'\n\n')
        f.writelines('#BSUB -e %J.err\n#BSUB -o %J.out\n')
        f.writelines('#BSUB -R "span[ptile=40]"\n')
        f.writelines('hostfile=`echo $LSB_DJOB_HOSTFILE`\n')
        f.writelines('NP=`cat $hostfile|wc -l`\n')
        f.writelines(json_f['job']['prepend']+'\n')
        f.writelines(json_f['job']['exec']+'\n')
        f.writelines(json_f['job']['append']+'\n')

def write_multi_job_files(node_name,cpu_num,node_num,job_name,start,end,n_job,execute_line=None):
    json_f = read_json()
    each = (end - start+1) // n_job
    if each * n_job == end - start+1:
        each_num = [each]*n_job
    else:
        each_num = [each]*(n_job - 1)
        last_num = end-start + 1 - sum(each_num)

        if last_num > each:
            for i in range(last_num-each):
                each_num[i] += 1
            each_num.append(each)
        else:
            each_num.append(last_num)

    for idx in range(n_job):
        with open('job_'+str(idx)+'.lsf','w') as f:
            f.writelines('#!/bin/bash \n')
            f.writelines('#BSUB -J '+job_name+str(idx)+'\n')
            f.writelines('#BSUB -q '+node_name +' -n '+str(int(cpu_num))+'\n\n')
            f.writelines('#BSUB -e %J.err\n#BSUB -o %J.out\n')
            f.writelines('#BSUB -R "span[ptile=40]"\n')
            f.writelines('hostfile=`echo $LSB_DJOB_HOSTFILE`\n')
            f.writelines('NP=`cat $hostfile|wc -l`\n')

            f.writelines("for idx in {"+str(start)+".."+str(start+each_num[idx]-1)+"}"+"\ndo\n")
            f.writelines('cd '+job_name+'${idx}\n')
            if execute_line:
                f.writelines(execute_line+"\n")
            else:
                f.writelines(json_f['job']['prepend']+'\n')
                f.writelines(json_f['job']['exec']+'\n')
                f.writelines(json_f['job']['append']+'\n')
            f.writelines('cd ..\ndone\n')
        start += each_num[idx]

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

def clean_parse(kw,key,def_val):
    val = kw.get(key,def_val)
    kw.pop(key,None)
    return val,kw

def prep_single_vasp(poscar='POSCAR',kw={}):
    node_name,kw = clean_parse(kw,'node_name','short')
    cpu_num,kw = clean_parse(kw,'cpu_num',40)
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
    write_job_file(node_name=node_name,
    node_num=node_num,cpu_num=cpu_num,job_name=job_name)
    chdir('..')

def prep_multi_vasp(start_job_num=0,end_job_num=0,job_list=None,kw={}):
    node_name,kw = clean_parse(kw,'node_name','short')
    cpu_num,kw = clean_parse(kw,'cpu_num',40)
    node_num,kw = clean_parse(kw,'node_num',1)
    job_name,kw = clean_parse(kw,'job_name','task')
    _kw = kw.copy()
    if job_list is  None:
        job_list = range(start_job_num,end_job_num+1)
    toolbar_width = end_job_num - start_job_num + 1
    with progressbar.ProgressBar(max_value=toolbar_width) as bar:
        for idx,ii in enumerate(job_list):
            if path.isdir(job_name+str(idx)):
                rmtree(job_name+str(idx))
            makedirs(job_name+str(idx))
            copy2(path.join('./POSCAR'+str(ii)),path.join(job_name+str(idx),'POSCAR'))
            chdir(job_name+str(idx))
            kw = write_potcar(kw=kw)
            kw = write_kpoints(kw=kw)
            kw = write_incar(kw=kw)
            write_job_file(node_name=node_name,
            node_num=node_num,cpu_num=cpu_num,job_name=job_name+str(idx))
            kw = _kw.copy()
            chdir('..')
            bar.update(idx)

if __name__ == '__main__':
    write_multi_job_files(node_name="short_q",cpu_num=48,node_num=2,job_name="task",start=0,end=14,n_job=3)
