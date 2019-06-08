from os import pardir,path,mkdir
import json

home = path.expanduser("~")

if not path.isdir(path.join(home,'.config')):
    mkdir(path.join(home,'.config'))

if not path.isdir(path.join(home,'.config','pyvaspflow')):
    mkdir(path.join(home,'.config','pyvaspflow'))

if not path.isfile(path.join(home,'.config','pyvaspflow','conf.json')):
    json_f = {"potcar_path":
                 {"paw_PBE":"/opt/ohpc/pub/apps/vasp/pps/paw_PBE",
                  "paw_LDA":"/opt/ohpc/pub/apps/vasp/pps/paw_LDA",
                  "paw_PW91":"/opt/ohpc/pub/apps/vasp/pps/paw_PW91",
                  "USPP_LDA":"/opt/ohpc/pub/apps/vasp/pps/USPP_LDA",
                  "USPP_PW91":"/opt/ohpc/pub/apps/vasp/pps/USPP_PW91"},
             "job":
                 {"prepend": "module load vasp/5.4.4-impi-mkl",
                  "exec": "mpirun -n ${SLURM_NPROCS} vasp_std"}}

    with open(path.join(home,'.config','pyvaspflow','conf.json'),'w') as outfile:
        json.dump(json_f,outfile,ensure_ascii=False)
        outfile.write('\n')
