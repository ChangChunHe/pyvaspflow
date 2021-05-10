import numpy as np
from sagar.toolkit.mathtool import refine_positions
from sagar.molecule.structure import Molecule
from sagar.crystal.utils import non_dup_hnfs, snf
from sagar.io.vasp import  write_vasp, read_vasp
from sagar.toolkit.derivetool import remove_redundant
from sagar.crystal.structure import Cell
from sagar.element.base import periodic_table_dict as ptd
from sagar.toolkit.mathtool import is_int_np_array
from sagar.crystal.derive import PermutationGroup as PG
from pyvaspflow.io.vasp_out import ExtractValue
from sagar.element.base import periodic_table_dict as ptd
from itertools import combinations
from os import path
import configparser


def refine_points(tetra,extend_S,C,min_d=1):
    n = np.shape(tetra)[0]
    tetra_cen = np.zeros((n,3))
    for ii in range(n):
        tetra_cen[ii] = np.mean(extend_S[tetra[ii]],axis=0)
    tetra_cen = [cen for cen in tetra_cen if min(np.linalg.norm(cen-extend_S,axis=1))>1.5]
    final_res = []
    for cen in tetra_cen:
        d = np.linalg.norm(cen-tetra_cen,axis=1)
        d = d[d>0]
        if min(d) > min_d:
            final_res.append(cen)
    if len(final_res) == 0:
        return np.array([])
    final_res = np.dot(final_res,np.linalg.inv(C))
    final_res = np.unique(np.round(final_res,decimals=3),axis=0)
    final_res[final_res>0.99] = 0
    final_res[final_res<0.01] = 0
    return np.unique(final_res,axis=0)


def write_poscar(cell,folder='.',idx=0,comment=""):
    filename = '{:s}{:d}'.format('POSCAR'+comment, idx)
    file = path.join(folder, filename)
    write_vasp(cell,file,suffix='')


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
              rm_atom,ii+1,'in the defect-free POSCAR has benn removed')
        with open('element-in-out','w') as f:
            f.writelines(str(rm_atom)+'='+str(1)+'\n')
            f.writelines('Vacc=-1 \n')
        return ii,d
    elif len(no_defect.atoms) == len(one_defect.atoms):
        no_def_atoms,def_atoms = np.unique(no_defect.atoms),np.unique(one_defect.atoms)
        purity_atom = np.setdiff1d(def_atoms,no_def_atoms)
        if len(purity_atom) != 0: # introduce a new atom purity
            idx = np.where(one_defect.atoms==purity_atom)[0]
            d = np.linalg.norm(one_def_pos[idx]-no_def_pos,axis=1)
            ii,d = np.argmin(d), np.min(d)
            for key,val in ptd.items():
                if val == no_defect.atoms[ii]:
                    rm_atom = key
                if val == purity_atom:
                    in_atom = key
            print('This is a purity defect','atom: \n',
                rm_atom, ii+1,'in the defect-free POSCAR has benn dopped by', in_atom)
            with open('element-in-out','w') as f:
                f.writelines(str(rm_atom)+'='+str(1)+'\n')
                f.writelines(str(in_atom)+'='+str(-1)+'\n')
            return ii,d
        else:
            purity_atom = []
            for _atom in no_def_atoms:
                idx_num_1,idx_num_2 = len(np.where(_atom==no_defect.atoms)[0]),len(np.where(_atom==one_defect.atoms)[0])
                if abs(idx_num_2-idx_num_1) == 1:
                    purity_atom.append(_atom)
                elif abs(idx_num_1-idx_num_2) > 1:
                    raise ValueError("The POSCAR has two or more defect atoms")
            if len(purity_atom) > 2:
                raise ValueError("The POSCAR has two or more defect atoms")
            no_def_pos_0 = no_def_pos[no_defect.atoms==purity_atom[0]]
            no_def_pos_1 = no_def_pos[no_defect.atoms==purity_atom[1]]

            one_def_pos_0 = one_def_pos[one_defect.atoms==purity_atom[0]]
            one_def_pos_1 = one_def_pos[one_defect.atoms==purity_atom[1]]

            if no_def_pos_0.shape[0]- one_def_pos_0.shape[0] == 1:
                purity_in = purity_atom[1]
                purity_out = purity_atom[0]
                d = [min(np.linalg.norm(pos-one_def_pos_0,axis=1)) for pos in no_def_pos_0]
                ahead_num = np.where(no_defect.atoms==purity_out)[0][0]
                idx = np.argmax(d)
                for key,val in ptd.items():
                    if val == purity_out:
                        rm_atom = key
                    if val == purity_in:
                        in_atom = key
                print('This is a purity defect','atom: \n',
                    rm_atom, ahead_num+idx+1,'in the defect-free POSCAR has benn dopped by', in_atom)
                with open('element-in-out','w') as f:
                    f.writelines(str(rm_atom)+'='+str(1)+'\n')
                    f.writelines(str(in_atom)+'='+str(-1)+'\n')
                return ahead_num+idx,d[idx]
            else:
                purity_in = purity_atom[0]
                purity_out = purity_atom[1]
                d = [min(np.linalg.norm(pos-one_def_pos_1,axis=1)) for pos in no_def_pos_1]
                idx = np.argmax(d)
                ahead_num = np.where(no_defect.atoms==purity_out)[0][0]
                # import pdb; pdb.set_trace()
                for key,val in ptd.items():
                    if val == purity_out:
                        rm_atom = key
                    if val == purity_in:
                        in_atom = key
                print('This is a purity defect','atom: \n',
                    rm_atom, ahead_num+idx+1,'in the defect-free POSCAR has benn dopped by', in_atom)
                with open('element-in-out','w') as f:
                    f.writelines(str(rm_atom)+'='+str(1)+'\n')
                    f.writelines(str(in_atom)+'='+str(-1)+'\n')
                return ahead_num+idx,d[idx]

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
    one_def_pos = np.dot(one_def_pos,c)
    ii,d = get_delete_atom_num(no_defect_poscar,one_defect_poscar)
    defect_atom = no_def_pos[ii]
    extend_S = []

    d,idx = np.zeros((no_def_pos.shape[0],27)),0
    for basis in all_basis:
        i,j,k = basis
        d[:,idx] = np.linalg.norm(defect_atom-(no_def_pos+i*c[0]+j*c[1]+k*c[2]),axis=1)
        idx += 1
    max_idx_no_def = np.argmax(np.min(d,axis=1))#no-defect-farther-atom-number
    # import pdb;pdb.set_trace()
    d,idx = np.zeros((one_def_pos.shape[0],27)),0
    for basis in all_basis:
        i,j,k = basis
        d[:,idx] = np.linalg.norm(defect_atom-(one_def_pos+i*c[0]+j*c[1]+k*c[2]),axis=1)
        idx += 1
    max_idx_one_def = np.argmax(np.min(d,axis=1))
    return max_idx_one_def+1,max_idx_no_def+1


def str_delimited(results, header=None, delimiter="\t"):
    """
    Given a tuple of tuples, generate a delimited string form.
    >>> results = [["a","b","c"],["d","e","f"],[1,2,3]]
    >>> print(str_delimited(results,delimiter=","))
    a,b,c
    d,e,f
    1,2,3
    Args:
        result: 2d sequence of arbitrary types.
        header: optional header
    Returns:
        Aligned string output in a table-like format.
    """
    returnstr = ""
    if header is not None:
        returnstr += delimiter.join(header) + "\n"
    return returnstr + "\n".join([delimiter.join([str(m) for m in result])
                                  for result in results])


def clean_lines(string_list, remove_empty_lines=True):
    for s in string_list:
        clean_s = s
        if '#' in s:
            ind = s.index('#')
            clean_s = s[:ind]
        clean_s = clean_s.strip()
        if (not remove_empty_lines) or clean_s != '':
            yield clean_s


def zread(filename):
    name, ext = path.splitext(filename)
    ext = ext.upper()
    if ext in (".GZ", ".Z"):
        with open(filename,'rb') as f:
            data = f.read()
        return unlzw(data).decode('utf-8')
    else:
        with open(filename,'r') as f:
            data = f.read()
        return data

def unlzw(data):
    """
    This function was adapted for Python from Mark Adler's C implementation
    https://github.com/umeat/unlzw
    Decompress compressed data generated by the Unix compress utility (LZW
    compression, files with .Z suffix). Input can be given as any type which
    can be 'converted' to a bytearray (e.g. string, or bytearray). Returns
    decompressed data as string, or raises error.
    Written by Brandon Owen, May 2016, brandon.owen@hotmail.com
    Adapted from original work by Mark Adler - orginal copyright notice below
    Copyright (C) 2014, 2015 Mark Adler
    This software is provided 'as-is', without any express or implied
    warranty.  In no event will the authors be held liable for any damages
    arising from the use of this software.
    Permission is granted to anyone to use this software for any purpose,
    including commercial applications, and to alter it and redistribute it
    freely, subject to the following restrictions:
    1. The origin of this software must not be misrepresented; you must not
    claim that you wrote the original software. If you use this software
    in a product, an acknowledgment in the product documentation would be
    appreciated but is not required.
    2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.
    3. This notice may not be removed or altered from any source distribution.
    Mark Adler
    madler@alumni.caltech.edu
    """

    # Convert input data stream to byte array, and get length of that array
    try:
        ba_in = bytearray(data)
    except ValueError:
        raise TypeError("Unable to convert inputted data to bytearray")

    inlen = len(ba_in)
    prefix = [None] * 65536  # index to LZW prefix string
    suffix = [None] * 65536  # one-character LZW suffix

    # Process header
    if inlen < 3:
        raise ValueError(
            "Invalid Input: Length of input too short for processing")

    if (ba_in[0] != 0x1f) or (ba_in[1] != 0x9d):
        raise ValueError(
            "Invalid Header Flags Byte: Incorrect magic bytes")

    flags = ba_in[2]

    if flags & 0x60:
        raise ValueError(
            "Invalid Header Flags Byte: Flag byte contains invalid data")

    max_ = flags & 0x1f
    if (max_ < 9) or (max_ > 16):
        raise ValueError(
            "Invalid Header Flags Byte: Max code size bits out of range")

    if (max_ == 9):
        max_ = 10  # 9 doesn't really mean 9

    flags &= 0x80  # true if block compressed

    # Clear table, start at nine bits per symbol
    bits = 9
    mask = 0x1ff
    end = 256 if flags else 255

    # Ensure stream is initially valid
    if inlen == 3:
        return 0  # zero-length input is permitted
    if inlen == 4:  # a partial code is not okay
        raise ValueError("Invalid Data: Stream ended in the middle of a code")

    # Set up: get the first 9-bit code, which is the first decompressed byte,
    # but don't create a table entry until the next code
    buf = ba_in[3]
    buf += ba_in[4] << 8
    final = prev = buf & mask  # code
    buf >>= bits
    left = 16 - bits
    if prev > 255:
        raise ValueError("Invalid Data: First code must be a literal")

    # We have output - allocate and set up an output buffer with first byte
    put = [final]

    # Decode codes
    mark = 3  # start of compressed data
    nxt = 5  # consumed five bytes so far
    while nxt < inlen:
        # If the table will be full after this, increment the code size
        if (end >= mask) and (bits < max_):
            # Flush unused input bits and bytes to next 8*bits bit boundary
            # (this is a vestigial aspect of the compressed data format
            # derived from an implementation that made use of a special VAX
            # machine instruction!)
            rem = (nxt - mark) % bits

            if (rem):
                rem = bits - rem
                if rem >= inlen - nxt:
                    break
                nxt += rem

            buf = 0
            left = 0

            # mark this new location for computing the next flush
            mark = nxt

            # increment the number of bits per symbol
            bits += 1
            mask <<= 1
            mask += 1

        # Get a code of bits bits
        buf += ba_in[nxt] << left
        nxt += 1
        left += 8
        if left < bits:
            if nxt == inlen:
                raise ValueError(
                    "Invalid Data: Stream ended in the middle of a code")
            buf += ba_in[nxt] << left
            nxt += 1
            left += 8
        code = buf & mask
        buf >>= bits
        left -= bits

        # process clear code (256)
        if (code == 256) and flags:
            # Flush unused input bits and bytes to next 8*bits bit boundary
            rem = (nxt - mark) % bits
            if rem:
                rem = bits - rem
                if rem > inlen - nxt:
                    break
                nxt += rem
            buf = 0
            left = 0

            # Mark this location for computing the next flush
            mark = nxt

            # Go back to nine bits per symbol
            bits = 9  # initialize bits and mask
            mask = 0x1ff
            end = 255  # empty table
            continue  # get next code

        # Process LZW code
        temp = code  # save the current code
        stack = []  # buffer for reversed match - empty stack

        # Special code to reuse last match
        if code > end:
            # Be picky on the allowed code here, and make sure that the
            # code we drop through (prev) will be a valid index so that
            # random input does not cause an exception
            if (code != end + 1) or (prev > end):
                raise ValueError("Invalid Data: Invalid code detected")
            stack.append(final)
            code = prev

        # Walk through linked list to generate output in reverse order
        while code >= 256:
            stack.append(suffix[code])
            code = prefix[code]

        stack.append(code)
        final = code

        # Link new table entry
        if end < mask:
            end += 1
            prefix[end] = prev
            suffix[end] = final

        # Set previous code for next iteration
        prev = temp

        # Write stack to output in forward order
        put += stack[::-1]

    # Return the decompressed data as string
    return bytes(bytearray(put))


def get_kw(attribute):
    kw = {}
    if attribute:
        if attribute[-1] == ",":
            attribute = attribute[:-1]
        attribute = attribute.split('=')
        n = len(attribute)
        if len(attribute[1].split(',')) == 2 :
            kw[attribute[0]] = attribute[1].split(',')[0]
        else:
            kw[attribute[0]] = attribute[1].split(',')[:-1]
        for ii in range(1,n-1):
            if len(attribute[ii+1].split(',')) == 2:
                kw[attribute[ii].split(',')[-1]] = attribute[ii+1].split(',')[0]
            else:
                kw[attribute[ii].split(',')[-1]] = attribute[ii+1].split(',')[:-1]
        if len(attribute[-1].split(',')) > 1:
            kw[attribute[-2].split(',')[-1]] = attribute[-1].split(',')
        else:
            kw[attribute[-2].split(',')[-1]] = attribute[-1]
        if 'kpts' in kw:
            kw['kpts'] = tuple(int(i) for i in kw['kpts'])
        if 'shift' in kw:
            kw['shift'] = tuple(float(i) for i in kw['shift'])
    return kw



def get_idx_in_pri_pos(pri_pos,pos):
    return [np.argmin(np.linalg.norm(p-pri_pos,axis=1)) for p in pos]

def _get_min_serial(perms,serial):
    return np.unique(np.sort(perms[:,serial],axis=1),axis=0)[0]


def is_2d_structure(cell):
    pos = cell.positions
    pos_std = np.std(pos,axis=0)
    if min(pos_std) < 0.1*max(pos_std):
        idx = np.argmin(pos_std)
        return True,idx
    return False

def get_grd_state(job_name,start_job_num,end_job_num):
    energy = []
    for ii in range(start_job_num,end_job_num+1):
        EV = ExtractValue(data_folder=job_name+str(ii))
        energy.append(EV.get_energy())
    return np.argmin(energy)

def get_perms(cell,str_type='crystal',symprec=1e-3):
    latt = cell.lattice
    pos = cell.positions
    pos = np.dot(pos,latt)
    if str_type == "crystal":
        symm = cell.get_symmetry()
        trans,rots = symm['translations'],symm['rotations']
        perms = np.zeros((np.shape(trans)[0],len(cell.atoms)))
        origin_positions = refine_positions(cell.positions)
        for ix, rot in enumerate(rots):
            for iy,o_pos in enumerate(origin_positions):
                new_pos = np.dot(rot,o_pos.T) + trans[ix]
                new_pos = np.mod(new_pos,1)
                new_pos = refine_positions(new_pos)
                idx = np.argmin(np.linalg.norm(new_pos-origin_positions,axis=1))
                perms[ix,iy] = idx
        perms_table = np.unique(perms,axis=0)
    else:
        mol = Molecule(pos,cell.atoms)
        perms_table = mol.get_symmetry_permutation(symprec)
    return perms_table

def add_log_shell_file(shell_file,log_dir,main_pid):
    with open(shell_file,"r") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if 'pyvasp run_' in line:
            line = line.rstrip()
            line += " -d "+log_dir + " -m " + str(main_pid)+"\n"
            new_lines.append(line)
        else:
            new_lines.append(line)
    return new_lines


def get_max_volume(pcell, sites, max_volume, min_volume=1, dimension=3, symprec=1e-5):
    for volume in range(min_volume, max_volume + 1):
        hnfs = non_dup_hnfs(pcell, volume, dimension, symprec)
        dict_trans = {}  # 记录已经产生过的snf，相同snf的平移操作相同。
        for h in hnfs:
            hfpg = PG(pcell, h)
            perms = hfpg.get_symmetry_perms(symprec)
            if dimension == 2:
                supercell = pcell.extend(h)._get_niggli_2D()
            else:
                supercell = pcell.extend(h)._get_niggli_3D()
            _sites = np.repeat(sites, volume, axis=0)
            for mol, _ in remove_redundant(supercell.positions, _sites, perms):
                c = Cell(supercell.lattice, mol[0], mol[1])
                if c.is_primitive(symprec):
                    yield c

def get_identity_atoms(cell,symprec,style="crystal"):
    atom_number = cell.atoms
    if style == "crystal":
        equ_atom = cell.get_symmetry(symprec)['equivalent_atoms']
        atom_uniq_type = np.unique(equ_atom)
        atom_type = np.zeros(np.shape(equ_atom))
        for idx,ea in enumerate(equ_atom):
            atom_type[idx] = np.where(atom_uniq_type==ea)[0]
    return atom_type


def read_config():
    from os import pardir
    home = path.expanduser("~")
    wd = path.abspath(pardir)
    if path.isfile(path.join(wd,'config.ini')):
        conf_file_path = path.join(wd,'config.ini')
    elif path.isfile(path.join(home,'.config','pyvaspflow','config.ini')):
        conf_file_path = path.join(home,'.config','pyvaspflow','config.ini')
    else:
        raise FileNotFoundError('cannot found config.ini in $HOME/.config/pyvaspflow or current direcroty')
    config = configparser.ConfigParser()
    config.read(conf_file_path)
    return config


def clean_parse(kw,key,def_val):
    val = kw.get(key,def_val)
    kw.pop(key,None)
    return val,kw
