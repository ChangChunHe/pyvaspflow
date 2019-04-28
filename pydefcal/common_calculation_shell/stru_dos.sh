#!/bin/bash -l

if [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
elif [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
fi

if [ ! -d dos ]
then    mkdir dos;fi

cp scf/CHG* scf/WAVECAR scf/INCAR scf/POTCAR scf/KPOINTS scf/CONTCAR dos/
cd dos/
mv CONTCAR POSCAR
echo "LORBIT = 11" >>INCAR
sed -i -e '/ISIF/c ISIF=2' -e '/NSW/c NSW=0' -e '/IBRION/c IBRION=-1' -e '/LWAVE/c LWAVE=T' -e '/LCHARG/c LCHARG=T' -e '/ICHARG/c ICHARG=11' -e '/ISMEAR/c ISMEAR=-5' INCAR

sed -i "4s/.*/`awk 'NR==4 {print $1+4,$2+4,$3+4}' KPOINTS`/" KPOINTS
# module load vasp/5.4.4-impi-mkl
mpirun -n ${NSLOTS} vasp_std

cd ..

