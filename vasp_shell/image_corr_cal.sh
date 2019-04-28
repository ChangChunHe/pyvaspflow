#!/bin/bash

sed -n '1,5p' POSCAR >poscar_img

echo H >> poscar_img
echo 1 >> poscar_img
echo direct >>poscar_img
echo "0.5 0.5 0.5 "  >>poscar_img

if [ ! -d image_corr ]
then
mkdir image_corr
fi
mv poscar_img image_corr/POSCAR
cd image_corr
stru_optimization.sh
cd ..
