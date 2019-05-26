============
INCAR 文件
============

INCAR 参数的设置也是在 ``-a`` 中, 只需要指定INCAR的参数就可以自动写入到INCAR文件.

例如::


    $ pyvasp prep_single_vasp -a NSW=143.2,LCHARG=True,EDIFF=1e-4,NELECT=145


我们可以自动将输入的参数格式化到正确的格式, 例如 ``NSW=143.2`` 可以转化成 ``NSW=143`` .


我们也提供了只生成INCAR文件的命令, 使用方式都是一样的.

例如::


    $ pyvasp incar -a NSW=143.2,LCHARG=True,EDIFF=1e-4,NELECT=145
