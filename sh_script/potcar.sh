#!/bin/bash
path1="/home/wyp/PAW_POTCAR_pbe"
path2="/home/wyp/PAW_POTCAR_lda/"
path3="/home/wyp/PAW_POTCAR_scan/"
if [ ! -n "$pot_type" ]
then	path=$path1
elif [ $pot_type -eq 1 ]
then	path=$path1
elif [ $pot_type -eq 2 ]
then 	path=$path2
elif [ $pot_type -eq 3 ]
then	path=$path3
fi


while [ ! -f POTCAR ]
do    
        dos2unix POSCAR > /dev/null
        ele_num=`awk 'NR==6{print NF}' POSCAR`
        for i in `seq $ele_num`
        do
                ls $path/POTCAR-"`awk -v i=$i  'NR==6{print $i}' POSCAR`"* |awk 'NR==1{print $1}' >> temp_pot
                a=`awk -v i=$i 'NR==i{print}' temp_pot`
                cat $a >> POTCAR
        done
        rm temp_pot
done

