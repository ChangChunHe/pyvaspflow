#!/bin/bash -l
#NOTE the -l flag!
#
#SBATCH -J NAME
# Default in slurm
# Request 5 hours run time
#
#SBATCH -p short_q  -N 1 -n 24
# NOTE Each small node has 12 cores
#
export NSLOTS=24
module load vasp/5.4.4-impi-mkl
stru_relax.sh
stru_scf.sh
stru_band.sh
stru_dos.sh
