# Defect-Formation-Calculation

This package is a integrated Defect Formation energy package, which contains generating tetrahedral interstitial sites and  octahedral interstitial sites, submitting `VASP` calculation job and extracting necessary data to calculate defect formation energy. If you have any problems when using this package, you can new an issue or email me at changchun_he@foxmail.com.




## 0. Installation
You can install this package from source code, and use

```shell
pip install -e . # -e for developer
```

This package has the dependency of  `sagar`, you'd better refer to [this guide](https://sagar.readthedocs.io/zh_CN/latest/installation/quick_install.html)  to install `sagar`, noted that this package  will be installed easily in __unix__ system.

## 1. Preparation

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

## 1.2 Prepare multiple vasp-tasks

Noted that,first the work directory must has POSCAR[[:digit::]], and the `digit` must start with 0.


A multiple tasks preparation example:

```shell
pyvasp prep_multi_vasp -w . -a functional=paw_LDA,sym_potcar_map=Zr_sv,NSW=100,style=band
pyvasp prep_multi_vasp -w . -a kppa=4000,node_name=super_q,cpu_num=12
```

## 1.3 Parameters

### 1.3.0 `-p`

This parameter is the path of your `POSCAR` file, the default is `POSCAR`.

### 1.3.0.5 `-a`

This parameter mean attributes, you can specify some attributes in your calculation through this parameter. Noted that each attribute should be separated with `,`, this is the delimiter. <br />
 **!!! Do not** separate these parameters with **blank space**.

__Noted that `prep_single_vasp` will make a new directory to contain those generated files, and the directory is named by `job_name`, default is `task`, and the prep_multi_vasp will generate a serial of directories named by job_name+[[:digit]]__

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

## 2. Execution

## 2.1 Execute single vasp-task

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


## 2.2 Execute multiple vasp-tasks

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
pyvasp run_multi_vasp task 20 -p 4
```

The last parameter is `par_job_num`, this parameter means the number of parallel jobs, namely, you can occupy `par_job_num` node simultaneously, the above example means occupying 4 nodes simultaneously.
