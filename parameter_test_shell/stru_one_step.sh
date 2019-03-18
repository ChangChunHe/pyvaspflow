#!/bin/bash

module load vasp/5.4.4-impi-mkl
if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi

if [ ! -f POSCAR ]
then echo "there is no POSCAR,please check your file name!";break;fi


potcar.sh
incar.sh
kpoints.sh
sed -i -e '/ISIF/c ISIF=2' -e '/NSW/c NSW=0' INCAR

mpirun -n ${NSLOTS} $vasp_version

