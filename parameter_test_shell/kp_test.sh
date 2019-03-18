#!/bin/bash

module load vasp/5.4.4-impi-mkl

function kp_option1()
{
kp1=${kmaxs[1]}
while [ $kp1 -ge ${kmins[1]} ]
do
kp2=${kmaxs[2]}
while [ $kp2 -ge ${kmins[2]} ]
do
kp3=${kmaxs[3]}
while [ $kp3 -ge ${kmins[3]} ]
do
sed -i "4c $kp1 $kp2 $kp3" KPOINTS
stru_one_step.sh
echo $kp1 $kp2 $kp3 `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> kp_energy.out
        kp3=$[$kp3-1]
done
kp2=$[$kp2-1]
done
kp1=$[$kp1-1]
done
}

function kp_option2()
{
kp1=${kmaxs[1]}
while [ $kp1 -ge ${kmins[1]} ]
do
sed -i "4c $kp1 $kp1 $kp1" KPOINTS
stru_one_step.sh
echo $kp1 $kp1 $kp1 `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> kp_energy.out
kp1=$[$kp1-1]
done
}

function kp_option3()
{
kp1=${kmaxs[1]}
while [ $kp1 -ge ${kmins[1]} ]
do
	kp2=${kmaxs[2]}
	while [ $kp2 -ge ${kmins[2]} ]
	do
	        sed -i "4c $kp1 $kp2 $kp2" KPOINTS
          stru_one_step.sh
	        echo $kp1 $kp2 $kp2 `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> kp_energy.out
		kp2=$[$kp2-1]
	done
	kp1=$[$kp1-1]
done
}

function kp_option4()
{
kp1=${kmaxs[2]}
while [ $kp1 -ge ${kmins[2]} ]
do
	kp2=${kmaxs[1]}
        while [ $kp2 -ge ${kmins[1]} ]
        do
        sed -i "4c $kp2 $kp1 $kp2" KPOINTS
        stru_one_step.sh
        echo $kp2 $kp1 $kp2 `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> kp_energy.out
        kp2=$[$kp2-1]
        done
        kp1=$[$kp1-1]
done
}

function kp_option5()
{
kp1=${kmaxs[3]}
while [ $kp1 -ge ${kmins[3]} ]
do
	kp2=${kmaxs[1]}
  while [ $kp2 -ge ${kmins[1]} ]
  do
          sed -i "4c $kp2 $kp2 $kp1" KPOINTS
          stru_one_step.sh
          echo $kp2 $kp2 $kp1 `awk '/TOTEN/{print $(NF-1)}' OUTCAR |tail -1` `awk '/CPU/{print $NF}' OUTCAR` >> kp_energy.out
          kp2=$[$kp2-1]
  done
  kp1=$[$kp1-1]
done
}


#select vasp_version
if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp_ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std";
fi

#delete the kp_energy.out
if [ -f kp_energy.out ]
then	rm kp_energy.out;	fi

#generate constant_test_point
if [ -n "$1" ] && [ -n "$2" ]
then
  k_min=$1
  k_max=$2
else
	k_min=20
	k_max=40
fi
kpoints.sh
cons=`awk 'NR==2{print $1}' POSCAR`
for iii in 1 2 3
do
kmaxs[$iii]=`awk -v k_max=$k_max -v iii=$iii -v cons=$cons 'NR==(2+iii){printf "%d\n",k_max/cons/($1^2+$2^2+$3^2)^0.5}' POSCAR`
kmins[$iii]=`awk -v k_min=$k_min -v iii=$iii -v cons=$cons 'NR==(2+iii){printf "%d\n",k_min/cons/($1^2+$2^2+$3^2)^0.5}' POSCAR`
done
echo kmaxs=${kmaxs[*]} kmins=${kmins[*]}

if [ ${kmaxs[1]} -eq ${kmaxs[2]} ] && [ ${kmaxs[1]} -eq ${kmaxs[3]} ]
then	kp_option2
elif [ ${kmaxs[2]} -eq ${kmaxs[3]} ]
then	kp_option3
elif [ ${kmaxs[1]} -eq ${kmaxs[3]} ]
then	kp_option4
elif [ ${kmaxs[1]} -eq ${kmaxs[2]} ]
then	kp_option5
else	kp_option1
fi

