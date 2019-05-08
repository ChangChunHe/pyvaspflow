# Defect-Formation-Calculation

This package is a integrated Defect Formation energy package, which contains generating tetrahedral interstitial sites and  octahedral interstitial sites, submitting `VASP` calculation job and extracting necessary data to calculate defect formation energy. If you have any problems when using this package, you can new an issue or email me at changchun_he@foxmail.com.

Table of Contents
=================

   * [Defect-Formation-Calculation](#defect-formation-calculation)
      * [0 Installation](#0-installation)
      * [0.5 Configuration](#05-configuration)
      * [1 Preparation](#1-preparation)
      * [1.1 Prepare single vasp-task](#11-prepare-single-vasp-task)
      * [1.2 Prepare multiple vasp-tasks](#12-prepare-multiple-vasp-tasks)
      * [1.3 Parameters](#13-parameters)
         * [1.3.0 -a](#130--a)
         * [1.3.1 INCAR](#131-incar)
         * [1.3.2 KPOINTS](#132-kpoints)
         * [1.3.3 POTCAR](#133-potcar)
         * [1.3.4 job.sh](#134-jobsh)
      * [2 Execution](#2-execution)
         * [2.1 Execute single vasp-task](#21-execute-single-vasp-task)
         * [2.2 Execute multiple vasp-tasks](#22-execute-multiple-vasp-tasks)
         * [2.3 Test some parameters](#23-test-some-parameters)
            * [2.3.1 test ENMAX](#231-test-enmax)
            * [2.3.2 test KPOINTS](#232-test-kpoints)
      * [3 Fetch](#3-fetch)
         * [3.1 pyvasp-help](#31-pyvasp-help)
         * [3.2 pyvasp-main](#32-pyvasp-main)
         * [3.3 pyvasp-cell](#33-pyvasp-cell)
         * [3.4 pyvasp-get_purity](#34-pyvasp-get_purity)
         * [3.5 pyvasp-get_tetrahedral](#35-pyvasp-get_tetrahedral)
         * [3.6 pyvasp-get_PA](#36-pyvasp-get_pa)
         * [3.7 pyvasp-symmetry](#37-pyvasp-symmetry)


## 0 Installation
You can install this package from source code, and use

```shell
pip install -e . # -e for developer
```

This package has the dependency of  `sagar`, you'd better refer to [this guide](https://sagar.readthedocs.io/zh_CN/latest/installation/quick_install.html)  to install `sagar`, noted that this package  will be installed easily in __unix__ system.

## 0.5 Configuration
This package need you to set some configurations in order to read `POTCAR` files and write correct `job.sh` files.
This file should be named as `conf.json` under your `$HOME` directory or in your current directory. And we will **firstly** search  this  file in your **current directory**.

```json
{
"potcar_path":
{"paw_PBE":"/opt/ohpc/pub/apps/vasp/pps/paw_PBE",
"paw_LDA":"/opt/ohpc/pub/apps/vasp/pps/paw_LDA",
"paw_PW91":"/opt/ohpc/pub/apps/vasp/pps/paw_PW91",
"USPP_LDA":"/opt/ohpc/pub/apps/vasp/pps/USPP_LDA",
"USPP_PW91":"/opt/ohpc/pub/apps/vasp/pps/USPP_PW91"
},
"job":{
"prepend": "module load vasp/5.4.4-impi-mkl",
"exec": "mpirun -n ${SLURM_NPROCS} vasp_std"
}
}
```
This file your  should specify your `POTCAR` path and the command of  submitting  jobs.

## 1 Preparation

You can use `--help` to get some help

## 1.1 Prepare single vasp-task

```shell
pyvasp prep_single_vasp --help # to get help
```

A single task  preparation example:

```shell
pyvasp prep_single_vasp -p POSCAR -a functional=paw_LDA,sym_potcar_map=Zr_sv,NSW=100,style=band
pyvasp prep_single_vasp -p POSCAR -a kppa=4000,node_name=super_q,cpu_num=12
```

`-p` parameter is the path of your `POSCAR` file, the default is `POSCAR`.`-a` parameter is the attribute you want to specify.


## 1.2 Prepare multiple vasp-tasks

Noted that,first the work directory must has POSCAR[[:digit:]], and the `digit` must start with 0. This command will generate separated directories containing `POSCAR, KPOINTS,POTCAR, job.sh`.

A multiple tasks preparation example:

supposed that your work directory has POSCAR0,POSCAR1,...,POSCAR12.
```shell
# -w means the work directory, this directory should contain
# POSCAR0,POSCAR1,..., this command will automatic
# find all theses files

pyvasp prep_multi_vasp -w . -a kppa=4000,node_name=super_q,cpu_num=12,job_name=struc_opt
```
This command will generate  `struc_opt0`,`struc_opt1`,...,`struc_opt12`, because you specify parameter `job_name=struc_opt`, the default is `task`. If you do not  specify `job_name`, the names of generated directories will be `task0`,`task1`,...,`task12`.

## 1.3 Parameters

### 1.3.0 `-a`

This parameter mean attributes, you can specify some attributes in your calculation through this parameter. Noted that each attribute should be separated with `,`( this is the delimiter). <br />
 **!!! Do not** separate these parameters with **blank space**.

__Noted that `prep_single_vasp` will make a new directory to contain those generated files, and the directory is named by `job_name`, default is `task`, and the prep_multi_vasp will generate a serial of directories named by job_name+[[:digit:]]__

Below examples are  based on `prep_single_vasp`, which will also be applicable for `prep_multi_vasp`.

### 1.3.1 `INCAR`

You can write any parameters  in INCAR  after `pyvasp -a`. Example:

```shell
pyvasp prep_single_vasp -a NSW=143.2,LCHARG=True,EDIFF=1e-4,NELECT=145
```
We can interpret `NSW=143.2` to `NSW=143` for this parameter should be an `INTEGER`.

### 1.3.2 `KPOINTS`
You can choose `style`=`auto`,`gamma`,`monkhorst`,`line` to generate different KPOINTS.

Example:
```shell
# the default will choose G or M according to your structure, kppa=3000
pyvasp prep_single_vasp

# gamma center,kppa=5000
pyvasp prep_single_vasp -a style=gamma,kppa=5000

# gamma center, k-mesh=5*6*7, shift=0.5 0.5 0.5, default shift is 0 0 0
pyvasp prep_single_vasp -a style=gamma,kpts=5,6,7,shift=0.5,0.5,0.5

# similar as the above one
pyvasp prep_single_vasp -a style=monkhorst,kpts=5,6,7

# line mode for band structure calculation,style=line or band
# num_kpt means  the points inserted between two nearest K-points.
pyvasp prep_single_vasp -a style=line,num_kpt=20
```

### 1.3.3 `POTCAR`
You can specify `functional` and `sym_potcar_map` to generate POTCAR.


```shell
# this will generate Zr_sv of paw_LDA POTCAR
# for those not specified in `sym_potcar_map` will using the default
# the default is the element itself

pyvasp prep_single_vasp -a functional=paw_LDA,sym_potcar_map=Zr_sv
```

### 1.3.4 `job.sh`
You can specify `node_name`, `node_num`, `cpu_num` and `job_name` in your `job.sh`.<br \>
Default:<br \>
node_name=short_q,cpu_num=24,node_num=1,job_name=task

```shell
pyvasp prep_single_vasp -a node_name=super_q,cpu_num=12,job_name=task
```

## 2 Execution

### 2.1 Execute single vasp-task

```shell
$ pyvasp run_single_vasp --help
Usage: pyvasp run_single_vasp [OPTIONS] <single_vasp_dir>

Options:
  --help  Show this message and exit.
```

Below is an example, only one parameter (your task directory) should be input.

```shell
pyvasp run_ringle_vasp  task
```


### 2.2 Execute multiple vasp-tasks

```shell
$ pyvasp run_multi_vasp --help
Usage: pyvasp run_multi_vasp [OPTIONS] <job_name> <total number of jobs>

Options:
  -p, --par_job_num INTEGER
  --help  Show this message and exit.
```

The first parameter is your `job_name`, because you have generated some separate directories with the same prefix, the prefix is `job_name`,the default `job_name` in the `prep_multi_vasp` command is `task`.

The second parameter is the total number of jobs you want to calculate, noted that the name of all directories should be job_name[[:digit:]].

Below example means that there are 20 directories should be calculated, there are task0,task1,...,task19.

```shell
pyvasp run_multi_vasp -p 4 task 20
```

The last parameter is `par_job_num`, this parameter means the number of parallel jobs, namely, you can occupy `par_job_num` node simultaneously, the above example means occupying 4 nodes simultaneously.

And  we also support the parameter `start_job_num`, this is the number of your first directory.

```shell
pyvasp run_multi_vasp -p 3 -s 13 task 20
```
This means that you  will start your jobs from task13 to task 20. The default of  this parameter is 0.

### 2.3 Test some parameters
Here we support `parameters-testing` command.

#### 2.3.1 test ENMAX

```shell
pyvasp test_enmax -p POSCAR -s 0.8 -e 1.3 -t 30
```
Here `-s` is the min_enmax, which means 0.8*max(enmax), `-e` is the max_enmax, which means 1.3*max(enmax), `-t` is the step of the test-enmax. This command also supports `-a` parameter, you can specify other attributes.

#### 2.3.2 test KPOINTS

```shell
pyvasp test_kpts -p POSCAR -s 1000 -e 3000 -t 200
```
Here `-s` is the min_kppa, `-e` is the max_kppa, `-t` is the step of the test-kppa. This command also supports `-a` parameter, you can specify other attributes.


## 3 Fetch

Here we supply a command interface to get the value you want.

__Noted that, if you get `permission denied`, please use `chmod u+x pyvasp.py` to give the execute right to the file__

### 3.1 pyvasp-help
```shell
pyvasp --help # you can get some short help from this command
pyvasp main --help # get the help of a specific command  
```

### 3.2 pyvasp-`main`
This command is used to get some common value of your calculation system. For instance, gap, fermi energy, electrons number and so on.
The last parameter is the directory path of your calculation system, make sure it is right or you will get wrong answer.
```shell
pyvasp main -a gap . # this can read the gap and vbm, cbm
pyvasp main -a fermi . # this can read the fermi energy
pyvasp main -a energy . # this can read the total energy
pyvasp main -a ele . # this can read the electrons in your OUTCAR
pyvasp main -a ele-free . # this can get electrons number of  the defect-free system
pyvasp main -a image image_corr/ # this can get Ewald energy of your system,  
# using `pyvasp main -a ewald image_corr` can also get the same result.
pyvasp main -a cpu # get total run time
```

### 3.3 pyvasp-`cell`
This command is used to extend your cell and generate a supcell.vasp
```shell
pyvasp cell -v 2 2 2 POSCAR
# extend your POSCAR to 2*2*2 supercell
```

### 3.4 pyvasp-`get_purity`
This command is used to get the purity structures , such Si-vacancy, Ga purity in In2O3 system, but noted that each time only one purity atom will be dopped into the system.
```shell
pyvasp get_purity -i Vacc -o Si Si-POSCAR # generate a vacancy
pyvasp get_purity -i Ga -o In In2O3-POSCAR #genrate a Ga defect
```

### 3.5 pyvasp-`get_tetrahedral`
This command is used to get the tetrahedral interstitial sites, for example, in YFe2 system, H atom can be inserted into the tetrahedral sites.

```shell
pyvasp get_tetrahedral -i H YFe2-POSCAR
```

### 3.6 pyvasp-`get_PA`
This command can get the electrostatic of your defect system and no defect system of the farther atom from defect atom
```shell
pyvasp get_PA defect_free charge_state_1
```

### 3.7 pyvasp-`symmetry`
This command can get some symmetry message of your POSCAR.

```shell
pyvasp symmetry -a spacegroup POSCAR # get space group
pyvasp symmetry -a equivalent POSCAR # get equivalent atoms
pyvasp symmetry -a primitive POSCAR
# generate primitive cell POSCAR
```
