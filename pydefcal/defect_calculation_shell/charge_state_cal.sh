#!/bin/bash

# module load vasp/5.4.4-impi-mkl
if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi

if [ ! -z $1 ]
then dir=charge_state_$1;q=$1
else dir=charge_state_0;q=0;fi

if [ ! -d $dir  ]
then
mkdir $dir
fi
cp POSCAR POTCAR $dir
cd $dir
potcar.sh
incar.sh
kpoints.sh

if [ ! -f POSCAR ]
then echo "there is no POSCAR,please check your file name!"
exit;fi

if [ ! -f POTCAR ]
then echo "there is no POTCAR,please check your file name!"
exit;fi

awk 'NR==7' POSCAR |sed "s/^[ \t]*//"|tr -s ' '  '\n' > num_atom
grep ZVAL POTCAR |awk '{print $6}' > num_ele
paste num_atom num_ele > num_tmp
nelect=`awk '{s+=$1*$2}END{print s}' num_tmp`
rm num*

let nelect=nelect-q
sed -i -e '/ISIF/c ISIF=2' -e '/NSW/c NSW=60' INCAR
if grep NELECT INCAR ;
then  sed -i -e "/NELECT/c NELECT=$nelect" INCAR
else echo NELECT=$nelect >> INCAR
fi

mpirun -n ${NSLOTS} $vasp_version

mkdir scf
cp CONTCAR scf/POSCAR
cp POTCAR INCAR KPOINTS scf/
cd scf/

sed -i -e '/ISIF/c ISIF=2' -e '/NSW/c NSW=0' -e '/IBRION/c IBRION=-1' -e '/LWAVE/c LWAVE=T' -e '/LCHARG/c LCHARG=T' INCAR

#echo ISYM=-1>>INCAR
mpirun -n ${NSLOTS} $vasp_version

cd ../..
