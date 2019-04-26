#!/bin/bash -l
# NOTE the -l flag!
#
#SBATCH -J Si
# Default in slurm
# Request 5 hours run time
#SBATCH -t 4-5:0:0
#
#SBATCH -p super_q -N 1 -n 12
# NOTE Each small node has 12 cores
#
module load vasp/5.4.4-impi-mkl
# add your job logical here!!!

# this is the defect directory
defect_folder=Si-Vacc-defect

export NSLOTS=$SLURM_NPROCS
mkdir supercell
cp POSCAR supercell/
cd supercell
stru_relax.sh
stru_scf.sh
cd ..
get_ground_defect_stru.sh $defect_folder
cd $defect_folder
for q in  -1 0 1
do
  charge_state_cal.sh $q
done
cd ..
image_corr_cal.sh
