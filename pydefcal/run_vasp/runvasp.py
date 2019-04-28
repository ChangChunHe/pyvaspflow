#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.utils import run,read_json
from os import path
import json

def is_inqueue(jobid):
    res = run('squeue','grep '+str(jobid)).std_out_err
    if res[0] == '':
        return False
    else:
        return True

def submit_job(node_name, cpu_num,node_num=1,jobname='job-name'):
    write_job_file(node_name,cpu_num,node_num,jobname)
    res = run('sbatch job.sh')
    std = res.std_out_err
    return std[0].split()[-1],std[1]


def job_status(jobid):
    res = run('squeue','grep '+str(jobid)).std_out_err
    stdout = res[0].split()
    if stdout == [] :
        print('Not found jobid in queue')
        return  None
    return dict(zip(['jobid','part','name','user','status','time','node','nodelist'],stdout))

def write_job_file(node_name,cpu_num,node_num,jobname):
    json_f = read_json()
    with open('job.sh','w') as f:
        f.writelines('#!/bin/bash -l\n')
        f.writelines('#SBATCH -J '+jobname+'\n')
        f.writelines('#SBATCH -p '+node_name+' -N '+ str(node_num) +' -n '+str(cpu_num)+'\n\n')
        f.writelines(json_f['job']['prepend']+'\n')
        f.writelines(json_f['job']['exec']+'\n')
