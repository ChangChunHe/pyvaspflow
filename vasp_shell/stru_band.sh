#!/bin/bash

if [ ! -d band ]
then
mkdir band/
fi
cp scf/WAVECAR scf/CHG* scf/POTCAR scf/POSCAR scf/INCAR band
cd band
kpoints.sh band $1
sed -i -e '/ISTART/c ISTART=1' -e '/ISIF/c ISIF=2' -e '/ICHARG/c ICHARG=11'  INCAR

# module load vasp/5.4.4-impi-mkl
mpirun -n ${NSLOTS}  vasp_std
rm CHG*
cd ..
