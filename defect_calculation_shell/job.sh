#!/bin/bash -l
# NOTE the -l flag!
#
#SBATCH -J ZnO_Al
# Default in slurm
# Request 5 hours run time
#SBATCH -t 24:0:0
#
#SBATCH -p normal_q -N 1 -n 12
# NOTE Each small node has 24 cores
#

module load vasp/5.4.4-impi-mkl
module load sagar
###############################################
encut=500
k_max=40
host_name="test"
export NSLOTS=$SLURM_NPROCS
export host_name encut

get_ground_defect_stru.sh In-Ga-defect
