#!/usr/bin/env python3

import numpy as np
import linecache as lc
import os,subprocess,click
import pyvaspflow.utils as us
from sagar.io.vasp import read_vasp, write_vasp
from pyvaspflow.io.vasp_out import ExtractValue, get_ele_sta
from pyvaspflow.defect_cal.defect_maker import DefectMaker
from pyvaspflow.vasp.prep_vasp import prep_single_vasp as psv
from pyvaspflow.vasp.run_vasp import run_single_vasp as rsv
from pyvaspflow.vasp.prep_vasp import prep_multi_vasp as pmv
from pyvaspflow.vasp.run_vasp import run_multi_vasp as rmv
from pyvaspflow.vasp.prep_vasp import write_incar as wi
from pyvaspflow.vasp.prep_vasp import write_kpoints as wk
from pyvaspflow.vasp import test_para
from pyvaspflow.defect_cal.defect_formation_energy import get_defect_formation_energy

@click.group()
def cli():
    '''
    you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation

    for more help
    '''
    pass


@cli.command('main',short_help="Get the value you want")
@click.option('--wd','-w',default='.')
@click.option('--attribute','-a', default='energy', type=str)
@click.option('--number','-n', default=1, type=int)
def main(wd, attribute,number):
    """
    Example:

    pyvasp main -a gap  # this can read the gap and vbm, cbm

    pyvasp main -a fermi  -w work_dir  # this can read the fermi energy, -w is your work directory

    pyvasp main -a energy  # this can read the total energy

    pyvasp main -a ele  # this can read the electrons in your OUTCAR

    pyvasp main -a ele-free  # this can get electrons number of  the defect-free system

    pyvasp main -a  Ewald  # this can get the Ewald energy of your system

    pyvasp main -a cpu  # this can get CPU time
    """

    EV = ExtractValue(wd)
    if 'gap' in attribute:
        get_gap(EV)
    elif 'fermi' in attribute:
        click.echo(EV.get_fermi())
    elif 'total' in attribute.lower() or 'energy' in attribute.lower():
        click.echo(EV.get_energy())
    elif 'ele' in attribute.lower() and 'free' in attribute.lower():
        click.echo(EV.get_Ne_defect_free())
    elif 'ele' in attribute.lower() and 'free' not in attribute.lower() and 'static' not in attribute.lower():
        click.echo(EV.get_Ne_defect())
    elif 'ima' in attribute or 'ewald' in attribute.lower():
        clikc.echo(EV.get_image())
    elif 'elect' in attribute and 'static' in attribute:
        outcar = os.path.join(wd,'OUTCAR')
        click.echo(str(number)+' '+str(get_ele_sta(outcar, number)))
    elif 'cpu' in attribute.lower():
        click.echo(EV.get_cpu_time())

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

    pyvasp cell -v 2 2 2 POSCAR
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

    pyvasp get_purity_poscar -i Vacc -o Si POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    DM.get_purity_defect(purity_out=purity_out,purity_in=purity_in,symprec=symprec,num=num)


@cli.command('get_tetrahedral',short_help="Get get tetrahedral sites of POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--purity_in','-i', default='H', type=str)
@click.option('--isunique','-u', default=False, type=bool)
@click.option('--min_d','-d',default=1.5,type=float)
def get_tetrahedral_poscar(poscar,purity_in,isunique,min_d):
    """
    argument:

    poscar, the  path of your initial POSCAR

    purity_in, the element you want to put into the system

    Example:

    pyvasp get_tetrahedral_poscar -i H  POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    DM.get_tetrahedral_defect(isunique=isunique,purity_in=purity_in,min_d=min_d)


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

    pyvasp symmetry -a space POSCAR # get space_group

    pyvasp symmetry -a translations POSCAR # get translations symmetry

    pyvasp symmetry -a rotations POSCAR # get rotations symmetry

    pyvasp symmetry -a equivalent POSCAR # get equivalent_atoms

    pyvasp symmetry -a primitive POSCAR # get primitive cell
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


@cli.command('incar',short_help="Prepare INCAR for vasp calculation")
@click.option('--attribute','-a', default='', type=str)
@click.option('--incar_file','-f', default=None, type=str)
def incar(attribute,incar_file):
    '''
    Example:

    pyvasp incar -f INCAR -a NSW=100,EDIFF=1e-6

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    wi(incar_file=incar_file,kw=us.get_kw(attribute))


@cli.command('kpoints',short_help="Prepare KPOINTS for vasp calculation")
@click.argument('poscar_file', metavar='<POSCAR_file_path>',nargs=1)
@click.option('--attribute','-a', default='', type=str)
def kpoints(poscar_file,attribute):
    '''
    Example:

    pyvasp incar -f KPOINTS -a NSW=100,EDIFF=1e-6

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    wk(poscar_file,kw=us.get_kw(attribute))


@cli.command('prep_single_vasp',short_help="Prepare necessary files for single vasp calculation")
@click.option('--poscar','-p', default='POSCAR', type=str)
@click.option('--attribute','-a', default='', type=str)
def prep_single_vasp(poscar,attribute):
    '''
    Example:

    pyvasp prep_single_vasp -p POSCAR -a functional=paw_LDA,sym_potcar_map=Zr_sv,NSW=100,style=band

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    psv(poscar=poscar,kw=us.get_kw(attribute))


@cli.command('run_single_vasp',short_help="run single vasp calculation")
@click.argument('job_name', metavar='<single_vasp_dir>',nargs=1)
@click.option('--is_login_node','-i',default=False,type=bool)
@click.option('--cpu_num','-n',default=20,type=int)
def run_single_vasp(job_name,is_login_node,cpu_num):
    '''
    Example:

    pyvasp run_ringle_vasp  task

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    rsv(job_name=job_name,is_login_node=is_login_node,cpu_num=cpu_num)


@cli.command('prep_multi_vasp',short_help="Prepare necessary files for multiple vasp calculation")
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1)
@click.option('--attribute','-a', default='', type=str)
@click.option('--start_job_num','-s', default=0, type=int)
def prep_multi_vasp(attribute,start_job_num,end_job_num):
    '''
    Example:

    pyvasp prep_multi_vasp -s 2  -a kppa=4000,node_name=super_q,cpu_num=12,job_name=struc_opt 20

    prepare multiple vasp task from POSCAR2 to POSCAR20

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    pmv(start_job_num,int(end_job_num),kw=us.get_kw(attribute))


@cli.command('run_multi_vasp',short_help="run single vasp calculation")
@click.argument('job_name', metavar='<job_name>',nargs=1)
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1)
@click.option('--start_job_num','-s', default=0, type=int)
@click.option('--par_job_num','-p', default=4, type=int)
def run_multi_vasp(job_name,end_job_num,start_job_num,par_job_num):
    '''
    Example:

    pyvasp run_multi_vasp -s 3 -p 6 task 20

    run multiple vasp task from task3 to task20 with 6 nodes in queue

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    rmv(job_name=job_name,end_job_num=end_job_num,
        start_job_num=start_job_num,par_job_num=par_job_num)


@cli.command('test_encut',short_help="test encut in vasp calculation")
@click.option('--poscar','-p', default='POSCAR')
@click.option('-start','-s', default=0.8,type=float)
@click.option('--end','-e', default=1.3,type=float)
@click.option('--step','-t', default=10,type=float)
@click.option('--attribute','-a', default='',type=str)
@click.option('--is_login_node','-i',default=False,type=bool)
def test_encut(poscar,start,end,step,attribute,is_login_node):
    '''
    Example:

    pyvasp test_encut -p POSCAR -s 0.8 -e 1.3 -t 30

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    tp = test_para.TestParameter(poscar=poscar)
    kw = {'start':start,'end':end,'step':step,'is_login_node':is_login_node}
    kw.update(us.get_kw(attribute))
    tp.test_encut(kw=kw)


@cli.command('test_kpts',short_help="test kpoints in vasp calculation")
@click.option('--poscar','-p', default='POSCAR')
@click.option('-start','-s', default=2000,type=int)
@click.option('--end','-e', default=4000,type=int)
@click.option('--step','-t', default=300,type=int)
@click.option('--attribute','-a', default='',type=str)
@click.option('--is_login_node','-i',default=False,type=bool)
def test_kpts(poscar,start,end,step,attribute,is_login_node):
    '''
    Example:

    pyvasp test_kpts -p POSCAR -s 1000 -e 3000 -t 200

    For more help you can refer to

    https://github.com/ChangChunHe/Defect-Formation-Calculation
    '''
    tp = test_para.TestParameter(poscar=poscar)
    kw = {'start':start,'end':end,'step':step,'is_login_node':is_login_node}
    kw.update(us.get_kw(attribute))
    tp.test_kpts(kw=kw)


@cli.command('diff_pos',short_help="judge two poscar are the same structures or not")
@click.argument('pri_pos', metavar='<primitive_poscar>',nargs=1)
@click.argument('pos1', metavar='<poscar1>',nargs=1)
@click.argument('pos2', metavar='<poscar2>',nargs=1)
@click.option('--symprec','-s',default=1e-3,type=float)
def diff_pos(pri_pos,pos1,pos2,symprec):
    '''
    This command you should support three poscar, the first one is the initial poscar.
    For example, your have a h-BN plane poscar, you substitute a boron atom by a sulfur atom,
    so you may have two or more sites to be substituted, then the fisrt parameter
    is the perfect h-BN plane, the second and third parameter are the two poscar
    you want to judge they are the same or not. If you get `True` means they are
    the same, `False` means they are not.

    There is one optional parameter, `symprec`, this is the precision you can
    specify, the default is 1e-3.

    Exmaple:

    pyvasp diff_pos POSCAR POSCAR1 POSCAR2
    '''
    click.echo(us.diff_poscar(pri_pos,pos1,pos2,symprec=symprec))


@cli.command('get_grd_state',short_help="get the ground state")
@click.argument('job_name', metavar='<your job name>',nargs=1)
@click.argument('end_job_num', metavar='<end job number>',nargs=1)
@click.option('--start_job_num','-s',default=0,type=int)
def get_grd_state(job_name,end_job_num,start_job_num):
    '''
    Exmaple:

    pyvasp get_grd_state task 100
    '''
    start_job_num,end_job_num = int(start_job_num),int(end_job_num)
    idx = us.get_grd_state(job_name,start_job_num=start_job_num,
               end_job_num=end_job_num)
    click.echo(str(idx))


@cli.command('get_def_form_energy',short_help="get defect formation energy")
@click.argument('data_dir', metavar='<your data main direcroty>',nargs=1)
@click.argument('defect_dirs', metavar='<your data defect calculation direcroty>',nargs=-1)
def get_def_form_energy(data_dir,defect_dirs):
    get_defect_formation_energy(data_dir,defect_dirs)


if __name__ == "__main__":
    cli()
