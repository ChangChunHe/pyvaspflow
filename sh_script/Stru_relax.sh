#!/bin/bash

module load vasp/5.4.4-impi-mkl
if [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
elif [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
fi

        if [ ! -f POSCAR ]
        then echo "there is no POSCAR,please check your file name!";exit;fi
        potcar.sh
        incar.sh
        kpoints.sh
        sed -i -e '/ISIF/c ISIF=3' -e '/NSW/c NSW=60' INCAR

if [ -n "$vdw" ] && [ $vdw -eq 1 ]
then    cp /home/wyp/wyp/vtstscripts/Auto_cal_plot/bin/vdw_kernel.bindat ./
fi

        mpirun -n ${NSLOTS} $vasp_version

