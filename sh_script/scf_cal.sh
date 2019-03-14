#!/bin/bash

module load vasp/5.4.4-impi-mkl

if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi

if [ ! -d scf ]
then    mkdir scf;fi

cp KPOINTS INCAR CONTCAR POTCAR scf/
cd scf/
mv CONTCAR POSCAR
incar.sh
potcar.sh
#kpoints.sh
sed -i -e '/ISIF/c ISIF=2' -e '/NSW/c NSW=0' -e '/IBRION/c IBRION=-1' -e '/LWAVE/c LWAVE=T' -e '/LCHARG/c LCHARG=T' INCAR

if [ -n "$vdw" ] && [ $vdw -eq 1 ]
then	cp /home/wyp/wyp/vtstscripts/Auto_cal_plot/bin/vdw_kernel.bindat ./;fi

mpirun -n ${NSLOTS} $vasp_version
cd ..

