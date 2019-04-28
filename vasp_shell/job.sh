#!/bin/bash -l
# NOTE the -l flag!
#
#SBATCH -J Si_pri
# Default in slurm
# Request 5 hours run time
#SBATCH -t 5:0:0
#
#SBATCH -p short_q -N 1 -n 24
# NOTE Each small node has 12 cores
#
module load vasp/5.4.4-impi-mkl
# add your job logical here!!!

export NSLOTS=$SLURM_NPROCS

#stru_scf.sh
#stru_band.sh


#charge_state_cal.sh -1

kp_test.sh
