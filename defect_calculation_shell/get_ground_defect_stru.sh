#!/bin/bash -l
# NOTE the -l flag!
#
#SBATCH -J FeY-H
# Default in slurm
# Request 5 hours run time
#
#SBATCH -p normal_q -N 1 -n 12
# NOTE Each small node has 12 cores
#
module load vasp/5.4.4-impi-mkl
# add your job logical here!!!
export NSLOTS=24

for ii in `ls`
do
if [[ $ii == *"POSCAR"*  ]]
then
a=$ii
mkdir $ii-cal
cp $ii $ii-cal/POSCAR
cd $ii-cal
potcar.sh Y_sv
kpoints.sh
incar.sh
stru_relax.sh
echo $ii `tail -1 OSZICAR |awk '{print $5}'`  >> energy_out
cd ..
fi
done
ground_stru_num=`cat energy_out|sort -nk2r|head -1|awk '{print $1}'`
b=`echo $a |cut -d'_' -f 1`
mv ${b}_idx$ground_stru_num.vasp POSCAR_ground_stru # this is the ground state
