============
处理输出的vasp数据
============


1 ``pyvasp``
===============
这个命令是的到一些基本的信息, 例如能量, 带隙, 费米能级, Ewald能, 电子数等等. 例子::

    $ pyvasp  gap  -w . # this can read the gap and vbm, cbm
    $ pyvasp  fermi  # this can read the fermi energy
    $ pyvasp  energy  # this can read the total energy
    $ pyvasp electron_number  # this can read the electrons in your OUTCAR
    $ pyvasp  electron_defect_free . # this can get electrons number of  the defect-free system
    $ pyvasp image  # this can get Ewald energy of your system,
    $ # using `pyvasp  ewald image_corr` can also get the same result.
    $ pyvasp  cpu # get total run time

``-w``  指定计算的文件夹, 默认是当前文件夹. 这里还有一个是的到electrostatic能的命令是::

    $ pyvasp  electrostatic  23 # 得到 23 号原子的静电势能


2 ``pyvasp symmetry``
=======================

得到结构对称性的一些信息::

    $ pyvasp symmetry  spacegroup POSCAR # get space group
    $ pyvasp symmetry  equivalent POSCAR # get equivalent atoms
    $ pyvasp symmetry  primitive POSCAR


3 ``pyvasp diff_pos``
=======================

用于比较两个POSCAR是否是一个结构, 这里需要保证两个POSCAR是同一个晶胞, 并且给出未掺杂的结构的POSCAR.
具体而言即为, 例如有一个原始的金刚石结构的Si的POSCAR, 然后将其中一个Si替换成C, 然后你有两个替换不同位置的Si的POSCAR1,POSCAR2
那么你就可以比较POSCAR1和POSCAR2是否是等价的::

    $ pyvasp diff_pos --help
    Usage: pyvasp diff_pos [OPTIONS] <primitive_poscar> <poscar1> <poscar2>

    $ pyvasp diff_pos POSCAR POSCAR1 POSCAR2

4 ``pyvasp get_grd_state``
===========================

 用于得到一系列结构的能量最低的结构的序号. 例如你用 ``pyvasp get_point_defect`` 生成了许
 多结构, 然后计算完能量就可以使用该命令得到能量最低的结构的序号::

    $ pyvasp get_grd_state -h
    Usage: pyvasp get_grd_state [OPTIONS] <your job name> <the last number of jobs>

     Exmaple:

     pyvasp get_grd_state -s 2 task 100

    Options:
     -s, --start_job_num INTEGER
     -h, --help                   Show this message and exit.
