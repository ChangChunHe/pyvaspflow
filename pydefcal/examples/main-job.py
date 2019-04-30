#!/usr/bin/env python3
# coding: utf-8

from pydefcal.vasp.run_vasp import run_single_vasp,run_multi_vasp
import logging
from os import getpid
#submit a single job

logging.basicConfig(level=logging.INFO,
                    filename='./log.txt',
                    filemode='w',
                    format='%(asctime)s - %(filename)s\n[line:%(lineno)d] - %(levelname)s: %(message)s')

logging.info('Task start...')
logging.info('PID of this process: '+str(getpid()))
run_multi_vasp(sum_job_num=21,kppa=5000,job_name='stru_opt')
logging.info('Task completion')
