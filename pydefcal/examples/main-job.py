#!/usr/bin/env python3
# coding: utf-8

from pydefcal.vasp.run_vasp import run_sing_vasp,run_multi_vasp

#submit a single job

run_sing_vasp(NSW=1000,LCHARG=True,LWAVE=True,EDIFF=1e-10,job_name='stru_opt')
