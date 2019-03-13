#!/bin/bash

module load vasp/5.4.4-impi-mkl
if [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
elif [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
fi

	source charge.sh

        charge_cal=`echo ${#q_charge[@]}`
	echo "We will calculate these charge_state in range of $charge_cal"
	potcar.sh
	sed -n '7p' POSCAR| awk 'BEGIN{RS=" "}{print $0}' >>temp_charge1
	awk '/ZVAL/{print $6}' POTCAR >>temp_charge2
	paste temp_charge1 temp_charge2 >temp_charge
	nelect=`awk '{s+=$1*$2}END{print s}' temp_charge`
	rm temp_charge*

        for ii in `seq $charge_cal`
        do
                nelect1=$[$nelect - ${q_charge[$[$ii-1]]}]
                mkdir -p NELECT_$nelect1
                cp POSCAR INCAR NELECT_$nelect1
                cd NELECT_$nelect1
                echo "NELECT=$nelect1" >>INCAR
                sed -i '/ISIF/c ISIF=2' INCAR
	
		if [ -n "$vdw" ] && [ $vdw -eq 1 ]
		then    cp /home/wyp/wyp/vtstscripts/Auto_cal_plot/bin/vdw_kernel.bindat ./
		fi

		Stru_optimation.sh
                scf_cal.sh
                cd ../
        done

