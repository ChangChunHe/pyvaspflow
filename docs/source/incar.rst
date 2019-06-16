============
INCAR 文件
============

INCAR 参数的设置也是在 ``-a`` 中, 只需要指定INCAR的参数就可以自动写入到INCAR文件.

例如::


    $ pyvasp prep_single_vasp POSCAR -a NSW=143.2,LCHARG=True,EDIFF=1e-4,NELECT=145


我们可以自动将输入的参数格式化到正确的格式, 例如 ``NSW=143.2`` 可以转化成 ``NSW=143`` .


我们也提供了只生成INCAR文件的命令, 使用方式都是一样的.

例如::

    $ pyvasp incar -h
    Usage: pyvasp incar [OPTIONS]

      Example:

      pyvasp incar -f INCAR -a NSW=100,EDIFF=1e-6

      For more help you can refer to

      https://pyvaspflow.readthedocs.io/zh_CN/latest/incar.html

    Options:
      -a, --attribute TEXT
      -f, --incar_file TEXT
      -h, --help             Show this message and exit.


一个例子::

    # generate a new INCAR
    $ pyvasp incar -a NSW=143.2,LCHARG=True,EDIFF=1e-4,NELECT=145

    # generate a INCAR based on an old INCAR file
    $ pyvasp incar -f INCAR -a NSW=100,EDIFF=1e-6

下面这个例子是指可以基于已有的INCAR文件生成一个新的INCAR, ``-a`` 后面的参数会更新到INCAR文件中。
