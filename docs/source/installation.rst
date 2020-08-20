.. _Installation:

=============
快速安装
=============

你可以通过源码进行安装, 这里我们建议安装在服务器上.

.. code-block:: python

     pip install -e . # -e for developer


下面是配置文件, 用于指定赝势的位置和`job.sh`文件的书写.

.. code-block:: json

    {
           "potcar_path":
                         {"paw_PBE":"/opt/ohpc/pub/apps/vasp/pps/paw_PBE",
                          "paw_LDA":"/opt/ohpc/pub/apps/vasp/pps/paw_LDA",
                          "paw_PW91":"/opt/ohpc/pub/apps/vasp/pps/paw_PW91",
                          "USPP_LDA":"/opt/ohpc/pub/apps/vasp/pps/USPP_LDA",
                          "USPP_PW91":"/opt/ohpc/pub/apps/vasp/pps/USPP_PW91"
                           },
           "job":
                 {"prepend": "module load vasp/5.4.4-impi-mkl",
                  "exec": "mpirun -n ${SLURM_NPROCS} vasp_std"
                  "append":"exit"
                 }
    }

potcar_path
===============
配置文件需要指定赝势的文件位置以及对应的泛函的位置, 注意到这里的"paw_PBE,paw_LDA"等也即为在命令行中生成赝势所需要指定的"functional".

:code:`pyvasp prep_single_vasp POSCAR -a functional=paw_PBE`

这里指定的"paw_PBE"也即为说明程序会自动向“/opt/ohpc/pub/apps/vasp/pps/paw_PBE”中寻找对应的赝势文件.

job
===============
job所对应的部分是生成 ``job.sh`` 文件, 这里 `prepend` 所对应的是运行程序前需要
先加载的模块, `exec` 对应的是执行的代码, `append` 对应程序执行完以后需要执行的代码.

如果你需要运行gamma版本, 你可以将 ``vasp_std`` 改成 ``vasp_gam`` .

该文件请放置在$HOME/.config/pyvaspflow/conf.json, 当然你可以可以放在当前文件夹, 我们会优先读取当前文件夹是否有配置文件, 如果没有才会到$HOME/.config/pyvaspflow/conf.json下面找. 所以你可以在$HOME/.config/pyvaspflow/conf.json下面设置一个常用的配置文件, 对与特殊的需要可以拷贝一份放在当前文件夹作为特殊用处.

例如你一般会使用 ``vasp_std`` , 然后只是偶尔需要计算分子的能量, 此时需要使用gamma版本的vasp, 那么你就可以拷贝一份配置文件在当前文件夹, 并把 ``vasp_std`` 改成 ``vasp_gam`` 即可.


自动补齐命令
===============
``pyvasp`` 是支持自动补齐命令的, 例如 ``pyvasp symm`` 按下tab键是可以自动补
齐成 ``pyvasp symmetry`` 的, 接着按下两次tab键可以
给出候选项 ``equivalent_atoms primitive_cell space_group`` 这三个子命令,
你可以接着键入 ``p`` 来补齐命令 ``primitive_cell`` . 但是这个是需要配置的, 需要你在 ``bashrc`` 里面加入::

    eval "$(_PYVASP_COMPLETE=source pyvasp)"

如果你使用 ``zsh`` , 那么需要在你的 ``zshrc`` 就加入::

    eval "$(_PYVASP_COMPLETE=source_zsh pyvasp)"

组内的同学
===============
注意到组内的服务器上是以 ``module`` 的方式安装的, 所以如果只是在你的 ``.bashrc`` 里面
加入这句话是不行的, 因为你还没有load ``pyvaspflow`` 这个包, 所以 ``eval`` 是没有效果的,
必须得在load你的module以后执行才会有效. 所以对于组内的同学我建议你可
以在 ``.bashrc`` 里面加入::

    alias mlpy='module load pyvaspflow;eval "$(_PYVASP_COMPLETE=source pyvasp)"'

然后使用命令 ``mlpy`` 即可加载模块 ``pyvaspflow`` 并且激活自动补齐命令.
