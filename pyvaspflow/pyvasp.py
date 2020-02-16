#!/usr/bin/env python3

import numpy as np
import linecache as lc
import os,subprocess,click,re,signal,logging
import pyvaspflow.utils as us
from sagar.io.vasp import read_vasp, write_vasp
from sagar.crystal.derive import cells_nonredundant
from pyvaspflow.io.vasp_out import ExtractValue, get_ele_sta
from pyvaspflow.defect_cal.defect_maker import DefectMaker
from pyvaspflow.vasp.prep_vasp import prep_single_vasp as psv
from pyvaspflow.vasp.run_vasp import run_single_vasp as rsv
from pyvaspflow.vasp.prep_vasp import prep_multi_vasp as pmv
from pyvaspflow.vasp.run_vasp import run_multi_vasp as rmv
from pyvaspflow.vasp.run_vasp import run_multi_vasp_with_shell as rmvws
from pyvaspflow.vasp.run_vasp import run_multi_vasp_without_job as rmvwj
from pyvaspflow.vasp.run_vasp import run_single_vasp_without_job as rsvwj
from pyvaspflow.vasp.prep_vasp import write_incar as wi
from pyvaspflow.vasp.prep_vasp import write_kpoints as wk
from pyvaspflow.defect_cal.defect_formation_energy import get_defect_formation_energy
from pyvaspflow.vasp import test_para
from pyvaspflow.io.vasp_out import read_doscar

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    '''
    you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/index.html

    for more help
    '''
    pass


def get_poscar_files(ctx, args, incomplete):
    if incomplete:
        return [k for k in os.listdir() if  k.startswith(incomplete)]
    else:
        return [k for k in os.listdir() if  (k.lower().startswith('poscar') \
        or k.endswith('vasp')) and os.path.isfile(k)]

def get_dir_name(ctx, args, incomplete):
    if incomplete:
        return [k for k in os.listdir() if  k.startswith(incomplete)]
    else:
        return [k for k in os.listdir() if os.path.isdir(k)]


@cli.command('gap',short_help="Get band gap and vbm cbm")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def gap(wd):
    EV = ExtractValue(wd)
    get_gap(EV)

@cli.command('fermi',short_help="Get fermi energy level")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def fermi(wd):
    EV = ExtractValue(wd)
    click.echo(EV.get_fermi())

@cli.command('energy',short_help="Get total energy")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def energy(wd):
    EV = ExtractValue(wd)
    click.echo(EV.get_energy())

@cli.command('electron_defect_free',short_help="Get electron number of defect free system")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def electron_defect_free(wd):
    EV = ExtractValue(wd)
    click.echo(EV.get_Ne_defect_free())

@cli.command('electron_number',short_help="Get electron number of current system")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def electron_number(wd):
    EV = ExtractValue(wd)
    click.echo(EV.get_Ne_defect())

@cli.command('ewald',short_help="Get ewald energy of current system")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def ewald(wd):
    EV = ExtractValue(wd)
    click.echo(EV.get_image())

@cli.command('electrostatic',short_help="Get electrostatic energy of current system")
@click.argument('number', type=int,nargs=1)
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def ewald(wd,number):
    outcar = os.path.join(wd,'OUTCAR')
    click.echo(': '.join(get_ele_sta(outcar, number)))

@cli.command('cpu',short_help="Get cpu time of current system")
@click.option('--wd','-w',default='.',help='your work direcroty',show_default=True,
type=click.Path(exists=True,resolve_path=True),autocompletion=get_dir_name)
def cpu(wd):
    EV = ExtractValue(wd)
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
    return [str(i) for i in tmp_line[2*col:2*col+2]]

def _get_line(file_tmp,rematch=None):
    grep_res = subprocess.Popen(['grep', rematch, file_tmp,'-n'],stdout=subprocess.PIPE)
    return [int(ii) - 1 for ii in subprocess.check_output(['cut','-d',':','-f','1'],stdin=grep_res.stdout).decode('utf-8').split()]


@cli.command('extend_spec_direc', short_help="Expanding  cell in specific direction")
@click.argument('pcell_filename', metavar='<cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True),
                autocompletion=get_poscar_files)
@click.option('--volume', '-v', nargs=3, type=int, metavar='<x> <y> <z>',default=(1,1,1),
              help="Expand cell to supercell of dismension <x> <y> <z>")
def extend_spec_direc(pcell_filename, volume):
    """
    First parameter: filename, the  path of your initial POSCAR

    Sencond parameter: volume, the volume you want to extend

    Example:

    pyvasp extend_spec_direc -v 2 2 2 POSCAR
    """
    pcell = read_vasp(pcell_filename)
    supcell = pcell.extend(np.diag(volume))
    write_vasp(supcell, 'supcell')


@cli.command('extend_spec_vol', short_help="Expanding primitive cell to specific range of volumes.")
@click.argument('pcell_filename', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True),
                autocompletion=get_poscar_files)
@click.option('--dimension', '-d', type=int, default=3,
              help="Dimension of the system, 2 for slab. Defalut=3 for crystal")
@click.option('--volume', '-v', nargs=2, type=int, metavar='<min> <max>',
              help="Expand primitive cell to supercell of volume <min> to <max>, set <min> as -1 for creating only <max> volume expanded supercells")
@click.option('--symprec', '-s', type=float, default=1e-5,
              help="Symmetry precision to decide the symmetry of primitive cell. Default=1e-5")
@click.option('--comprec', '-p', type=float, default=1e-5,
              help="Compare precision to judging if supercell is redundant. Defalut=1e-5")
@click.option('--verbose', '-vvv', is_flag=True, metavar='',
              help="Will print verbose messages.")
def extend_specific_volume(pcell_filename, dimension, volume, symprec, comprec, verbose):
    """
    <primitive_cell_file>  Primitive cell structure file, now only vasp POSCAR version5 supported.
    """
    pcell = read_vasp(pcell_filename)
    comment = 'cell'
    (min_v, max_v) = volume
    if min_v == -1:
        click.echo("Expanding primitive to volume {:d}".format(max_v))
        _export_supercell(pcell, comment, dimension, max_v, symprec, comprec, verbose)
    else:
        for v in range(min_v, max_v + 1):
            click.echo("Expanding primitive to volume {:d}".format(v))
            _export_supercell(pcell, comment, dimension, v, symprec, comprec, verbose)


def _export_supercell(pcell, comment, dimension, v, symprec, comprec, verbose):

    cells = cells_nonredundant(
        pcell, v, dimension, symprec=symprec, comprec=comprec)
    for idx, c in enumerate(cells):
        if verbose:
            print("    " + "No.{:d}: Processing".format(idx))
        filename = '{:s}_v{:d}_id{:d}'.format(comment, v, idx)
        write_vasp(c, filename)


@cli.command('get_point_defect',short_help="Get purity POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True),
                autocompletion=get_poscar_files)
@click.option('--doped_in', '-i', default='Vac', type=str, nargs=1,
help='the element you want to dope into the system')
@click.option('--doped_out', '-o', default='all', type=str, nargs=1,
help='the element you want to remove out of the system')
@click.option('--symprec', '-s', default='1e-3', type=float,
help='system precision')
@click.option('--num', '-n', default='1', type=str, nargs=1,
help='the number of elements you want to substitute')
def get_point_defect(poscar,doped_in,doped_out,num,symprec):
    """
    argument:

    poscar, the  path of your initial POSCAR

    doped_in, the element you want to put into the system

    doped_out, the element you want to remove out of the system

    Optional parameter:
    num: the number of element you want to put, the default is 1
    sympre: system precision

    Example:

    pyvasp get_point_defect -i Fe,Ti -o Si -n 2,3 POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    doped_out,doped_in,num = doped_out.split(','),doped_in.split(','),num.split(',')
    DM.get_point_defect(doped_in=doped_in,doped_out=doped_out,symprec=symprec,num=[int(i) for i in num])


@cli.command('get_mole_point_defect',short_help="Get purity POSCAR of molecule")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True),
                autocompletion=get_poscar_files)
@click.option('--doped_in', '-i', default='Vac', type=str, nargs=1,
help='the element you want to dope into the system')
@click.option('--doped_out', '-o', default='all', type=str, nargs=1,
help='the element you want to remove out of the system')
@click.option('--symprec', '-s', default='1e-3', type=float,
help='system precision')
@click.option('--num', '-n', default='1', type=str, nargs=1,
help='the number of elements you want to substitute')
def get_mole_point_defect(poscar,doped_in,doped_out,num,symprec):
    """
    argument:

    poscar, the  path of your initial POSCAR

    doped_in, the element you want to put into the system

    doped_out, the element you want to remove out of the system

    Optional parameter:
    num: the number of element you want to put, the default is 1
    sympre: system precision

    Example:

    pyvasp get_mole_point_defect -i Fe,Ti -o Si -n 2,3 POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    doped_in,num = doped_in.split(','),num.split(',')
    DM.get_mole_point_defect(doped_in=doped_in,doped_out=doped_out,symprec=symprec,num=[int(i) for i in num])



@cli.command('get_tetrahedral',short_help="Get get tetrahedral sites of POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True),
                autocompletion=get_poscar_files)
@click.option('--doped_in','-i', default='H', type=str,show_default=True)
@click.option('--isunique','-u', default=False, type=bool)
@click.option('--min_d','-d',default=1.5,type=float,show_default=True)
def get_tetrahedral_poscar(poscar,doped_in,isunique,min_d):
    """
    argument:

    poscar, the  path of your initial POSCAR

    doped_in, the element you want to put into the system

    Example:

    pyvasp get_tetrahedral_poscar -i H  POSCAR
    """
    DM = DefectMaker(no_defect=poscar)
    DM.get_tetrahedral_defect(isunique=isunique,doped_in=doped_in,min_d=min_d)


def get_symmetry_attr(ctx, args, incomplete):
    return [k for k in ['space_group','equivalent_atoms','primitive_cell'] if k.startswith(incomplete)]


@cli.command('symmetry',short_help="Get symmetry of POSCAR")
@click.argument('attr', type=str,autocompletion=get_symmetry_attr)
@click.argument('poscar', metavar='<cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True),
                autocompletion=get_poscar_files)
@click.option('--sympre','-s', default=1e-3, type=float)
def symmetry(poscar,attr,sympre):
    """
    argument:

    poscar, the  path of your initial POSCAR

    attr, the attribute you want to get

    Example:

    pyvasp symmetry  space POSCAR # get space_group

    pyvasp symmetry  equivalent POSCAR # get equivalent_atoms

    pyvasp symmetry  primitive POSCAR # get primitive cell
    """
    c = read_vasp(poscar)
    if 'space' in attr or 'group' in attr:
        print('Space group: ', c.get_spacegroup(sympre))
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
        if c.is_primitive():
            click.echo('This poscar is a primitive cell, or you can decrease symprec to try to get a primitive cell')
            return
        pc = c.get_primitive_cell(sympre)
        write_vasp(pc,'primitive_cell')


@cli.command('incar',short_help="Prepare INCAR for vasp calculation")
@click.option('--attribute','-a', default='', type=str)
@click.option('--incar_file','-f', default=None,
type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
def incar(attribute,incar_file):
    '''
    Example:

    pyvasp incar -f INCAR -a NSW=100,EDIFF=1e-6

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/incar.html
    '''
    wi(incar_file=incar_file,kw=us.get_kw(attribute))


@cli.command('kpoints',short_help="Prepare KPOINTS for vasp calculation")
@click.argument('poscar_file', type=str,autocompletion=get_poscar_files)
@click.option('--attribute','-a', default='', type=str)
def kpoints(poscar_file,attribute):
    '''
    Example:

    pyvasp kpoints POSCAR -a kppa=3000,style=gamma

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/kpoints.html
    '''
    wk(poscar_file,kw=us.get_kw(attribute))


@cli.command('prep_single_vasp',short_help="Prepare necessary files for single vasp calculation")
@click.argument('poscar', type=str, autocompletion=get_poscar_files)
@click.option('--attribute','-a', default='', type=str)
def prep_single_vasp(poscar,attribute):
    '''
    Example:

    pyvasp prep_single_vasp  POSCAR -a functional=paw_LDA,sym_potcar_map=Zr_sv,NSW=100,style=band

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/prepare.html#prep-single-vasp
    '''
    psv(poscar=poscar,kw=us.get_kw(attribute))


@cli.command('run_single_vasp',short_help="run single vasp calculation")
@click.argument('job_name', metavar='<single_vasp_dir>',nargs=1,autocompletion=get_dir_name)
@click.option('--is_login_node','-i',default=False,type=bool)
@click.option('--cpu_num','-n',default=24,type=int)
def run_single_vasp(job_name,is_login_node,cpu_num):
    '''
    Example:

    pyvasp run_ringle_vasp  task &

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#execute-single-vasp-task
    '''
    rsv(job_name=job_name,is_login_node=is_login_node,cpu_num=cpu_num)


@cli.command('run_single_vasp_without_job',short_help="run single vasp calculation")
@click.argument('job_name', metavar='<single_vasp_dir>',nargs=1,autocompletion=get_dir_name)
@click.option('--node_name','-nname',default="short_q",type=str)
@click.option('--cpu_num','-cnum',default='1',nargs=1,type=str)
@click.option('--node_num','-nnum',default=1,nargs=1,type=int)
@click.option('--cwd','-d',default="",nargs=1,type=str)
def run_single_vasp_without_job(job_name,node_name,cpu_num,node_num,cwd):
    '''
    Example:

    pyvasp run_ringle_vasp  task &

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#execute-single-vasp-task
    '''
#    import pdb;pdb.set_trace()
    node_name,cpu_num = node_name.split(','),cpu_num.split(',')
    if len(cpu_num) != len(node_name):
        raise ValueError("The length of node_name is not consistent with the length of cpu_num")
    rsvwj(job_name,node_name,cpu_num,node_num=1,cwd=cwd)



def get_prep_end_job_num(ctx, args, incomplete):
    dir_names = [i for i in os.listdir() if os.path.isfile(i)]
    prefix = 'POSCAR'
    max_num = []
    for dir_name in dir_names:
        if dir_name.startswith(prefix):
            res = re.search('\d+',dir_name)
            if res:
                max_num.append(int(float(res.group())))
    return [str(max(max_num))]

@cli.command('prep_multi_vasp',short_help="Prepare necessary files for multiple vasp calculation")
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1,autocompletion=get_prep_end_job_num)
@click.option('--attribute','-a', default='', type=str)
@click.option('--start_job_num','-s', default=0, type=int)
def prep_multi_vasp(attribute,start_job_num,end_job_num):
    '''
    Example:

    pyvasp prep_multi_vasp -s 2  -a kppa=4000,node_name=super_q,cpu_num=12,job_name=struc_opt 20

    prepare multiple vasp task from POSCAR2 to POSCAR20

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/prepare.html#prep-multi-vasp
    '''
    pmv(start_job_num,int(end_job_num),kw=us.get_kw(attribute))


@cli.command('prep_multi_vasp_from_file',short_help="Prepare necessary files for multiple vasp calculation")
@click.argument('job_list_file', metavar='<job list file>',nargs=1)
@click.option('--attribute','-a', default='', type=str)
def prep_multi_vasp_from_file(attribute,job_list_file):
    '''
    Example:

    pyvasp prep_multi_vasp_from_file -a kppa=4000,node_name=super_q,cpu_num=12,job_name=struc_opt job_list_file

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/prepare.html#prep-multi-vasp
    '''
    job_list = np.loadtxt(job_list_file,dtype=int)
    pmv(job_list=job_list,kw=us.get_kw(attribute))

def get_job_name(ctx, args, incomplete):
    dir_names = [i for i in os.listdir() if os.path.isdir(i)]
    prefix_list = []
    num_list = []
    if len(dir_names) == 0:
        return ["Not found any directory"]
    for dir_name in dir_names:
        res = re.match('([^\d]+?)(\d+)',dir_name)
        if res:
            prefix = res.groups()[0]
            num = 0
            for _dir_name in dir_names:
                if _dir_name.startswith(prefix):
                    num += 1
            prefix_list.append([prefix])
            num_list.append(num)
    return prefix_list[np.argmax(num_list)]

def get_run_end_job_num(ctx, args, incomplete):
    dir_names = [i for i in os.listdir() if os.path.isdir(i)]
    prefix_list = []
    num_list = []
    for dir_name in dir_names:
        res = re.match('([^\d]+?)(\d+)',dir_name)
        if res:
            prefix = res.groups()[0]
            num = 0
            for _dir_name in dir_names:
                if _dir_name.startswith(prefix):
                    num += 1
            prefix_list.append(prefix)
            num_list.append(num)
    prefix = prefix_list[np.argmax(num_list)]
    max_num = []
    for dir_name in dir_names:
        if dir_name.startswith(prefix):
            res = re.match('([^\d]+?)(\d+)',dir_name)
            if res:
                max_num.append(int(float(res.groups()[1])))
    return [str(max(max_num))]


@cli.command('run_multi_vasp',short_help="run multiple vasp calculations")
@click.argument('job_name', metavar='<job_name>',nargs=1,autocompletion=get_job_name)
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1,autocompletion=get_run_end_job_num)
@click.option('--start_job_num','-s', default=0, type=int)
@click.option('--par_job_num','-p', default=4, type=int)
def run_multi_vasp(job_name,end_job_num,start_job_num,par_job_num):
    '''
    Example:

    pyvasp run_multi_vasp -s 3 -p 6 task 20 &

    run multiple vasp task from task3 to task20 with 6 nodes in queue

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#execute-multiple-vasp-tasks
    '''
    rmv(job_name=job_name,end_job_num=end_job_num,
        start_job_num=start_job_num,par_job_num=par_job_num)


@cli.command('run_multi_vasp_from_shell',short_help="run multiple vasp calculations from shell scripts")
@click.argument('shell_file', metavar='<shell scripts file>',nargs=1)
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1,autocompletion=get_run_end_job_num)
@click.option('--work_name','-w', default='job', type=str)
@click.option('--start_job_num','-s', default=0, type=int)
@click.option('--par_job_num','-p', default=4, type=int)
def run_multi_vasp(work_name,shell_file,end_job_num,start_job_num,par_job_num):
    '''
    Example:

    nohup pyvasp run_multi_vasp_from_shell band.sh 9 -w job -p 5 1>std 2>err &

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#execute-multiple-vasp-tasks
    '''
    pwd = os.getcwd()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=os.path.join(pwd,'.run.log'),
                        filemode='a')
    rmvws(work_name,shell_file,end_job_num=end_job_num,start_job_num=start_job_num,job_list=None,par_job_num=par_job_num)


@cli.command('run_multi_vasp_without_job',short_help="run multiple vasp calculations without job files")
@click.argument('job_name', metavar='<job_name>',nargs=1,autocompletion=get_job_name)
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1,autocompletion=get_run_end_job_num)
@click.option('--node_num','-nnum',default=1,nargs=1,type=int)
@click.option('--node_name','-nname',default="short_q",type=str)
@click.option('--cpu_num','-cnum',default=24,type=str)
@click.option('--start_job_num','-s', default=0, type=int)
@click.option('--par_job_num','-p', default=4, type=int)
def run_multi_vasp_without_job(job_name,end_job_num,node_name,cpu_num,node_num,start_job_num,par_job_num):
    '''
    Example:

    pyvasp run_multi_vasp_without_job  task 5 --node_name  test_q --cpu_num 24

    run multiple vasp task from task0 to task5 through test_q node whith 24 cpu

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#run-multi-vasp-without-job
    '''
    node_name,cpu_num = node_name.split(','),cpu_num.split(',')
    if len(cpu_num) != len(node_name):
        raise ValueError("The length of node_name is not consistent with the length of cpu_num")
    rmvwj(job_name=job_name,end_job_num=end_job_num,node_name=node_name,cpu_num=cpu_num,
    node_num=node_num,start_job_num=start_job_num,par_job_num=par_job_num)



@cli.command('run_multi_vasp_from_file',short_help="run multiple vasp calculations from file")
@click.argument('job_name', metavar='<job_name>',nargs=1,autocompletion=get_job_name)
@click.argument('job_list_file', metavar='<job list file>',nargs=1)
@click.option('--par_job_num','-p', default=4, type=int)
def run_multi_vasp_from_file(job_name,job_list_file,par_job_num):
    '''
    Example:

    pyvasp run_multi_vasp  task job_list_file

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#run-multi-vasp-from-file
    '''
    job_list = np.loadtxt(job_list_file,dtype=int)
    rmv(job_name=job_name,job_list=job_list,par_job_num=par_job_num)


@cli.command('run_multi_vasp_without_job_from_file',short_help="run multiple vasp calculations")
@click.argument('job_name', metavar='<job_name>',nargs=1,autocompletion=get_job_name)
@click.argument('job_list_file', metavar='<job list file>',nargs=1)
@click.option('--node_num','-nnum',default=1,nargs=1,type=int)
@click.option('--node_name','-nname',default="short_q",nargs=1,type=str)
@click.option('--cpu_num','-cnum',default=24,nargs=1,type=str)
@click.option('--start_job_num','-s', default=0, type=int)
@click.option('--par_job_num','-p', default=4, type=int)
def run_multi_vasp_without_job_from_file(job_name,job_list_file,node_name,cpu_num,node_num,start_job_num,par_job_num):
    '''
    Example:

    pyvasp run_multi_vasp_without_job_from_file  task job_list_file --node_name  test_q --cpu_num 24

    run multiple vasp task from job_list_file through test_q node whith 24 cpu

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/execute.html#run-multi-vasp-without-job-from-file
    '''
    job_list = np.loadtxt(job_list_file,dtype=int)
    node_name,cpu_num = node_name.split(','),cpu_num.split(',')
    if len(cpu_num) != len(node_name):
        raise ValueError("The length of node_name is not consistent with the length of cpu_num")
    rmvwj(job_name=job_name,job_list=job_list,node_name=node_name,cpu_num=cpu_num,
    node_num=node_num,start_job_num=start_job_num,par_job_num=par_job_num)

@cli.command('test_encut',short_help="test encut in vasp calculation")
@click.argument('poscar', type=str, autocompletion=get_poscar_files)
@click.option('-start','-s', default=0.8,type=float)
@click.option('--end','-e', default=1.3,type=float)
@click.option('--step','-t', default=10,type=float)
@click.option('--attribute','-a', default='',type=str)
@click.option('--is_login_node','-i',default=False,type=bool)
def test_encut(poscar,start,end,step,attribute,is_login_node):
    '''
    Example:

    pyvasp test_encut  POSCAR -s 0.8 -e 1.3 -t 30

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/test_para.html#id2
    '''
    tp = test_para.TestParameter(poscar=poscar)
    kw = {'start':start,'end':end,'step':step,'is_login_node':is_login_node}
    kw.update(us.get_kw(attribute))
    tp.test_encut(kw=kw)


@cli.command('test_kpts',short_help="test kpoints in vasp calculation")
@click.argument('poscar', type=str, autocompletion=get_poscar_files)
@click.option('-start','-s', default=2000,type=int)
@click.option('--end','-e', default=4000,type=int)
@click.option('--step','-t', default=300,type=int)
@click.option('--attribute','-a', default='',type=str)
@click.option('--is_login_node','-i',default=False,type=bool)
def test_kpts(poscar,start,end,step,attribute,is_login_node):
    '''
    Example:

    pyvasp test_kpts  POSCAR -s 1000 -e 3000 -t 200

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/test_para.html#k
    '''
    tp = test_para.TestParameter(poscar=poscar)
    kw = {'start':start,'end':end,'step':step,'is_login_node':is_login_node}
    kw.update(us.get_kw(attribute))
    tp.test_kpts(kw=kw)


@cli.command('diff_pos',short_help="judge two poscar are the same structures or not")
@click.argument('pri_pos', metavar='<primitive_poscar>',nargs=1,autocompletion=get_poscar_files)
@click.argument('pos1', metavar='<poscar1>',nargs=1,autocompletion=get_poscar_files)
@click.argument('pos2', metavar='<poscar2>',nargs=1,autocompletion=get_poscar_files)
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

    For more help you can refer to

    https://pyvaspflow.readthedocs.io/zh_CN/latest/fetch.html#pyvasp-diff-pos
    '''
    click.echo(us.diff_poscar(pri_pos,pos1,pos2,symprec=symprec))


@cli.command('get_grd_state',short_help="get the ground state")
@click.argument('job_name', metavar='<your job name>',nargs=1,autocompletion=get_job_name)
@click.argument('end_job_num', metavar='<the last number of jobs>',nargs=1,autocompletion=get_run_end_job_num)
@click.option('--start_job_num','-s',default=0,type=int)
def get_grd_state(job_name,end_job_num,start_job_num):
    '''
    Exmaple:

    pyvasp get_grd_state task 100
    '''
    start_job_num,end_job_num = int(start_job_num),int(end_job_num)
    idx = us.get_grd_state(job_name,start_job_num=start_job_num,
               end_job_num=end_job_num)
    click.echo(str(idx+start_job_num))


@cli.command('get_def_form_energy',short_help="get defect formation energy")
@click.argument('data_dir', metavar='<your data main direcroty>',nargs=1,
autocompletion=get_dir_name)
@click.argument('defect_dirs', metavar='<your data defect calculation direcroty>',
nargs=-1,autocompletion=get_dir_name)
def get_def_form_energy(data_dir,defect_dirs):
    get_defect_formation_energy(data_dir,defect_dirs)

@cli.command('save_pdos',short_help="save your DOS to txt file")
@click.option('--wd','-w',default='.')
def save_pdos(wd):
    read_doscar(wd)

@cli.command('kill',short_help="kill the pyvasp and cancel jobs have been submitted")
@click.argument('pid', metavar='pid_of_pyvasp',nargs=1)
@click.option('--cancel_or_not','-c',default=True,type=bool)
def kill(pid,cancel_or_not):
    res = os.kill(int(pid),signal.SIGKILL)
    print(res,pid)
    job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(pid))
    with open(job_id_file,'r') as f:
        job_idx = f.readlines()
    if cancel_or_not:
        for idx in job_idx:
            os.system('scancel '+str(idx))
    os.remove(job_id_file)


if __name__ == "__main__":
    cli()
