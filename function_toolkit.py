import numpy as np
from sagar.io.vasp import  write_vasp
from os import path


def generate_all_basis(N1,N2,N3):
    n1,n2,n3 = 2*N1+1, 2*N2+1, 2*N3+1
    x = np.tile(np.arange(-N3,N3+1),n1*n2)
    y = np.tile(np.repeat(np.arange(-N2,N2+1),n3),n1)
    z = np.repeat(np.arange(-N1,N1+1),n2*n3)
    x,y,z = np.reshape(x,(-1,1)),np.reshape(y,(-1,1)),np.reshape(z,(-1,1))
    tmp = np.hstack((z,y))
    return np.hstack((tmp,x))


def refine_points(tetra,extend_S,C):
    n = np.shape(tetra)[0]
    tetra_cen = np.zeros((n,3))
    for ii in range(n):
        tetra_cen[ii] = np.mean(extend_S[tetra[ii]],axis=0)
    tetra_cen = [cen for cen in tetra_cen if min(np.linalg.norm(cen-extend_S,axis=1))>1.5]
    final_res = []
    for cen in tetra_cen:
        d = np.linalg.norm(cen-tetra_cen,axis=1)
        d = d[d>0]
        if min(d) > 1:
            final_res.append(cen)
    final_res = np.dot(final_res,np.linalg.inv(C))
    final_res = np.unique(np.round(final_res,decimals=3),axis=0)

    idx = np.sum((final_res <= 0.99) &(final_res >= 0.01),axis=1)
    idx = np.where(idx == 3)[0]
    return final_res[idx]


def wirite_poscar(cell,purity_atom,folder,idx):
    comment = 'POSCAR-' + purity_atom + '-defect'
    filename = '{:s}_id{:d}'.format(comment, idx)
    file = path.join('./'+folder, filename)
    write_vasp(cell,file)
