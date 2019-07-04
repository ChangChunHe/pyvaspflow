============
运行任务
============

这里我们提供了两种执行任务的命令, 分别为执行单个任务和多个任务( ``run_single_vasp`` , ``run_multi_vasp`` ).

execute single vasp task
============

这是在你已经准备好了要计算的文件以后才可以运行的, 这个命令的作用在于它可以等待你的vasp计算完成
之后才会停止运行. 比如你需要在计算完成之后提取某些数据, 如果你直接 ``sbatch job.sh`` , 那么
这句命令直接就运行结束了, 但是vasp却没有计算完成, 所以你就没法提取数据了, 这个命令的好处在于他会查询你提交的任务号是否
还在队列中, 如果不在了则说明你已经计算完毕了, 才会继续进行下面的操作, 比如你要进行的提取数据的操作.


例子::

    $ pyvasp run_ringle_vasp  task


最后跟上你要计算的文件夹即可. 但是注意到该命令会跟着你的任务计算同时停止掉, 所以你需要把这个程
序放到后台执行. 对于Linux用户只需要加末尾加上一个&号即可, 对于 Windows用户需要使用 ``nohup`` 对程序进行后台托管.

.. note:: 例子::

    $ pyvasp run_ringle_vasp task 1>std.out 2>err.out & # for Linux user
    $ nohup pyvasp run_ringle_vasp task 1>std.out 2>err.out& # for Windows user, 1后面重定向标准输出, 2后面重定向错误输出.

注意你也可以不写重定向的东西, 直接以&结尾, 但是这个是不建议的.




execute multiple vasp-tasks
============


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

    $ pyvasp run_multi_vasp -p 6 -s 5 struc_opt 20 1>std.out 2>err.out & # for Linux user
    $ nohup pyvasp run_multi_vasp -p 6 -s 5 struc_opt 20 1>std.out 2>err.out& # for Windows user, 1后面重定向标准输出, 2后面重定向错误输出.
