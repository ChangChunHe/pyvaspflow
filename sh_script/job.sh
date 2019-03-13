#!/bin/bash -l
# NOTE the -l flag!
#
#SBATCH -J ZnO_Al
# Default in slurm
# Request 5 hours run time
#SBATCH -t 24:0:0
#
#SBATCH -p dellmid -N 1 -n 12
# NOTE Each small node has 24 cores
#

module load vasp/5.4.4-impi-mkl
module load sagar
###############################################
hse=0
vdw=0
soc=0
sc=(3 3 3)
charge_Sr=2;charge_V=4;charge_O=-2
encut=500
k_max=40
host_name="test"
inter_num=20
pot_type=1
NSLOTS=12
export hse vdw soc  pot_type NSLOTS
export extrinsic replace  
export host_name encut
export charge_Sr charge_O charge_V
export inter_num
######测试参数####################
function step1()
{
cp poscar.vasp POSCAR
cons_test.sh
cp CONTCAR*.vasp POSCAR
encut_test.sh
kp_test.sh
}
function aaa()
{
Stru_relax.sh
switch.sh
runati supcell CONTCAR.vasp -s ${sc[0]} ${sc[1]} ${sc[2]}|sed '1d'  > CONTCAR
scf.sh
Generate_stru.sh CONTCAR
defect_num=`ls poscar|wc -l`
for ss in `seq $defect_num`
do
        mkdir   defect_$ss
        cp poscar/poscar$ss INCAR KPOINTS defect_$ss
        cd defect_$ss
        mv poscar$ss POSCAR
        diff_charge.sh
        cd ..
done

Name_c.sh
}

#######初始结构优化和参数确定########
cp Si.vasp POSCAR
cons_test.sh
cp CONTCAR*.vasp POSCAR
encut_test.sh
kp_test.sh
#检查cons_energy.out，encut_energy.out和kp_energy.out确定参数

#####扩胞并筛选结构############
#python ~/Auto_cal_plot/bin/supcell.py CONTCAR_relax.vasp -v 2 2 2
#Generate_stru.sh
#select_stru.sh
awk '{if(NR==4){printf "%d %d %d\n",$1/2,$2/2,$3/2 } else {print }}' KPOINTS > kpoints_supcell

#####计算##############
#mkdir scf
#cp supcell.vasp CONTCAR
#cp kpoints_supcell scf/KPOINTS 
#scf_cal.sh
imgcor_cal.sh

#defect_name=`awk '{print}' defect_name.out`
#for name in $defect_name
#do
#	mkdir ${name}_defect
#	cp poscar/$name*vasp INCAR  kpoints_supcell ${name}_defect
#	cd ${name}_defect
#	mv $name*vasp POSCAR
#	mv kpoints_supcell KPOINTS
#	diff_charge.sh
#	cd ..
#done

#######计算缺陷形成能#######
#Plot_Hf-Tr.sh


