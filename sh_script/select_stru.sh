#!/bin/bash

module load vasp/5.4.4-impi-mkl
defect_name=`awk '{print}' defect_name.out`
if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi

	mkdir poscar
        cp INCAR stru_cal
        cd stru_cal
        for name in ${defect_name[*]}
        do
echo $name
                for ii in $name*
                do
echo $ii
                        cp $ii POSCAR
                        kpoints.sh
			rm POTCAR
                        sed -i '4c 1 1 1' KPOINTS
                        Stru_optimation.sh
                        echo $ii `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> ${name}_energy.out
                done
                defect_select=`awk '{print $1,$2}' ${name}_energy.out|sort -k2nr|awk 'END{print $1}'`
                cp $defect_select ../poscar/
        done
        cd ..
