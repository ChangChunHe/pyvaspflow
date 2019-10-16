============
杀掉任务
============

这里我们提供了杀掉任务的命令 ``kill`` , 用于杀掉交任务的 ``pyvasp`` , 它可以用于杀掉 ``pyvasp`` 这个进程而且取消掉由它提交 的 任务.

``kill``
============

首先你需要 使用 ``ps -ef|grep pyvasp`` 得到你的任务进程号. 使用该命令你可以得到类似下面的结果::

    [hecc@cmp ~]$ ps -ef|grep pyvasp
    hecc      66237  56185 19 04:34 ?        01:03:44 /opt/ohpc/pub/apps/python-virtualenv/pyvaspflow/bin/python3.6 /opt/ohpc/pub/apps/python-virtualenv/pyvaspflow/bin/pyvasp run_multi_vasp_without_job task 125 -nname short_q,super_q -cnum 24,12 -p 8
    xwq      107772  95242 22 08:49 pts/12   00:16:16 /opt/ohpc/pub/apps/python-virtualenv/pyvaspflow/bin/python3.6 /opt/ohpc/pub/apps/python-virtualenv/pyvaspflow/bin/pyvasp run_multi_vasp_without_job -nnum 1 -nname short_q -cnum 24 -s 1 -p 2 dir-dir-POSCAR4-2H- 3
    hecc     108275 121327  0 10:02 pts/14   00:00:00 grep --color=auto pyvasp
    xwq      132222  95242 21 08:50 pts/12   00:15:36 /opt/ohpc/pub/apps/python-virtualenv/pyvaspflow/bin/python3.6 /opt/ohpc/pub/apps/python-virtualenv/pyvaspflow/bin/pyvasp run_multi_vasp_without_job -nnum 1 -nname short_q -cnum 24 -s 0 -p 2 dir-dir-POSCAR- 3

这里你可以查看最后一列的命令来确定你要 ``kill`` 掉哪个进程, 其进程号就是第二列的数字, 例如你要杀掉第一行的进程, 那么你使用::

    $ pyvasp kill 66237

就可以了. 这里还提供了一个 ``-c`` 的参数用于选择是否取消已经在队列里面的任务, 默认是 ``True``, 你可以选择``False`` 来不选择取消队列中的任务::

    $ pyvasp kill 66237 -c False
