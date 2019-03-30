#!/bin/bash
path_pbe="/opt/ohpc/pub/apps/vasp/pps/paw_PBE"
path_lda="/opt/ohpc/pub/apps/vasp/pps/paw_LDA"
path_pw="/opt/ohpc/pub/apps/vasp/pps/paw_PW91"
path_uslda="/opt/ohpc/pub/apps/vasp/pps/USPP_LDA"
path_uspw="/opt/ohpc/pub/apps/vasp/pps/USPP_PW91"
if [ -f POTCAR ]
then
exit;fi

if  [ -z $1 ]
then	path=$path_pbe
echo using paw_PBE POTCAR
else
if [[ $1 =~ ^-?[0-9]+$ ]]
then

if [ $1 -eq 1 ]
then	path=$path_pbe
echo using paw_PBE POTCAR
elif [ $1 -eq 2 ]
then 	path=$path_lda
echo using paw_LDA POTCAR
elif [ $1 -eq 3 ]
then	path=$path_pw
echo using paw_PW91 POTCAR
elif [ $1 -eq 4 ]
then	path=$path_uslda
echo using USPP_LDA POTCAR
elif [ $1 -eq 5 ]
then	path=$path_uspw
echo using USPP_PW91 POTCAR
fi
else
path=$path_pbe
fi

tmp="$@"
tmp=$(printf '%s\n' "${tmp//[[:digit:]]/}")
IFS=',' read -a pot_type <<< $tmp
fi


perl -i -p -e "s/\r//" POSCAR

ele_num=`awk 'NR==6{print NF}' POSCAR`

for i in `seq $ele_num`
do
ele=`awk -v i=$i 'NR==6{print $i}' POSCAR`


is_write=false
echo $pot_type
for pot_ty in $pot_type
do

if [[ $pot_ty =~ .*${ele}.* ]]
then
  if [ -e  ${path}/${pot_ty}/POTCAR ]
  then
    cat ${path}/${pot_ty}/POTCAR >> POTCAR
    echo ${path}/${pot_ty}/POTCAR   
  is_write=true
  elif [ -e ${path}/${pot_ty}/POTCAR.Z ]
  then 
    cp  ${path}/${pot_ty}/POTCAR.Z .
    gzip -d < POTCAR.Z >tmp
    cat POTCAR tmp >> POTCAR
    rm POTCAR.Z tmp
    echo ${path}/${pot_ty}/POTCAR.Z
    is_write=true
  fi
break
fi

done

if  ! $is_write
then

if [ -f ${path}/${ele}/POTCAR   ]
then 
cat ${path}/${ele}/POTCAR >> POTCAR
elif [ -f  ${path}/${ele}/POTCAR.Z   ]
then
 cp  ${path}/${ele}/POTCAR.Z .
    gzip -d < POTCAR.Z >tmp
    cat POTCAR tmp >> POTCAR
    rm POTCAR.Z tmp
fi
fi

done
