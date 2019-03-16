#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 20:47:13 2019

@author: hecc
"""
import sys
from numpy import genfromtxt, zeros, mean, where
folder = sys.argv[1]
line6 = genfromtxt(folder+'/EIGENVAL',skip_header=5,max_rows=1)
kpt_num, eig_num = int(line6[1]), int(line6[2])

all_eigval = zeros((eig_num, kpt_num*2))

for ii in range(kpt_num):
     all_eigval[:,2*ii:2*ii+2] = genfromtxt('EIGENVAL',skip_header=8+eig_num*int(ii)+2*ii,\
                               max_rows=eig_num,usecols=(1,2))
elec_num =  mean(all_eigval[:,1::2],axis=1)
idx1 = where(elec_num > 0.9)
idx2 = where(elec_num < 0.5)
if idx1[0][-1] - idx2[0][0] == -1:
    vbm = max(all_eigval[idx1[0][-1],::2])
    cbm = min(all_eigval[idx2[0][0],::2])
    gap = cbm - vbm
    print('VBM: ', vbm, 'CBM: ', cbm, 'Gap: ', gap)
