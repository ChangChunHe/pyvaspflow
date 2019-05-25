.. _Installation:

=============
快速安装
=============

你可以通过源码进行安装, 这里我们建议安装在服务器上.

```shell
pip install -e . # -e for developer
```

下面是配置文件, 用于指定赝势的位置和`job.sh`文件的书写.

```json
{
"potcar_path":
{"paw_PBE":"/opt/ohpc/pub/apps/vasp/pps/paw_PBE",
"paw_LDA":"/opt/ohpc/pub/apps/vasp/pps/paw_LDA",
"paw_PW91":"/opt/ohpc/pub/apps/vasp/pps/paw_PW91",
"USPP_LDA":"/opt/ohpc/pub/apps/vasp/pps/USPP_LDA",
"USPP_PW91":"/opt/ohpc/pub/apps/vasp/pps/USPP_PW91"
},
"job":{
"prepend": "module load vasp/5.4.4-impi-mkl",
"exec": "mpirun -n ${SLURM_NPROCS} vasp_std"
}
}
```
