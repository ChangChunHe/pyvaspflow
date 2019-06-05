#/bin/bash


# relax calculation and scf calculation
pyvasp prep_single_vasp -a ISIF=3,node_name=long_q,job_name=supercell
pyvasp run_single_vasp supercell
cd supercell
pyvasp prep_single_vasp -p  CONTCAR -a kppa=4000,job_name=scf,node_name=long_q,NSW=0
pyvasp run_single_vasp scf
cd ..


# get ground state of defect configurations
pyvasp get_purity -i Vacc -o Si supercell/scf/CONTCAR

cd Si-Vacc-defect
i=0
for f in `ls`
do
mv $f POSCAR$i
let i=i+1
done
pyvasp prep_multi_vasp $((i-1)) -a node_name=long_q
pyvasp run_multi_vasp task $((i-1))
grd_idx=`pyvasp get_grd_state task $((i-1)) `
cp task${grd_idx}/CONTCAR grd_poscar


## calculate possible charge states
total_ele=`pyvasp main -a ele-free -w  task0`
for q in -2 -1 0 1 2
do
let ele=${total_ele}-$q
pyvasp prep_single_vasp -p grd_poscar -a NELECT=$ele,job_name=charge_state_$q,node_name=long_q
pyvasp run_single_vasp charge_state_$q
cd charge_state_$q
pyvasp prep_single_vasp -p  CONTCAR -a NELECT=$ele,job_name=scf,node_name=long_q,NSW=0
pyvasp run_single_vasp scf
cd ..
done

cd ..

## calculate image correlation
sed -n '1,5p' supercell/scf/POSCAR >poscar_img
echo H >> poscar_img
echo 1 >> poscar_img
echo direct >>poscar_img
echo "0.5 0.5 0.5 "  >>poscar_img
if [ ! -d image_corr ]
then
mkdir image_corr
fi
pyvasp prep_single_vasp -p poscar_img -a ISIF=2,job_name=image_corr,node_name=long_q
rm poscar_img
pyvasp run_single_vasp image_corr
