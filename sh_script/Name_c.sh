#!/bin/bash
	repeat_num=1
	error_num=1
        for i in defect_*
        do
		rm out
		name_d=`grep System INCAR |awk '{if(NF==1){print substr($1,8)}else{print $NF}}'`
		if [ "$name_d" != "test" ]
		then	mv $i "$name_d"_defect;continue;fi

                element.sh CONTCAR $i/POSCAR
                ele_c_num=`cat out|wc -l`

                if [ $ele_c_num -eq 1 ]
                then
                        c_value=`awk '{print $2}' out`
                        if [ $c_value -gt 0 ]
                        then
                                c_atom=`awk '{print $1}' out`
                                if [ -d "$c_atom"_i_defect ]
                                then    mv $i "$c_atom"_i_defect"$repeat_num";repeat_num=$[$repeat_num+1]
                                else    mv $i "$c_atom"_i_defect;fi
                        else
                                c_atom=`awk '{print $1}' out`
                                if [ -d V_"$c_atom"_defect ]
                                then    mv $i Vac_"$c_atom"_defect"$repeat_num";repeat_num=$[$repeat_num+1]
                                else    mv $i Vac_"$c_atom"_defect;fi
                        fi
                else
                                c1_value=`awk 'NR==1{print $2}' out`
                                c2_value=`awk 'NR==2{print $2}' out`
                        if [ $c1_value -gt $c2_value ]
                        then
                                c1_atom=`awk 'NR==1{print $1}' out`
                                c2_atom=`awk 'NR==2{print $1}' out`
                                if [ -d "$c1_atom"_"$c2_atom"_defect ]
                                then    mv $i "$c1_atom"_"$c2_atom"_defect"$repeat_num";repeat_num=$[$repeat_num+1]
                                else    mv $i "$c1_atom"_"$c2_atom"_defect;fi
                        else
                                c1_atom=`awk 'NR==1{print $1}' out`
                                c2_atom=`awk 'NR==2{print $1}' out`
                                if [ -d "$c2_atom"_"$c1_atom"_defect ]
                                then    mv $i "$c2_atom"_"$c1_atom"_defect"$repeat_num";repeat_num=$[$repeat_num+1]
                                else    mv $i "$c2_atom"_"$c1_atom"_defect;fi
                        fi
                fi
        done

