#!/bin/bash
####we should give $1 and $2 #################
#####$1 is no-modified POSCAR,$2 is midified POSCAR#######
if [ -f out ]
then	exit;fi
ele_free_num=`sed -n '6p' $1 | awk '{print NF}' `   
ele_defect_num=`sed -n '6p' $2 | awk '{print NF}'` 
a[0]=0
#compare=`echo "$ele_defect_num > $ele_free_num"|bc -l`
compare=`awk -v a=$ele_defect_num -v b=$ele_free_num 'END{print a<b}' POSCAR`

if [ $compare -eq 0 ]
then	max=$ele_defect_num
else	max=$ele_free_num
fi

for i in `seq $max`
do	
	ele1=`sed -n "6 p" $1 |awk -v i=$i '{print $i}'`	
	for j in `seq $max`
	do	
		b=$[$i -1 ]	
		if [ $b -ne 0 ]
		then
			for k in `seq $b`
			do
				c=0
				if [ $j -eq ${a[$k]} ]	
				then
					c=1;break
				fi
			done
			if [ $c -eq 1 ]
			then
				continue
			fi
		fi
		ele2=`sed -n "6 p" $2 |awk -v j=$j '{print $j}'`	;
		if [ "$ele1" == "" ] && [ "$ele2" != "" ] 
		then	
			a[$i]=$j
			#echo "$ele2 go in system" >> out
                        atom_num2=`sed -n "7 p" $2 |awk -v j=$j '{print $j}'`
                        echo $ele2 $atom_num2 >> out
                        break
		elif [ "$ele2" == "" ] && [ "$ele1" != "" ]
		then 	
			a[$i]=$j
			#echo "$ele1 go out system" >> out
                        atom_num1=`sed -n "7 p" $1 |awk -v j=$j '{print $j}'`
                        echo $ele1 $atom_num1 >> out
                        break
		elif [ "$ele1" == "$ele2" ] 
		then
			atom_num1=`sed -n "7 p" $1 |awk -v i=$i '{print $i}'`	;
			atom_num2=`sed -n "7 p" $2 |awk -v j=$j '{print $j}'`	;
			if [ $atom_num1 -eq $atom_num2 ]  
			then 
				a[$i]=$j
				break 
			else 
				#deta=`echo "$atom_num2 - $atom_num1"|bc -l`
				deta=`awk -v a=$atom_num2 -v b=$atom_num1 'END{print a-b}' POSCAR`
				#judge=`echo "$deta > 0 "|bc -l`		;	
				judge=`awk -v a=$deta 'END{print a<=0}' POSCAR`
				if [  $judge -gt  1 ] 
				then
					a[$i]=$j
					#echo "$ele1 go in system"  >> out
					echo $ele1 $deta >> out
				else 	
					a[$i]=$j
					#echo "$ele1 go out system" >> out
					echo $ele1 $deta >> out
				fi
			fi
			break
		fi
	done
done




