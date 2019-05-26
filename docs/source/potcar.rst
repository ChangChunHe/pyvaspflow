============
POTCRA 文件
============

生成POTCAR 参数的设置也是在 ``-a`` 中, 需要指定使用的泛函类型和使用哪一种类型的赝势.
即 ``functional`` 和 ``sym_potcar_map` 这两个参数. 举个例子::

    # this will generate Zr_sv of paw_LDA POTCAR
    # for those not specified in `sym_potcar_map` will using the default
    # the default is the element itself

    $ pyvasp prep_single_vasp -a functional=paw_LDA,sym_potcar_map=Zr_sv
