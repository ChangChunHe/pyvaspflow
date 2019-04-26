#!/bin/bash

module load vasp/5.4.4-impi-mkl



for val in 0.8 0.85 0.9 0.95 1.0 1.05 1.1 1.15 1.2
do
  sed -i "2s/.*/$val/" POSCAR
  stru_one_step.sh
  echo $val `tail -1 OSZICAR|awk '{print $5}'` >> latt_const_energy.out
done
