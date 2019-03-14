#!/bin/bash
module load sagar

extrinsic_c=(${extrinsic//\t/ });replace_c=(${replace//\t/ })

if [ -n "$1" ]
then	cp $1 supcell.vasp
elif [ ! -f supcell.vasp ]
then	exit
fi

FName='supcell.vasp'
ele_num=`awk 'NR==7{print NF}' $FName`
mkdir stru_cal
defect_num=1
for I in `seq $ele_num`
do
	for J in `seq $ele_num`
        do
        	if [ $I -eq $J ]
                then
                	ele1=`awk -v I=$I 'NR==6{print $I}' $FName`
                        ele2="Vacc"                                                #Vacancy
			defect_name[$defect_num]=Vac_$ele1
                        rexpand conf $FName -v 1 1 -e $ele1 -s $ele2 -n 1 -c Vac_$ele1 
                else
                        ele1=`awk -v I=$I 'NR==6{print $I}' $FName`             #Replace
                        ele2=`awk -v J=$J 'NR==6{print $J}' $FName`
                        rexpand conf $FName -v 1 1 -e $ele1 -s $ele2 -n 1 -c ${ele2}_${ele1}
			defect_name[$defect_num]=${ele2}_${ele1}
                fi
		defect_num=$[$defect_num+1]
        done
done

if [ -n "${extrinsic_c[*]}" ] && [ -n "${replace_c[*]}" ] && [ ${#extrinsic_c[*]} -eq  ${#replace_c[*]} ]			#extrinsic replace
then	
	for II in `seq ${#extrinsic_c[*]}` 
	do	
		rexpand conf $FName -v 1 1 -e ${replace_c[$[$II-1]]} -s ${extrinsic_c[$[II-1]]} -n 1 -c ${extrinsic_c[$[II-1]]}_${replace_c[$[$II-1]]}
		defect_name[$defect_num]=${extrinsic_c[$[II-1]]}_${replace_c[$[$II-1]]}
		defect_num=$[$defect_num+1]
	done
fi


mv *id*vasp stru_cal
echo ${defect_name[*]} >defect_name.out


