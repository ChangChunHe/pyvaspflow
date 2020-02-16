============
运行任务
============

这里我们提供了两种执行任务的命令, 分别为执行单个任务和多个任务( ``run_single_vasp`` , ``run_multi_vasp`` ).

``run_ringle_vasp``
======================

这是在你已经准备好了要计算的文件以后才可以运行的, 这个命令的作用在于它可以等待你的vasp计算完成
之后才会停止运行. 比如你需要在计算完成之后提取某些数据, 如果你直接 ``sbatch job.sh`` , 那么
这句命令直接就运行结束了, 但是vasp却没有计算完成, 所以你就没法提取数据了, 这个命令的好处在于他会查询你提交的任务号是否
还在队列中, 如果不在了则说明你已经计算完毕了, 才会继续进行下面的操作, 比如你要进行的提取数据的操作.


例子::

    $ pyvasp run_ringle_vasp  task


最后跟上你要计算的文件夹即可. 但是注意到该命令会跟着你的任务计算同时停止掉, 所以你需要把这个程
序放到后台执行. 对于Linux用户只需要加末尾加上一个&号即可, 对于 Windows用户需要使用 ``nohup`` 对程序进行后台托管.

.. note:: 例子::

    $ nohup pyvasp run_ringle_vasp task 1>std.out 2>err.out& #  1后面重定向标准输出, 2后面重定向错误输出.

注意你也可以不写重定向的东西, 直接以&结尾, 但是这个是不建议的.




``run_multi_vasp``
===================


先贴一下这个命令的帮助::

    $ pyvasp run_multi_vasp --help
    Usage: pyvasp run_multi_vasp [OPTIONS] <job_name> <the last number of jobs>

    Options:
      -s, --start_job_num INTEGER
      -p, --par_job_num INTEGER
      --help    Show this message and exit.



第一个参数是 ``job_name``, 这个就是你之前生成的文件夹的前缀, 比如之前你生成
了 task0,task1,task2,...,task20, 那么这里的job_name就应该填入 ``task`` ,
这里的 ``-s`` 是开始的任务号, 比如你可以指定从 ``task4`` 开始计算, ``-s 4`` 即可, 该参数默认为0. ``-p`` 是队列里同时有的最大任务数目.
默认是4, 具体的意思就是比如你有10个任务, 最开始一次性提交4个任务, 接着如果第一个计算完毕了, 而且二三四都没有计算完毕, 那么第五个任务就会被
提交上去, 会一直保持任务队列中有4个任务直到所有任务结束为止. 比如::

    $ pyvasp run_multi_vasp -p 6 -s 5 struc_opt 20

比如这个例子就是说从struc_opt5开始计算, 到struc_opt20截止, 同时运行的任务数为6个. 与之前一样, 该程序最好也用后台进行.

.. note:: 例子::

    $ nohup pyvasp run_multi_vasp -p 6 -s 5 struc_opt 20 1>std.out 2>err.out& #  1后面重定向标准输出, 2后面重定向错误输出.


``run_multi_vasp_without_job``
===============================
先贴一下这个命令的帮助::

    $ pyvasp run_multi_vasp --help
    Usage: pyvasp run_multi_vasp_without_job [OPTIONS] <job_name> <the last number of jobs>

    Example:

    pyvasp run_multi_vasp_without_job  task 5 --node_name  test_q --cpu_num 24

    run multiple vasp task from task0 to task5 through test_q node whith 24 cpu

    pyvasp run_multi_vasp_without_job  task 5 --node_name  test_q,super_q --cpu_num 24,12


这个命令可以用于, 例如你期望你的任务佔用多個節點, 那麼就不能使用`run_multi_vasp`這個命令了,
因爲他是直接提交任務文件夾裏面`job.sh`, 這裏可以自行設置節點和cpu數目. 这里需要指定的是节
点名 ``node_nam`` 和 cpu数量 ``cpu_num``, 节点数不建议修改,
就按照默认的1, 这样就可以使用 ``par_job_num``这个参数同时提交多个任务了. 你也可以指定多个
节点名, 相对应的也需要指定多个 ``cpu_num`` , 就可以在这些就节点上优先提交空闲的, 写在前面的节点.



``run_multi_vasp_from_file``
==============================
与准备文件的命令类似, 运行任务也有类似from_file的命令, 使用说明::

    $ pyvasp run_multi_vasp_from_file -h
    $ Usage: pyvasp run_multi_vasp_from_file [OPTIONS] <job_name> <job list file>
    $ pyvasp run_multi_vasp  task job_list_file -p 6 &


``run_multi_vasp_without_job_from_file``
============================================
类似地, 运行任务也有类似without_job 类型的命令, 使用说明::

    $ pyvasp run_multi_vasp_without_job_from_file -h
    $ Usage: pyvasp run_multi_vasp_without_job_from_file [OPTIONS] <job_name> <job list file>
    $ pyvasp run_multi_vasp_without_job_from_file  task job_list_file --node_name  test_q --cpu_num 24
    $ pyvasp run_multi_vasp_without_job_from_file  task job_list_file --node_name  test_q --cpu_num 24




``run_multi_vasp_from_shell``
==============================
因爲上面的任務都是單步的, 也就是你只能計算一次, 如果你希望計算能帶, 那麼你需要計算三次:1. 结构
优化, 2. 结构自恰, 3.计算线性K点的能带, 这样就不能使用上述 ``prep_multi_vasp`` 和 ``run_multi_vasp`` 等等来
系统计算多个任务了.你只能先计算完所有的结构优化, 然后把所有结构的 `CONTCAR` 拷贝出来再计算自恰等等. 这个是不太
恰当的, 所以就有了这个 ``run_multi_vasp_from_shell`` 的命令, 使用说明::

    $ pyvasp run_multi_vasp_from_shell -h
    $ Usage: pyvasp run_multi_vasp_from_shell [OPTIONS] <shell scripts file> <the last number of jobs>

这里需要提供一个 `shell` 文件，例如我们计算能带的时候，可以使用如下的 `band.sh` 文件::

    #!/bin/bash
    # make sure you have install pyvasp in your current environment
    # make sure current directory has POSCAR

    module load pyvaspflow
    pyvasp prep_single_vasp POSCAR -a ISIF=3,job_name=stru_relax
    pyvasp run_single_vasp stru_relax
    pyvasp prep_single_vasp  stru_relax/CONTCAR -a job_name=scf,NSW=0,LCHARG=True
    pyvasp run_single_vasp scf
    pyvasp prep_single_vasp  scf/CONTCAR -a style=band,NSW=0,job_name=band,ICHARG=11
    cp scf/CHG* band/
    pyvasp run_single_vasp band

假设你的文件夹下面现在有10个POSCAR, 按照流水号命名，POSCAR0-POSCAR9， 还有如上的一个 `band.sh` 文件, 那
么你就可以使用命令::

    $ pyvasp run_multi_vasp_from_shell band.sh 9 -w job -p 5

这个命令会自己新建文件夹，按照job前缀的流水号命名, 然后将POSCAR$idx copy到该文件夹里面
为POSCAR, 然后运行这个 `band.sh` . 参数 ``-p`` 与上述的含义是一样的, 只是保持同时有5个 `band.sh` 文件在运行.
这里可以注意到，在 `band.sh` 里面是只能写 `run_single_vasp` 这样的命令, 那么就不能占据多个节点计算了, 所以
就有了这个 `run_single_vasp_without_job` 这个命令.



``run_single_vasp_without_job``
================================
类似与 ``run_multi_vasp_without_job`` 这个命令， 你可以指定用哪些节点，一旦有空闲的节点就会把任务提交上去， 举个例子::

    $ pyvasp run_single_vasp_without_job stru_relax -nname short_q,long_q,test_q -cnum 24,24,24

它会先把任务交到 `short_q` 上， 然后监测到如果任务一直在挂起的状态而 `long_q` 或者 `test_q` 这两个
节点有空闲，那它会把交到 `short_q` 的任务取消掉，重新将任务提交到 `long_q` 或者 `test_q` 上, 这个命令
刚好可以跟 ``run_multi_vasp_from_shell`` 配合使用. 例如可以写一个如下的 `spin.sh` 的shell脚本::

    module load pyvaspflow
    pyvasp prep_single_vasp POSCAR -a NSW=100,kpts=1,1,1,job_name=nospin
    pyvasp run_single_vasp_without_job nospin -nname inter_q,test_q,short_q,long_q,super_q -cnum 24,24,24,24,12

    pyvasp prep_single_vasp nospin/CONTCAR -a NSW=1,kpts=1,1,1,job_name=spin,ISPIN=2,NUPDOWN=2
    pyvasp run_single_vasp_without_job spin -nname inter_q,test_q,short_q,long_q,super_q -cnum 24,24,24,24,12

再配合使用命令::

    $ nohup pyvasp run_multi_vasp_from_shell spin.sh 4182 job  -p 5 1>std 2>err &

那么就可以同时提交5个 `spin.sh` 的任务, 而且每个任务都可以按照节点空闲情况进行分配任务.


logging
===============
日志系统
