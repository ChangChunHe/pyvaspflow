#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from itertools import combinations
from collections import namedtuple, defaultdict
import re
from sagar.element.base import periodic_table_dict as ptd


all_eles = [key for key in ptd]
def get_ele_num(line):
    _element = []
    for ele in all_eles:
        tmp = line.find(ele)
        if tmp != -1:
            if line[tmp:tmp+2] in all_eles:
                _element.append(line[tmp:tmp+2])
            else:
                _element.append(line[tmp:tmp+1])
    _element = list(set(_element))
    idx = np.argsort([line.index(ele) for ele in _element])
    element = [_element[i] for i in idx]
    all_idx = [(line.index(ele), len(ele)) for ele in element]
    number = []
    for ii in range(len(all_idx)-1):
        tmp = line[all_idx[ii][0]+all_idx[ii][1]:all_idx[ii+1][0]]
        if tmp == '':tmp = '1'
        number.append(int(tmp))
    tmp = line[all_idx[-1][1]+all_idx[-1][0]:]
    if tmp == '':tmp = '1'
    number.append(int(tmp))
    return (element,number)


class Phase:
    def __init__(self,name='',element='',number='',energy=''):
        self.name = name
        self.element = element
        self.number = number
        self.energy = energy
    def __repr__(self):
        print('name: ',self.name)
        print('element: ',self.element)
        print('number: ',self.number)
        print('energy: ',self.energy)

with open('chemical-incar','r') as f:
    lines = f.readlines()

pure_phase = {}
for line in lines:
    line = re.sub(r"\s+","",line,flags=re.UNICODE).split('=')
    (tmp_ele,tmp_num) = get_ele_num(line[0])
    if len(tmp_ele) == 1:
        pure_phase[tmp_ele[0]] = float(line[1]) / float(tmp_num[0])
    else:
        if '#' in line[0]:
            line[0] = line[0].replace('#','')
            element, number = get_ele_num(line[0])
            energy = float(line[1])
            host = Phase(name=line[0],element=element,number=np.array(number),energy=energy)
for idx in range(len(host.element)):
    host.energy -= host.number[idx] * pure_phase[host.element[idx]]

compete_phase = []
for line in lines:
    line = re.sub(r"\s+","",line,flags=re.UNICODE).split('=')
    element, number = get_ele_num(line[0])
    ele_num = defaultdict(lambda: 0, dict(zip(element,number)))
    if '#' not in line[0] and len(element) > 1:
        element = host.element
        number = np.array([ele_num[key] for key in element])
        energy = float(line[1])
        for idy in range(len(host.element)):
            energy -= number[idy] * pure_phase[host.element[idy]]
        compete_phase.append(Phase(name=line[0],element=element,number=number,energy=energy))


atom_num = len(host.element)
f = open('chemical_log.txt','w')
pts = {}
for phase in compete_phase:
    f.write('chemical potential constrain of '+phase.name+'\n')
    for ii in host.element:
        f.write(str(ii)+'\t')
    f.write('\n')
    A_ub = -phase.number.reshape((1,-1))
    b_ub = -np.array(phase.energy).reshape((1,1))
    A_eq = np.array(host.number).reshape((1,-1))
    b_eq = np.array(host.energy).reshape((1,1))
    bounds = [(None,0) for i in range(atom_num)]
    pts_val = []
    for ii in range(atom_num):
        c = np.zeros((atom_num,))
        c[ii] = 1
        res = linprog(c,A_ub,b_ub,A_eq,b_eq,bounds=bounds)
        import pdb;pdb.set_trace()
        res = res.x.tolist()
        f.write('\t'.join([str(np.round(i,4)) for i in res])+'\n')
        pts_val.append(res)
    pts[phase.name] = pts_val
    f.write('\n')
f.close()


fig = plt.figure()
ax=plt.axes()
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.spines['bottom'].set_position(('data',0))
ax.yaxis.set_ticks_position('left')
ax.spines['left'].set_position(('data',0))
ax.set_xlabel(r'$\mu_A $ (eV)',ha='left', va = 'top')
ax.xaxis.set_label_coords(0, 1.01)
ax.set_ylabel(r'$\mu_B$ (eV)')
ax.yaxis.set_label_coords(1.01, 0)

for key, val in pts.items():
    for two_pts in combinations(val,2):
        x,y = two_pts[0],two_pts[1]
        plt.plot([x[0],y[0]],[x[1],y[1]],color="blue",linewidth=2.5,linestyle="-")

xlim,ylim = host.energy/host.number[0],host.energy/host.number[1]
plt.plot([xlim,0],[0,ylim],color="blue",linewidth=2.5,linestyle="-")
plt.plot([xlim,0],[0,0],color="blue",linewidth=2.5,linestyle="-")
plt.plot([0,0],[0,ylim],color="blue",linewidth=2.5,linestyle="-")
plt.show()
