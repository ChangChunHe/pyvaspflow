#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
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


def get_3d_cross_pts(A,B):
# A = [1,2,4,-10]
# B = [1,0,1,-6]
    C = np.array([A,B])
    res = []
    for com in combinations(range(len(A)-1),len(A)-2):
        a,b = C[:,com],C[:,-1]
        x = np.linalg.solve(a, b)
        _res = np.zeros((len(A)-1,))
        _res[list(com)] = x
        _res[np.setdiff1d(range(len(A)-1),com)] = 0
        res.append(_res.tolist())
    return res


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


def plot_2d_chemical_potential_phase(chem_incar, remove_ele=0):
    with open(chem_incar,'r') as f:
        lines = f.readlines()
    pure_phase = {}
    for line in lines:
        if not line.strip(): continue
        line = re.sub(r"\s+","",line,flags=re.UNICODE).split('=')
        (tmp_ele,tmp_num) = get_ele_num(line[0])
        if len(tmp_ele) == 1:
            pure_phase[tmp_ele[0]] = float(line[1]) / float(tmp_num[0])
        else:
            if '#' in line[0]:
                line[0] = line[0].replace('#','')
                element, number = get_ele_num(line[0])
                energy = float(line[1])
                host = Phase(name=line[0],element=element,number=number,energy=energy)
    for idx in range(len(host.element)):
        host.energy -= host.number[idx] * pure_phase[host.element[idx]]
    compete_phase = []
    for line in lines:
        if not line.strip(): continue
        line = re.sub(r"\s+","",line,flags=re.UNICODE).split('=')
        element, number = get_ele_num(line[0])
        ele_num = defaultdict(lambda: 0, dict(zip(element,number)))
        if '#' not in line[0] and len(element) > 1:
            element = host.element
            number = [ele_num[key] for key in element]
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
        A_ub = phase.number
        A_ub.append(phase.energy)
        A_eq = host.number.copy()
        A_eq.append(host.energy)
        pts_val1 = get_3d_cross_pts(A_eq,A_ub)
        pts[phase.name] = pts_val1
        for pt in pts_val1:
            f.write('\t'.join([str(np.round(i,4)) for i in pt])+'\n')
        f.write('\n')
    f.close()
    idx = [0,1,2]
    idx.remove(remove_ele)
    fig = plt.figure()
    ax=plt.axes()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['bottom'].set_position(('data',0))
    ax.yaxis.set_ticks_position('left')
    ax.spines['left'].set_position(('data',0))
    ax.set_xlabel(r'$\mu $'+host.element[idx[0]]+' (eV)',ha='left',va='top')
    ax.xaxis.set_label_coords(0, 1.01)
    ax.set_ylabel(r'$\mu$'+host.element[idx[1]]+' (eV)')
    ax.yaxis.set_label_coords(1.01, 0)
    for key, val in pts.items():
        for two_pts in combinations(val,2):
            pts0,pts1 = two_pts[0],two_pts[1]
            x1,x2,y1,y2 = pts0[idx[0]],pts1[idx[0]],pts0[idx[1]],pts1[idx[1]]
            if all(np.array([x1,x2,y1,y2])<=0) and A_eq[idx[0]]*x1+A_eq[idx[1]]*y1 >=A_eq[-1] \
            and A_eq[idx[0]]*x2+A_eq[idx[1]]*y2 >=A_eq[-1]:
                plt.plot([x1,x2],[y1,y2],linewidth=1,linestyle="-",label=key)
    xlim,ylim = host.energy/host.number[idx[0]],host.energy/host.number[idx[1]]
    plt.plot([xlim,0],[0,ylim],color="blue",linewidth=2,linestyle="-")
    plt.plot([xlim,0],[0,0],color="blue",linewidth=2,linestyle="-")
    plt.plot([0,0],[0,ylim],color="blue",linewidth=2,linestyle="-")
    plt.legend()
    plt.savefig('chemical-potential.png',dpi=450)


if __name__ == '__main__':
    plot_2d_chemical_potential_phase('chemical-incar')
