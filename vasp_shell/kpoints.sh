#!/bin/bash

if [ ! -n "$k_max" ];then	k_max=30;fi
if [ ! -n "$inter_num" ];then	inter_num=30;fi

if [ -f KPOINTS ]
then
exit
fi


if [[ $1 == "ba"* ]]
then
aflow --kpath<POSCAR> k-path
kpts_start=`awk "/KPOINTS/{print NR}" k-path`
let kpts_start++
kpts_end=`awk "/END/{print NR}" k-path`
let kpts_end--
for i in `seq $kpts_start 1 $kpts_end`
do
awk -v j=$i 'NR==j {print}' k-path >> KPOINTS
done
rm k-path

else

if [[ $1 =~ ^-?[0-9]+$ ]]
then
k_max=$1
fi

cons=`awk 'NR==2{print $1}' POSCAR`
for iii in 1 2 3
do
k[$iii]=`awk -v k_max=$k_max -v iii=$iii -v cons=$cons 'NR==(2+iii){printf "%d\n",k_max/cons/($1^2+$2^2+$3^2)^0.5}' POSCAR`
done
cat > KPOINTS <<!
KPOINTS
0
G
${k[*]}
0 0 0
!
fi
