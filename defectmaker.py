#!/usr/bin/env python3

import click,subprocess
from  defect_maker import DefectMaker


@click.group()
def cli():
    pass


@cli.command('get_purity',short_help="Get purity POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--purity_in','-i', default='Vacc', type=str)
@click.option('--purity_out','-o', default='all', type=str)
@click.option('--symprec','-s', default='1e-3', type=float)
def get_purity_poscar(poscar, purity_in, purity_out,symprec):
    DM = DefectMaker(no_defect=poscar)
    DM.get_purity_defect(purity_out=purity_out,purity_in=purity_in,symprec=symprec)


@cli.command('get_tetrahedral',short_help="Get get tetrahedral sites of POSCAR")
@click.argument('poscar', metavar='<primitive_cell_file>',
                type=click.Path(exists=True, resolve_path=True, readable=True, file_okay=True))
@click.option('--purity_in','-i', default='H', type=str)
@click.option('--isunique','-u', default=True, type=bool)
def get_tetrahedral_poscar(poscar,purity_in,isunique):
    DM = DefectMaker(no_defect=poscar)
    DM.get_tetrahedral_defect(isunique=isunique,purity_in=purity_in)


if __name__ == '__main__':
    cli()
