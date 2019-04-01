#!/bin/bash -l
# NOTE the -l flag!
#
#SBATCH -J job-name
# Default in slurm
# Request 5 hours run time
#SBATCH -t 5:0:0

#SBATCH -p short_q -N 1 -n 24
# NOTE Each small node has 24 cores

export NSLOTS=$SLURM_NPROCS
module load vasp/5.4.4-impi-mkl
stru_relax.sh
stru_scf.sh
stru_band.sh
stru_dos.sh
