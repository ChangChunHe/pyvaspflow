============
处理输出的vasp数据
============


1 pyvasp main
============
这个命令是的到一些基本的信息, 例如能量, 带隙, 费米能级, Ewald能, 电子数等等. 例子::

    $ pyvasp main -a gap  -w . # this can read the gap and vbm, cbm
    $ pyvasp main -a fermi  # this can read the fermi energy
    $ pyvasp main -a energy  # this can read the total energy
    $ pyvasp main -a ele  # this can read the electrons in your OUTCAR
    $ pyvasp main -a ele-free . # this can get electrons number of  the defect-free system
    $ pyvasp main -a image  # this can get Ewald energy of your system,
    $ # using `pyvasp main -a ewald image_corr` can also get the same result.
    $ pyvasp main -a cpu # get total run time

``-w``  指定计算的文件夹, 默认是当前文件夹. 这里还有一个是的到electrostatic能的命令是::

    $ pyvasp main -a electrostatic  23 # 得到 23 号原子的静电势能


2 pyvasp symmetry
============

得到结构对称性的一些信息::

    $ pyvasp symmetry -a spacegroup POSCAR # get space group
    $ pyvasp symmetry -a equivalent POSCAR # get equivalent atoms
    $ pyvasp symmetry -a primitive POSCAR


3 pyvasp diff_pos
============

用于比较两个POSCAR是否是一个结构, 这里需要保证两个POSCAR是同一个晶胞, 并且给出未掺杂的结构的POSCAR.
具体而言即为, 例如有一个原始的金刚石结构的Si的POSCAR, 然后将其中一个Si替换成C, 然后你有两个替换不同位置的Si的POSCAR1,POSCAR2
那么你就可以比较POSCAR1和POSCAR2是否是等价的::

    $ pyvasp diff_pos --help
    Usage: pyvasp diff_pos [OPTIONS] <primitive_poscar> <poscar1> <poscar2>

    $ pyvasp diff_pos POSCAR POSCAR1 POSCAR2
