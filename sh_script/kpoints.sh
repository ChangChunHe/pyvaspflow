#!/bin/bash

if [ ! -n "$k_max" ];then	k_max=30;fi
if [ ! -n "$inter_num" ];then	inter_num=30;fi

function band_kpoints()
{
if [ -f k-path ]
then
k_line=`grep -A1 KPOINTS k-path|awk 'NR==2{print $0}'`
high_kp_num=`echo ${k_line##*)}|awk 'BEGIN{FS="[- ]"}{print NF}'`

column=$[$high_kp_num*3-1]

echo $high_kp_num >>syml1

grep -A$column reciprocal k-path|sed '1d'|awk NF|awk 'NR%2{print $5,$1,$2,$3}' >>syml1

a=`sed '1d' syml1|awk 'NR==1{print $1}'`;b=""

for i in `seq $[$high_kp_num-1]`
do
        b=`sed '1d' syml1|awk -v i=$i 'NR==(i+1){print $1}'`

        if [ "$a" == "$b" ];        then    num=$[$i+1];        fi

done

if [ -n "$num" ] &&  [ $num -eq 0 ];	then	num=5;	fi
fi
###################################
if [ ! -f syml ]
then
	echo  $num >>syml

	for i in `seq $num`
	do
        	echo -n "$inter_num  " >>syml
	done

	echo "  " >>syml
	sed -n "2,$[$num+1] p" syml1 >>syml
fi

gk.x

if [ -n "$hse" ] && [ $hse -eq 1 ]
then
        sed -n '1,3p' KPOINTS >> kpoints
        sed '1,3d' KPOINTS |awk '{print $1,$2,$3,0}' >> kpoints
        sed '1,3d' ../IBZKPT|awk '{print }' >> kpoints
        kp_num=`sed '1,3d' kpoints |awk 'END{print NR}'`
        sed -i "2c $kp_num" kpoints
        mv kpoints KPOINTS
fi

#rm syml1
}

###############Generate KPOINTS##########################
while [ ! -f KPOINTS ]
do

cons=`awk 'NR==2{print $1}' POSCAR`
for iii in 1 2 3
do
        k[$iii]=`awk -v k_max=$k_max -v iii=$iii -v cons=$cons 'NR==(2+iii){printf "%d\n",k_max/cons/($1^2+$2^2+$3^2)^0.5}' POSCAR`
done

cat > KPOINTS <<! 
KPOINTS
0
G
${k[*]}
0 0 0
!
done

if [ -n "$band" ] && [ $band -eq 1 ]
then
	band_kpoints
fi
