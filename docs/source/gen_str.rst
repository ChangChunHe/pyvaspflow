============
生成结构
============


生成替换原子的结构
============

该命令即为替换原子生成结构, ``-i`` 代表进去的原子, ``-o``代表移除的原子.


例子::

    $ pyvasp get_purity -i Vacc -o Si Si-POSCAR # generate a vacancy
    $ pyvasp get_purity -i Ga -o In In2O3-POSCAR #genrate a Ga defect



生成四面体中心位置的结构
============

该命令会生成三种四面体中心的位置, ``-d`` 参数设置两个缺陷的最近的距离不可以小于1, 默认设置也是1.


例子::

    $ pyvasp get_tetrahedral -i H -d 1 YFe2-POSCAR
