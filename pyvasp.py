#!/usr/bin/env python3

import click
from defect_formation_energy import ExtractValue
from defect_formation_energy import get_ele_sta
import numpy as np
import utils as ft
import linecache as lc
from sagar.io.vasp import read_vasp, write_vasp
import os
from defect_maker import DefectMaker
from chemical_potential import plot_2d_chemical_potential_phase

@click.group()
def cli():
    pass


@cli.command('main',short_help="Get the value you want")
@click.argument('file_directory',metavar='<Work_directory>',
type=click.Path(exists=True))
@click.option('--attribute','-a', default='energy', type=str)
@click.option('--number','-n', default=1, type=int)
def main(file_directory, attribute,number):
    """
    First parameter:

    calculation directory, the dir path of your calculation

    Sencond parameter:

    this is an option, use this parameter to get some common
    value in your vasp outfiles

    Example:

    module load sagar #load the necessay package

    pyvasp.py main -a gap . # this can read the gap and vbm, cbm

    pyvasp.py main -a fermi . # this can read the fermi energy

    pyvasp.py main -a energy . # this can read the total energy

    pyvasp.py main -a ele . # this can read the electrons in your OUTCAR

    pyvasp.py main -a ele-free . # this can get electrons number of  the defect-free system

    pyvasp.py main -a  Ewald . # this can get the Ewald energy of your system
    """

    EV = ExtractValue(file_directory)
    if 'gap' in attribute:
        get_gap(EV)
    elif 'fermi' in attribute:
        get_fermi(EV)
    elif 'total' in attribute.lower() or 'energy' in attribute.lower():
        get_energy(EV)
    elif 'ele' in attribute.lower() and 'free' in attribute.lower():
        get_Ne_defect_free(EV)
    elif 'ele' in attribute.lower() and 'free' not in attribute.lower() and 'static' not in attribute.lower():
        get_Ne_defect(EV)
    elif 'ima' in attribute or 'ewald' in attribute.lower():
        get_Ewald(EV)
    elif 'elect' in attribute and 'static' in attribute:
        outcar=os.path.join(file_directory,'OUTCAR')
        click.echo('Electrostatic energy of '+str(number)+' atom is: '+str(get_ele_sta(outcar, number)))

def get_gap(EV):
    gap_res = EV.get_gap()
    if len(gap_res) == 3:
        click.echo('vbm: ' + str(gap_res[0])+
        '\ncbm: '+str(gap_res[1])+'\ngap: '+str(gap_res[2]))
    elif len(gap_res) == 2:
        click.echo('This is a spin system')
        click.echo('vbm_up: ' + str(gap_res[0][0])+
        '\ncbm_up: '+str(gap_res[0][1])+'\ngap_up: '+str(gap_res[0][2]))
        click.echo('vbm_down: ' + str(gap_res[1][0])+
        '\ncbm_down: '+str(gap_res[1][1])+'\ngap_down: '+str(gap_res[1][2]))

def get_fermi(EV):
    click.echo('fermi energy: '+str(EV.get_fermi()))

def get_energy(EV):
    click.echo('total energy: '+str(EV.get_energy()))

def get_Ne_defect_free(EV):
    click.echo('Number of valance electrons in defect free system: '
    +str(EV.get_Ne_defect_free()))

def get_Ne_defect(EV):
    click.echo('Number of valance electrons in your calculation system: '
    +str(EV.get_Ne_defect()))

def get_Ewald(EV):
    click.echo(EV.get_image())


@cli.command('get_PA',short_help='Get the potential alignment correlation')
@click.argument('no_defect_dir',nargs=1, metavar='no-defect-dir')
@click.argument('defect_dir',nargs=1,metavar='defect-dir')

def get_PA(no_defect_dir,defect_dir):
    """
    Noted that: you should do self-consistent-field calculation,
    so the no_defect_dir should have a subdirectory scf, and so as defect_dir

    First parameter: no_defect_dir, the directory path of the defece free system

    Sencond parameter: defect_dir, the directory path of defect_dir

    Example:

    module load sagar #load the necessay package

    pyvasp.py get_PA defect_free charge_state_1
    """
    num_def, num_no_def = ft.get_farther_atom_num(os.path.join(no_defect_dir,'CONTCAR'), \
            os.path.join(defect_dir,'POSCAR'))
    pa_def = get_ele_sta(os.path.join(defect_dir,'scf','OUTCAR'),num_def)[1]
    pa_no_def = get_ele_sta(os.path.join(no_defect_dir,'scf','OUTCAR'),num_no_def)[1]
    click.echo('Electrostatic of the farther atom '+str(num_def)+' from defect atom in defect system is: ')
    click.echo(pa_def)
    click.echo('Electrostatic of the farther atom '+str(num_no_def)+' from defect atom in defect-free system is: ')
    click.echo(pa_no_def)
    click.echo('Potential alignment correlation is: '+str(pa_def-pa_no_def))

def get_ele_sta(no_defect_outcar,number):
    number = int(number)
    tmp_match_line = _get_line(no_defect_outcar,rematch='electrostatic')
    rows = number // 5
    col =  number - rows * 5 - 1
    if col == -1:
        rows -= 1
        col = 4
    tmp_line = lc.getlines(no_defect_outcar)[tmp_match_line[0]+rows+3].split()
    return [float(i) for i in tmp_line[2*col:2*col+2]]

def _get_line(file_tmp,rematch=None):
    grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
    return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]


@cli.command('cell', short_help="Expanding primitive cell to specific range of volumes.")
@click.argument('pcell_filename', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--volume', '-v', nargs=3, type=int, metavar='<x> <y> <z>',default=(1,1,1),
              help="Expand cell to supercell of dismension <x> <y> <z>")

def cell(pcell_filename, volume):
    """
    First parameter: pcell_filename, the  path of your initial POSCAR

    Sencond parameter: volume, the volume you want to extend

    Example:

    module load sagar #load the necessay package

    pyvasp.py cell -v 2 2 2 POSCAR
    """
    pcell = read_vasp(pcell_filename)
    supcell = pcell.extend(np.diag(volume))
    write_vasp(supcell, 'supcell')



@cli.command('get_purity',short_help="Get purity POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--purity_in','-i', default='Vacc', type=str,help='the element you want to purity into the system')
@click.option('--purity_out','-o', default='all', type=str,help='the element you want to remove out of the system')
@click.option('--symprec','-s', default='1e-3', type=float,help='system precision')
@click.option('--num','-n', default=1, type=int,help='the number of elements you want to substitute')
def get_purity_poscar(poscar, purity_in, purity_out,num,symprec):
    """
    argument:

    poscar, the  path of your initial POSCAR

    purity_in, the element you want to put into the system

    purity_out, the element you want to drop out of the system

    Optional parameter:
    num: the number of element you want to put, the default is 1
    sympre: system precision

    Example:

    module load sagar #load the necessay package

    pyvasp.py get_purity_poscar -i Vacc -o Si POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    DM.get_purity_defect(purity_out=purity_out,purity_in=purity_in,symprec=symprec,num=num)


@cli.command('get_tetrahedral',short_help="Get get tetrahedral sites of POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--purity_in','-i', default='H', type=str)
@click.option('--isunique','-u', default=True, type=bool)
def get_tetrahedral_poscar(poscar,purity_in,isunique):
    """
    argument:

    poscar, the  path of your initial POSCAR

    purity_in, the element you want to put into the system

    Example:

    module load sagar #load the necessay package

    pyvasp.py get_tetrahedral_poscar -i H  POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    DM.get_tetrahedral_defect(isunique=isunique,purity_in=purity_in)



@cli.command('symmetry',short_help="Get symmetry of POSCAR")
@click.argument('poscar', metavar='<cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--attr','-a', default='space_group', type=str)
@click.option('--sympre','-s', default=1e-3, type=float)
def symmetry(poscar,attr,sympre):
    """
    argument:

    poscar, the  path of your initial POSCAR

    attr, the attribute you want to get

    Example:

    module load sagar #load the necessay package

    pyvasp.py symmetry -a space POSCAR # get space_group

    pyvasp.py symmetry -a translations POSCAR # get translations symmetry

    pyvasp.py symmetry -a rotations POSCAR # get rotations symmetry

    pyvasp.py symmetry -a equivalent POSCAR # get equivalent_atoms

    pyvasp.py symmetry -a primitive POSCAR # get primitive cell
    """
    c = read_vasp(poscar)
    if 'space' in attr or 'group' in attr:
        print('Space group: ', c.get_spacegroup(sympre))
    elif 'symme' in attr:
        print('Symmetry: ', c.get_symmetry(sympre))
    elif 'trans' in attr:
        print('Translations Symmetry: ', c.get_symmetry(sympre)['translations'])
    elif 'rotat' in attr:
        print('Rotations Symmetry: ', c.get_symmetry(sympre)['rotations'])
    elif 'equiv' in attr:
        equ_atom = c.get_symmetry(sympre)['equivalent_atoms']
        atom_type = np.unique(equ_atom)
        atom_species,k = {},1
        for ii in atom_type:
            atom_species[k] = np.where(equ_atom==ii)[0]+1
            k += 1
        for key, val in atom_species.items():
            print(key,val)
    elif 'primi' in attr:
        pc = c.get_primitive_cell(sympre)
        write_vasp(pc,'primitive_cell')

@cli.command('chem_pot',short_help="Get chemical potential phase figure")
@click.argument('chem_incar', metavar='<chemical-incar-file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--remove','-r', default=0, type=int)
def chem_pot(chem_incar,remove):
    '''
    argument:

    chem_incar, some necessay compound energy

    remove, the dismension you want to remove

    Example:

    module load sagar #load the necessay package

    pyvasp.py chem_pot chem_incar # get space_group
    '''
    plot_2d_chemical_potential_phase(chem_incar,remove)
if __name__ == "__main__":
    cli()
