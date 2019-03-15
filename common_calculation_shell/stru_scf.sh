#!/bin/bash

module load vasp/5.4.4-impi-mkl

if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi

if [ ! -d scf ]
then    mkdir scf;fi

cp  INCAR CONTCAR POTCAR scf/
cd scf/
mv CONTCAR POSCAR

kpoints.sh 50 # make KPOINTS denser
sed -i -e '/ISIF/c ISIF=2' -e '/NSW/c NSW=0' -e '/IBRION/c IBRION=-1' -e '/LWAVE/c LWAVE=T' -e '/LCHARG/c LCHARG=T' INCAR

mpirun -n ${NSLOTS} $vasp_version
cd ..
