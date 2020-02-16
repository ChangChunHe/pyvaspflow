============
生成结构
============


沿着基矢方向扩胞
============

将晶胞扩到指定的大小, ``-v`` 下面即为扩成2*2*2的超胞 ::

    $ pyvasp extend_spec_direc  -v 2 2 2 POSCAR


指定体积扩胞
============

将晶胞扩到指定的体积, ``-v`` 指定扩的体积上下限 ::

    $ pyvasp extend_spec_vol  -v 2 4 POSCAR

注意这里提供的POSCAR必须为原胞, 如果不是原胞可以使用 ``pyvasp symmetry primitive_cell POSCAR`` 得到原胞.
如果你只想生成指定体积的胞, 只需要上下限想等即可.


生成替换原子的结构
=================

该命令即为替换原子生成结构, ``-i`` 代表进去的原子, ``-o`` 代表移除的原子.


例子::

    $ pyvasp get_point_defect -i Vac -o Si Si-POSCAR # generate a vacancy
    $ pyvasp get_point_defect -i Ga -o In In2O3-POSCAR # genrate a Ga defect
    $ pyvasp get_point_defect -i Fe,Cu -o In -n 2,3 In2O3-POSCAR # genrate a 2Fe3Cu defect




生成四面体中心位置的结构
=======================

该命令会生成三种四面体中心的位置, ``-d`` 参数设置两个缺陷的最近的距离不可以小于的数值, 默认设置是1.5.


例子::

    $ pyvasp get_tetrahedral -i H -d 1 YFe2-POSCAR

该命令有一个 ``-u`` (``--isunique``) 的参数, 含义是四面体中心位是否是包含等价的还是都是非等价的,  默认是包含等价的, 即为生成所有
可能的位置, `-u False`, 你可以修改成 `True` 就会生成各种不等价的结构, 每个结构只包含一个四面体中心位.
