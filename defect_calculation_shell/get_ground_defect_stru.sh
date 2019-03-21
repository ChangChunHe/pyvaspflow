#!/bin/bash

if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi

for ii in `ls`
do
if [[ $ii == *"POSCAR"*  ]]
then
a=$ii
mkdir $ii-cal
cp $ii $ii-cal/POSCAR
cd $ii-cal
potcar.sh
kpoints.sh
incar.sh
stru_relax.sh
echo $ii `tail -1 OSZICAR |awk '{print $5}'`  >> energy_out
cd ..
fi
done
ground_stru_num=`cat energy_out|sort -nk2r|head -1|awk '{print $1}'`
b=`echo $a |cut -d'_' -f 1`
mv ${b}_idx${ground_stru_num}.vasp POSCAR_ground_stru # this is the ground state
