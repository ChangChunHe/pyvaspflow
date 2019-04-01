import numpy as np
from sagar.io.vasp import  write_vasp, read_vasp
from os import path
from sagar.element.base import periodic_table_dict as ptd

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
    final_res[final_res>0.99] = 0
    final_res[final_res<0.01] = 0
    return np.unique(final_res,axis=0)


def wirite_poscar(cell,purity_atom='',folder='.',idx=0):
    if purity_atom == '':
        filename = 'POSCAR-idx-' + str(idx)
    else:
        comment = 'POSCAR-' + purity_atom + '-defect'
        filename = '{:s}_id{:d}'.format(comment, idx)
    file = path.join('./'+folder, filename)
    write_vasp(cell,file)


def get_delete_atom_num(no_defect_poscar,one_defect_poscar):
    no_defect = read_vasp(no_defect_poscar)
    one_defect = read_vasp(one_defect_poscar)
    no_def_pos = no_defect.positions
    one_def_pos = one_defect.positions
    no_def_pos[abs(no_def_pos-1) < 0.01] = 0
    one_def_pos[abs(one_def_pos-1) < 0.01] = 0
    if len(no_defect.atoms)-1 == len(one_defect.atoms):
        num = no_def_pos.shape[0]
        for ii in range(num):
            d = np.linalg.norm(no_def_pos[ii] - one_def_pos,axis=1)
            if min(d) > 0.1:
                break
        _no_def_pos = np.unique(np.delete(no_def_pos,ii,0),axis=0)
        _one_def_pos = np.unique(one_def_pos,axis=0)
        d = 0
        for i in _no_def_pos:
            d = d + min(np.linalg.norm(i - _one_def_pos,axis=1))
        for key,val in ptd.items():
            if val == no_defect.atoms[ii]:
                rm_atom = key
                break
        print('This is a vacancy defect','atom: \n',
              rm_atom,ii,'in the defect-free POSCAR has benn removed')
        with open('element-in-out','w') as f:
            f.writelines(str(rm_atom)+'='+str(1)+'\n')
            f.writelines('Vacc=-1 \n')
        return ii,d
    elif len(no_defect.atoms) == len(one_defect.atoms):
        no_def_atoms,def_atoms = np.unique(no_defect.atoms),np.unique(one_defect.atoms)
        purity_atom = np.setdiff1d(def_atoms,no_def_atoms)
        idx = np.where(one_defect.atoms==purity_atom)[0]
        d = np.linalg.norm(one_def_pos[idx]-no_def_pos,axis=1)
        ii,d = np.argmin(d), np.min(d)
        for key,val in ptd.items():
            if val == no_defect.atoms[ii]:
                rm_atom = key
            if val == purity_atom:
                in_atom = key
        print('This is a purity defect','atom: \n',
            rm_atom, ii,'in the defect-free POSCAR has benn dopped by', in_atom)
        with open('element-in-out','w') as f:
            f.writelines(str(rm_atom)+'='+str(1)+'\n')
            f.writelines(str(in_atom)+'='+str(-1)+'\n')
        return ii,d
    else:
        print('This kind of defect is not supported here right now')



def generate_all_basis(N1,N2,N3):
    n1,n2,n3 = 2*N1+1, 2*N2+1, 2*N3+1
    x = np.tile(np.arange(-N3,N3+1),n1*n2)
    y = np.tile(np.repeat(np.arange(-N2,N2+1),n3),n1)
    z = np.repeat(np.arange(-N1,N1+1),n2*n3)
    x,y,z = np.reshape(x,(-1,1)),np.reshape(y,(-1,1)),np.reshape(z,(-1,1))
    tmp = np.hstack((z,y))
    return np.hstack((tmp,x))


def get_farther_atom_num(no_defect_poscar, one_defect_poscar):
    '''
    Return:
     1: atom number of the farther atom in defect system
     2: atom number of the farther atom in defect-free system
    '''
    all_basis = generate_all_basis(1,1,1)
    no_defect = read_vasp(no_defect_poscar)
    one_defect = read_vasp(one_defect_poscar)
    no_def_pos = no_defect.positions
    one_def_pos = one_defect.positions
    c = no_defect.lattice
    no_def_pos = np.dot(no_def_pos,c)
    ii,d = get_delete_atom_num(no_defect_poscar,one_defect_poscar)
    defect_atom = no_def_pos[ii]
    d = []
    for i in range(no_def_pos.shape[0]):
        if i != ii:
            d.append([i, min([np.linalg.norm(defect_atom - (no_def_pos[i] \
                    + sum(c*basis))) for basis in all_basis])])
    d = np.asarray(d)
    max_idx = int(d[np.argmax(d[:,1]),0])
    d_ = np.linalg.norm(no_def_pos[max_idx] - np.dot(one_def_pos,c),axis=1)
    return np.argmin(d_)+1,max_idx+1
