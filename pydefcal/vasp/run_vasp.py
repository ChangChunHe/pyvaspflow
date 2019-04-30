#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.vasp import prep_vasp
from os import chdir,makedirs,path
from shutil import copy2,rmtree
from multiprocessing import Process,Manager
from pydefcal.utils import run
from time import sleep


def is_inqueue(job_id):
    res = run('squeue','grep '+str(job_id)).std_out_err
    if res[0] == '':
        return False
    return True

def submit_job():
    res = run('sbatch ./job.sh')
    std = res.std_out_err
    return std[0].split()[-1]

def job_status(job_id):
    res = run('squeue','grep '+str(job_id)).std_out_err
    stdout = res[0].split()
    if stdout == [] :
        print('Not found job_id in queue')
        return  None
    return dict(zip(['job_id','part','name','user','status','time','node','nodelist'],stdout))

def clean_parse(kw,key,def_val):
    val = kw.get(key,def_val)
    kw.pop(key,None)
    return val,kw

def _submit_job(wd,jobs_dict):
    res = run('sbatch ./job.sh')
    std = res.std_out_err
    jobs_dict[wd] = std[0].split()[-1]

def run_sing_vasp(**kw):
    par_job_num,kw = clean_parse(kw,'par_job_num',4)
    node_name,kw = clean_parse(kw,'node_num','short_q')
    cpu_num,kw = clean_parse(kw,'cpu_num',24)
    node_num,kw = clean_parse(kw,'node_num',1)
    job_name,kw = clean_parse(kw,'job_name','task')
    if path.isdir(job_name):
        rmtree(job_name)
    makedirs(job_name)
    chdir(job_name)
    copy2('../POSCAR','./POSCAR')
    kw = prep_vasp.write_potcar(kw=kw)
    kw = prep_vasp.write_kpoints(kw=kw)
    kw = prep_vasp.write_incar(kw=kw)
    prep_vasp.write_job_file(node_name=node_name,
    node_num=node_num,cpu_num=cpu_num,job_name=job_name)
    job_id = submit_job()
    while True:
        if not is_inqueue(job_id):
            break
        sleep(5)
    chdir('..')


def run_multi_vasp(sum_job_num,**kw):
    par_job_num,kw = clean_parse(kw,'par_job_num',4)
    node_name,kw = clean_parse(kw,'node_num','short_q')
    cpu_num,kw = clean_parse(kw,'cpu_num',24)
    node_num,kw = clean_parse(kw,'node_num',1)
    for ii in range(sum_job_num):
        if path.isdir('task'+str(ii)):
            continue
        makedirs('task'+str(ii))
        chdir('task'+str(ii))
        copy2('../POSCAR'+str(ii),'./POSCAR')
        kw = prep_vasp.write_potcar(kw=kw)
        kw = prep_vasp.write_kpoints(kw=kw)
        kw = prep_vasp.write_incar(kw=kw)
        prep_vasp.write_job_file(node_name=node_name,
        node_num=node_num,cpu_num=cpu_num,job_name='task'+str(ii))
        chdir('..')
    job_inqueue_num = lambda id_pool:[is_inqueue(i) for i in id_pool].count(True)
    jobs = []
    manager = Manager()
    jobs_dict = manager.dict()
    for ii in range(par_job_num):
        chdir('task'+str(ii))
        p = Process(target=_submit_job,args=('task'+str(ii),jobs_dict))
        jobs.append(p)
        p.start()
        p.join()
        chdir('..')
    jobid_pool = jobs_dict.values()
    idx = par_job_num
    while True:
        inqueue_num = job_inqueue_num(jobid_pool)
        if inqueue_num < par_job_num:
            for j in range(par_job_num-inqueue_num):
                chdir('task'+str(idx))
                p = Process(target=_submit_job,args=('task'+str(idx),jobs_dict))
                jobs.append(p)
                p.start()
                p.join()
                chdir('..')
                idx += 1
                if idx == sum_job_num:
                    break
        jobid_pool = jobs_dict.values()
        sleep(5)
        if idx == sum_job_num:
            break
