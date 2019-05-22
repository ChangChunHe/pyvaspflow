#!/bin/bash
# make sure you have install pyvasp in your current environment
# make sure current directory has POSCAR

pyvasp prep_single_vasp -a ISIF=3,job_name=stru_relax
pyvasp run_single_vasp stru_relax
pyvasp prep_single_vasp -p stru_relax/CONTCAR -a kppa=4000,job_name=scf,NSW=0
pyvasp run_single_vasp scf
pyvasp prep_single_vasp -p scf/CONTCAR -a kppa=8000,ISMEAR=-5,job_name=dos,NSW=0
pyvasp run_single_vasp dos
