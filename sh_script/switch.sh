#!/bin/bash
	
	
	if [ -n "$1" ]
	then 		file=$1
	else		file=CONTCAR;	fi

        ele_num=`awk 'NR==6{print NF}' $file`
        s=0
        for x in `seq $ele_num`
        do
                s=`awk -v x=$x -v s=$s 'NR==7{print s+=$x}' $file`
        done
        acquire=$[$s+8]
        sed -n "1,$acquire p" $file >contcar
        mv contcar $file.vasp

