============
准备输入文件
============

这里我们主要提供了两个准备输入文件的命令行接口, 分别是准备单个任务和多个任务的命令, ``prep_single_vasp, prep_multi_vasp``. 下面会主要介绍这两个命令的用法. 使用这两个命令之前都需要你先提供 ``POSCAR`` 文件.




prep_single_vasp
===============
首先你可以通过使用 ``help`` 命令来获取帮助::

     $ pyvasp prep_single_vasp --help
     Usage: pyvasp prep_single_vasp [OPTIONS]

pyvasp prep_single_vasp 有两个可选参数, 分别为 ``-p, -a``. 这里 ``-p`` 是为了指定 ``POSCAR``的位置
默认值为 ``POSCAR`` , ``-a`` 是为了设置一些任务的参数, 例如 ``INCAR, KPOINTS, POTCAR, job.sh``中的
参数设置, 后面会仔细介绍 ``-a``  这个参数的用法.

这里举一个例子::

    $ pyvasp prep_single_vasp -p POSCAR -a NSW=100,job_name=task,style=band

和明显 NSW=100是设置 ``INCAR`` 的参数, ``style=band`` 是设置线性的k点用于计算能带.这
里的 ``job_name`` 是指会生成一个为 ``task`` 的文件夹, 所生成的文件都在这个文件夹里面.



prep_multi_vasp
===============
运行这个命令之前你需要先准备多个 ``POSCAR`` 文件, 这里文件需要按照流水号命名, 不然程序无法识别出来.
使用说明::

    $ pyvasp prep_multi_vasp --help
    Usage: pyvasp prep_multi_vasp [OPTIONS] <the last number of jobs>

这里的参数和上面的几乎是一样的, 只是最后需要指定最后一个任务的序号.例子::

    $ pyvasp prep_multi_vasp -s 2  -a node_name=super_q,cpu_num=12,job_name=struc_opt 20

这里的 ``-s`` 是指从 ``POSCAR2`` 开始生成任务文件, 最后的20是是指一直生成到 ``POSCAR20`` 为止.
对于这些生成的任务我们会生成各个独立的文件夹, 以 ``struc_opt`` 为前缀流水号命名.
