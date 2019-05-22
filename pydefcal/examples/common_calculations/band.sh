#!/bin/bash
# make sure you have install pyvasp in your current environment
# make sure current directory has POSCAR

pyvasp prep_single_vasp -a ISIF=3,job_name=stru_relax
pyvasp run_single_vasp stru_relax
pyvasp prep_single_vasp -p stru_relax/CONTCAR -a job_name=scf,NSW=0,LCHARG=True
pyvasp run_single_vasp scf
pyvasp prep_single_vasp -p scf/CONTCAR -a style=band,NSW=0,job_name=band,ICHARG=11
cp scf/CHG* band/
pyvasp run_single_vasp band
