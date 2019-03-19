#!usr/bin/env python3

import click,subprocess
from defect_cal import ExtractValue
from sagar.io.vasp import  read_vasp
import numpy as np
import function_toolkit as ft
import linecache as lc

@click.group()
def cli():
    pass

@cli.command('main')
@click.argument('file_directory')
@click.option('--attribute','-a', default='')
def main(file_directory, attribute):
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

def get_gap(EV):
    gap_res = EV.get_gap()
    import pdb;pdb.set_trace()
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

@cli.command('get_delete_atom_num')
@click.argument('no_defect_poscar',nargs=1)
@click.argument('one_defect_poscar',nargs=1)
def get_delete_atom_num(no_defect_poscar,one_defect_poscar):
    ii,d = ft.get_delete_atom_num(no_defect_poscar,one_defect_poscar)
    print('Delete the',str(ii+1),'atom in your no-defect  POSCAR,\n the two distance between the two POSCAR is',d)


@cli.command('get_farther_atom_num')
@click.argument('no_defect_poscar',nargs=1)
@click.argument('one_defect_poscar',nargs=1)
def get_farther_atom_num(no_defect_poscar,one_defect_poscar):
    ft.get_farther_atom_num(no_defect_poscar,one_defect_poscar)


@cli.command('get_potential_align')
@click.argument('defect_outcar',nargs=1)
@click.argument('number',nargs=1)
def get_PA(defect_outcar,number):
    # get potential alignment correlation
    number = int(number)
    tmp_match_line = _get_line(defect_outcar,rematch='electrostatic')
    rows = number // 5
    col =  number - rows * 5 - 1
    if col == -1:
        rows -= 1
        col = 4
    tmp_line = lc.getlines(defect_outcar)[tmp_match_line[0]+rows+3].split()
    click.echo([float(i) for i in  tmp_line[2*col:2*col+2]])

def _get_line(file_tmp,rematch=None):
    grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
    return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]

if __name__ == "__main__":
    cli()
