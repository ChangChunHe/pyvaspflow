============
具体的例子
============

计算能带, 态密度
============
下面是计算能带的例子, 相信如果你读完前面的文档应该是可以看得懂的::

    #!/bin/bash
    # make sure you have install pyvasp in your current environment
    # make sure current directory has POSCAR

    pyvasp prep_single_vasp -a ISIF=3,job_name=stru_relax
    pyvasp run_single_vasp stru_relax
    pyvasp prep_single_vasp -p stru_relax/CONTCAR -a job_name=scf,NSW=0,LCHARG=True
    pyvasp run_single_vasp scf
    pyvasp prep_single_vasp -p scf/CONTCAR -a style=band,NSW=0,job_name=band,ICHARG=11
    cp scf/CHG* band/
    pyvasp run_single_vasp band

计算态密度的例子::

    #!/bin/bash
    # make sure you have install pyvasp in your current environment
    # make sure current directory has POSCAR

    pyvasp prep_single_vasp -a ISIF=3,job_name=stru_relax
    pyvasp run_single_vasp stru_relax
    pyvasp prep_single_vasp -p stru_relax/CONTCAR -a kppa=4000,job_name=scf,NSW=0,LCHARG=True
    pyvasp run_single_vasp scf
    pyvasp prep_single_vasp -p scf/CONTCAR -a kppa=8000,ISMEAR=-5,job_name=dos,NSW=0
    cp scf/CHG* dos/
    pyvasp run_single_vasp dos

这两个例子可以在源文件中找到: `band`_ , `dos`_ .

.. _band: https://github.com/ChangChunHe/pyvaspflow/blob/master/pyvaspflow/examples/common_calculations/band.sh
.. _dos: https://github.com/ChangChunHe/pyvaspflow/blob/master/pyvaspflow/examples/common_calculations/dos.sh


计算基态相图
============
这一小节实际上是说例如$A_xB_{1-x}$合金, 我们可以给出指定胞的各种不重复结构, 然后计算能量, 最后可以给出一个横轴的浓度$x$的基态相图.

pyvasp get_grd_state::

    $ $ pyvasp get_grd_state --help
    $ Usage: pyvasp get_grd_state [OPTIONS] <your job name> <end job number>
    $
    $ pyvasp get_grd_state task 100 # return the number of ground state





计算缺陷形成能
============

pyvasp get_def_form_energy::

    $ pyvasp get_def_form_energy --help
    Usage: pyvasp get_def_form_energy [OPTIONS] <your data main direcroty> <your data defect calculation direcroty>

    pyvasp get_def_form_energy  test  test/H-vacc-defect test/Mg-vacc-defect
