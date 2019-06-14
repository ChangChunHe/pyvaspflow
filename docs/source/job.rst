============
job 文件
============

这里我们生成的 ``job.sh`` 文件是::

    #!/bin/bash 
    # NOTE the -l flag!
    #SBATCH -J task
    #SBATCH -p short_q -N 1 -n 24

    module load vasp/5.4.4-impi-mkl

    mpirun -n ${SLURM_NPROCS} vasp_std

你可以通过指定 ``node_name`` , ``node_num`` , ``cpu_num`` and ``job_name`` 在你的 ``job.sh`` 文件中
这里默认是设置是: node_name=short_q,cpu_num=24,node_num=1,job_name=task

举一个例子::

    $ pyvasp prep_single_vasp POSCAR -a node_name=super_q,cpu_num=12,job_name=task
