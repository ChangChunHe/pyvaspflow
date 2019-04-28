#!/bin/bash

if [ -n "$soc" ] && [ $soc -eq 1 ]
then    vasp_version="vasp5.4.4-ncl"
elif [ ! -n "$vasp_version" ]
then    vasp_version="vasp_std"
fi





# calculate the energy of all strcutures
folder=$1
if [ -z $folder ]
then
echo You should input a directory
exit
fi
IFS='-' read -ra A <<< "$folder"
atom_in=${A[1]}

cd $folder

for pos in `ls`
do
mkdir ${pos}-dir
mv $pos ${pos}-dir/POSCAR
cd ${pos}-dir
cp ../../KPOINTS .
cp ../../INCAR .
cp ../../POTCAR .
stru_optimization.sh
echo $pos `tail -1 OSZICAR |awk '{print $5}'` >> ../energy_out
cd ..
done
# gd is the ground structure
gd=`sort -k2n energy_out|awk 'NR==1{print $1}'`

# calculate scf of the ground structure
cp -r  $gd-dir $atom_in-defect
cd $atom_in-defect
stru_scf.sh
cd ../..
