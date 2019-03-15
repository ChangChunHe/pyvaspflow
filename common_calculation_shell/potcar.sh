#!/bin/bash
path_pbe="/opt/ohpc/pub/apps/vasp/pps/paw_PBE"
path_lda="/opt/ohpc/pub/apps/vasp/pps/paw_LDA"
path_pw="/opt/ohpc/pub/apps/vasp/pps/paw_PW91"
if  [ -z $1 ]
then	path=$path_pbe
echo using paw_PBE POTCAR
elif [ $1 -eq 1 ]
then	path=$path_pbe
echo using paw_PBE POTCAR
elif [ $1 -eq 2 ]
then 	path=$path_lda
echo using paw_LDA POTCAR
elif [ $1 -eq 3 ]
then	path=$path_pw
echo using paw_PW91 POTCAR
fi

if [ -f POTCAR ]
then
rm POTCAR
fi

# dos2unix POSCAR > /dev/null
ele_num=`awk 'NR==6{print NF}' POSCAR`
for i in `seq $ele_num`
do
ele=`awk -v i=$i 'NR==6{print $i}' POSCAR`
cat $path/$ele/POTCAR >> POTCAR
done
