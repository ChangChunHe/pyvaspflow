============
KPOINTS 文件
============

KPOINTS 参数的设置也是在 ``-a`` 中, 下面介绍几种KPOINTS文件的写法

你可以选择 style=auto,gamma,monkhorst,line 来生成不同样式的 KPOINTS.



1. 默认设置
===============

默认是按照你的结构生成Monkhorst-Pack的格点或者Gamma中心的网格k点, 计算的mesh方法:
Uses a simple approach scaling the number of divisions along each
reciprocal lattice vector proportional to its length.
          
 .. math ::
          \begin{equation}
          \begin{split}
                     ngrid &= kppa/atom_num\\
                     mult &= (ngrid*a*b*c)^(1/3)\\
                     k-mesh &= [mult/a, mult/b, mult/c]
          \end{split}
          \end{equation}

关于k点的关键字什么都不写就是用这种方式生成k点, 默认 ``kppa=3000`` ::

    $ pyvasp prep_single_vasp



2. 指定gamma中心和kppa设置k点
===============

例子::

    $ pyvasp prep_single_vasp -a style=gamma,kppa=5000

3. 指定mesh设置k点
===============

例子::

    $ # gamma center, k-mesh=5*6*7, shift=0.5 0.5 0.5, default shift is 0 0 0
    $ pyvasp prep_single_vasp -a style=gamma,kpts=5,6,7,shift=0.5,0.5,0.5



    $ pyvasp prep_single_vasp -a style=monkhorst,kpts=5,6,7

4. 指定设置线性的k点
===============

只需要设置 ``style=band`` 或者 ``style=line`` 就可以了, 生成的高对称点是调用 `seekpath`_
的, num_kpt是用于指定两个高对称点之间插入的k点的数目, 默认是16个.

例子::

    $ pyvasp prep_single_vasp -a style=line,num_kpt=20




最后 我们也提供了了一个单独生成 ``KPOINTS`` 的命令接口::


    $ pyvasp kpoints -a style=line,num_kpt=20

.. _seekpath: https://github.com/giovannipizzi/seekpath
