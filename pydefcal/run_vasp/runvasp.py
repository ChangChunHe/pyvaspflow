#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pydefcal.utils import run,read_json
from os import path
import json


def is_inqueue(job_id):
    res = run('squeue','grep '+str(job_id)).std_out_err
    if res[0] == '':
        return False
    else:
        return True

def submit_job(node_name, cpu_num,node_num=1,job_name='job-name'):
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

def clean_parse(kw,key,def_val):
    val = kw.get(key,def_val)
    kw.pop(key,None)
    return val,kw
