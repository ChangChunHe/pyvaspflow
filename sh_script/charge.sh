#!/bin/bash

#Generate different charge state

if [ -f ../supcell.vasp ]
then	
	element.sh ../supcell.vasp POSCAR
else
	element.sh ../CONTCAR POSCAR          ######this function need out file#########
fi

        unset q_charge
        ele_c_num=`cat out|wc -l`
        charge_C=0

        for emm in `seq $ele_c_num`
        do
                ele_c=`awk -v emm=$emm 'NR==emm{print $1}' out`
                charge_c=`awk -v emm=$emm 'NR==emm{print $2}' out`

	#	if [ -n "`echo eval \$charge_{$ele_c}`" ]
	#	then	echo "there is something wrong!";exit	
	#	fi		

                eval ele_charge=\$charge_$ele_c
                charge_C=$[$charge_C + $charge_c * $ele_charge]
        done
	
	if [ $charge_C -eq 0 ]
	then 	q_charge=(0 -1 1);charge_C=0
	elif [ $charge_C -le -4 ] || [ $charge_C -ge 4 ]
	then	q_charge=(0 -2 -1 1 2);charge_C=0
	fi
	
	q_charge[0]=0
        q_num=1
        while [ $charge_C -gt 0 ]
        do
                q_charge[$q_num]=$charge_C;        charge_C=$[$charge_C-1];        q_num=$[$q_num+1]
        done

        q_num=1
        while [ $charge_C -lt 0 ]
        do
                q_charge[$q_num]=$charge_C;        charge_C=$[$charge_C+1];        q_num=$[$q_num+1]
        done

echo "We get the q_charge is ${q_charge[*]}"
