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

A multiple tasks preparation example:

```shell
pyvasp prep_multi_vasp -w . -a functional=paw_LDA,sym_potcar_map=Zr_sv,NSW=100,style=band
pyvasp prep_multi_vasp -w . -a kppa=4000,node_name=super_q,cpu_num=12
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

The second parameter is the total number of jobs you want to calculate, noted that the name of all directories should be $job_name+$number, number from 0 to `total_number-1`.

Below example means that there are 20 directories should be calculated, there are task0,task1,...,task19.

```shell
pyvasp run_multi_vasp task 20 -p 4
```

The last parameter is `par_job_num`, this parameter means the number of parallel jobs, namely, you can occupy `par_job_num` node simultaneously, the above example means occupying 4 nodes simultaneously.
