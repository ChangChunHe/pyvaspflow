#!/bin/bash
# make sure you have install pyvasp in your current environment
# make sure current directory has POSCAR

module load pyvaspflow # we make a module in our server


pyvasp prep_single_vasp POSCAR -a ISIF=3,job_name=stru_relax
pyvasp run_single_vasp stru_relax
pyvasp prep_single_vasp  stru_relax/CONTCAR -a kppa=4000,job_name=scf,NSW=0,LCHARG=True
pyvasp run_single_vasp scf
pyvasp prep_single_vasp  scf/CONTCAR -a kppa=8000,ISMEAR=-5,job_name=dos,NSW=0,LORBIT=11
cp scf/CHG* dos/
pyvasp run_single_vasp dos
