#!/bin/bash

module load vasp/5.4.4-impi-mkl
if [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
elif [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
fi

mkdir band/
cp scf/WAVECAR scf/CHG* scf/POTCAR scf/POSCAR scf/INCAR band
cd band
kpoints.sh band
sed -i -e '/ISTART/c ISTART=1' -e '/ISIF/c ISIF=2' -e '/ICHARG/c ICHARG=11'  INCAR

# module load vasp/5.4.4-impi-mkl
mpirun -n ${NSLOTS}  $vasp_version
cd ..
