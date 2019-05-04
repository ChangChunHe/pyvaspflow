#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.vasp import prep_vasp
from os import chdir
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

def run_single_vasp(job_name):
    chdir(job_name)
    job_id = submit_job()
    while True:
        if not is_inqueue(job_id):
            break
        sleep(5)
    chdir('..')


def run_multi_vasp(job_name,sum_job_num,start_job_num=0,par_job_num=4):
    job_inqueue_num = lambda id_pool:[is_inqueue(i) for i in id_pool].count(True)
    jobs = []
    sum_job_num,start_job_num,par_job_num = int(sum_job_num),int(start_job_num),int(par_job_num)
    manager = Manager()
    jobs_dict = manager.dict()
    idx = start_job_num
    for ii in range(min(par_job_num,sum_job_num-start_job_num)):
        chdir(job_name+str(ii+start_job_num))
        p = Process(target=_submit_job,args=(job_name+str(ii+start_job_num),jobs_dict))
        jobs.append(p)
        p.start()
        p.join()
        chdir('..')
        idx += 1
    if idx == sum_job_num+1:
        return
    jobid_pool = jobs_dict.values()
    while True:
        inqueue_num = job_inqueue_num(jobid_pool)
        if inqueue_num < par_job_num:
            for j in range(par_job_num-inqueue_num):
                chdir(job_name+str(idx))
                p = Process(target=_submit_job,args=(job_name+str(idx),jobs_dict))
                jobs.append(p)
                p.start()
                p.join()
                chdir('..')
                idx += 1
                if idx == sum_job_num+1:
                    break
        jobid_pool = jobs_dict.values()
        sleep(5)
        if idx == sum_job_num+1:
            break
