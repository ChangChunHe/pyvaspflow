#!/usr/bin/env python3

import click,subprocess
from defect_cal import ExtractValue
from sagar.io.vasp import  read_vasp
import numpy as np
import function_toolkit as ft
import linecache as lc
from sagar.io.vasp import read_vasp, write_vasp
import os


@click.group()
def cli():
    pass


@cli.command('main',short_help="Get the value you want")
@click.argument('file_directory',metavar='<Work_directory>',
type=click.Path(exists=True))
@click.option('--attribute','-a', default='energy', type=str)

def main(file_directory, attribute):
    """
    First parameter:

    calculation directory, the dir path of your calculation

    Sencond parameter:

    this is an option, use this parameter to get some common
    value in your vasp outfiles

    Example:

    module load sagar #load the necessay package

    vaspout.py main -a gap . # this can read the gap and vbm, cbm

    vaspout.py main -a fermi . # this can read the fermi energy

    vaspout.py main -a energy . # this can read the total energy

    vaspout.py main -a ele . # this can read the electrons in your OUTCAR

    vaspout.py main -a ele-free . # this can get electrons number of  the defect-free system

    vaspout.py main -a  Ewald . # this can get the Ewald energy of your system
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
    elif 'ele' in attribute.lower() and 'free' not in attribute.lower():
        get_Ne_defect(EV)
    elif 'ima' in attribute or 'ewald' in attribute.lower():
        get_Ewald(EV)

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
@click.argument('no_defect',nargs=1, metavar='no-defect-dir')
@click.argument('defect_dir',nargs=1,metavar='defect-dir')

def get_PA(no_defect_dir,defect_dir):
    """
    First parameter: no_defect_dir, the directory path of the defece free system

    Sencond parameter: defect_dir, the directory path of defect_dir

    Example:

    module load sagar #load the necessay package

    vaspout.py get_PA defect_free/POSCAR charge_state_1
    """
    num_def, num_no_def = ft.get_farther_atom_num(os.path.join(no_defect_dir,'POSCAR'), \
            os.path.join(defect_dir,'POSCAR'))
    pa_def = get_ele_sta(os.path.join(defect_dir,'OUTCAR'),num_def)
    pa_no_def = get_ele_sta(os.path.join(no_defect_dir,'OUTCAR'),num_no_def)
    click.echo('Electrostatic of the farther atom from defect atom in defect system is: ')
    click.echo(pa_def)
    click.echo('Electrostatic of the farther atom from defect atom in defect-free system is: ')
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
    return float(tmp_line[2*col+1])

def _get_line(file_tmp,rematch=None):
    grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
    return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]


@cli.command('cell', short_help="Expanding primitive cell to specific range of volumes.")
@click.argument('pcell_filename', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--volume', '-v', nargs=3, type=int, metavar='<x> <y> <z>',default=(1,1,1),
              help="Expand cell to supercell of dismension <x> <y> <z>")

def cell(pcell_filename, volume):
    pcell = read_vasp(pcell_filename)
    supcell = pcell.extend(np.diag(volume))
    write_vasp(supcell, 'supcell')



if __name__ == "__main__":
    cli()
