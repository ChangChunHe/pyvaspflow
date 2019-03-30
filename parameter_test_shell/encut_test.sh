#!/bin/bash

module load vasp/5.4.4-impi-mkl

if [  -f  POTCAR ]
then
max_encut=`grep ENMAX POTCAR |sort -k3nr|awk 'NR==1{print $3*1.6}' `
min_encut=`grep ENMAX POTCAR |sort -k3nr|awk 'NR==1{print $3*0.8}' `
else
echo No POTCAR found
fi


for val in `seq $min_encut 10 $max_encut`
do
incar.sh
sed -i -e '/NSW/c NSW=0'  -e "/ENCUT/c  ENCUT=$val" INCAR
stru_one_step.sh
echo $val `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> encut_energy.out
done
