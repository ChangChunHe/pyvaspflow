#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from pyvaspflow.vasp import prep_vasp
from pyvaspflow.utils import add_log_shell_file
from time import sleep,ctime
from pyvaspflow.vasp.schedule import Schedule
import os,logging


schedule = Schedule()

def has_job_finished(folder):
    if (not os.path.isfile(os.path.join(folder,"EIGENVAL"))) or (not os.path.isfile(os.path.join(folder,"EIGENVAL"))):
        return False
    size = os.path.getsize(os.path.join(folder,"EIGENVAL")) + os.path.getsize(os.path.join(folder,"DOSCAR"))
    if size < 1000:
        return False
    return True



def get_number_of_running_shell_files(shell_file,main_pid):
    p = subprocess.Popen(['ps', '-ef'],stdout=subprocess.PIPE)
    que_res = p.stdout.readlines()
    p.stdout.close()
    pid_res = [i  for i in que_res if 'bash '+shell_file in i.decode("utf-8") and str(main_pid) in i.decode("utf-8") ]
    p.kill()
    return len(pid_res)


def run_single_vasp(job_name,is_login_node=False,cpu_num=24,cwd="",main_pid=None):
    if not main_pid:
        main_pid = os.getpid()
    job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(main_pid))
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename=os.path.join(cwd,'run-'+str(main_pid)+'.log'),
        filemode='a')

    job_id = schedule.schedule_type.submit_job(job_name)
    logging.info(job_name+" calculation has submitted at calculation node")
    # pid = os.getpid()
    # job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(pid))
    with open(job_id_file,'a') as f:
        f.writelines(job_id+"\n")
    while True:
        if not schedule.schedule_type.is_inqueue(job_id):
            logging.info(job_name+" in dir of "+os.getcwd()+" calculation finished")
            break
        sleep(5)


def run_single_vasp_without_job(job_name,node_name,cpu_num,node_num=1,cwd="",main_pid=None):
    if not main_pid:
        main_pid = os.getpid()
        job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(main_pid))
    else:
        job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(main_pid))
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename=os.path.join(cwd,'run-'+str(main_pid)+'.log'),
        filemode='a')
    job_id,submit_job_idx = schedule.schedule_type.submit_job_without_job(job_name,node_name,cpu_num,node_num=1)
    with open(job_id_file,'a') as f:
        f.writelines(job_id+"\n")
    sleep(5)
    while True:
        for idx,nname in enumerate(node_name):
            if schedule.schedule_type.node_is_idle(nname) and schedule.schedule_type.is_job_pd(job_id):
                os.system("scancel "+job_id)
                logging.info(job_name+" has been cancelled, the queue id is "+job_id)
                schedule.schedule_type.write_job_file(job_name,nname,cpu_num[idx],node_num)
                res = subprocess.Popen(['sbatch', './job.sh'],stdout=subprocess.PIPE,cwd=job_name)
                std = res.stdout.readlines()
                res.stdout.close()
                job_id = std[0].decode('utf-8').split()[-1]
                logging.info(job_name+" has been submitted at "+nname+" node, the queue id is "+job_id)
                with open(job_id_file,'a') as f:
                    f.writelines(job_id+"\n")
            sleep(5)
        if not is_inqueue(job_id):
            logging.info(job_name+" in dir of "+os.getcwd()+" calculation finished")
            break
        sleep(5)


def run_multi_vasp(job_name='task',end_job_num=1,start_job_num=0,job_list=None,par_job_num=4,cwd=""):
    pid = os.getpid()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=os.path.join(cwd,'run-'+str(pid)+'.log'),
                        filemode='a')

    job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(pid))
    start_job_num,end_job_num,par_job_num = int(start_job_num),int(end_job_num),int(par_job_num)
    jobid_pool = []
    idx = start_job_num
    for ii in range(min(par_job_num,end_job_num-start_job_num)):
        _job_id = schedule.schedule_type.submit_job(job_name+str(ii+start_job_num))
        jobid_pool.append(_job_id)
        with open(job_id_file,'a') as f:
            f.writelines(_job_id+"\n")
        idx += 1
    if idx == end_job_num+1:
        return
    while True:
        inqueue_num = schedule.schedule_type.num_of_job_inqueue(jobid_pool)
        logging.info(str(inqueue_num)+" in queue")
        if inqueue_num < par_job_num and idx < end_job_num+1:
            _job_id = schedule.schedule_type.submit_job(job_name + str(idx))
            jobid_pool.append(_job_id)
            with open(job_id_file,'a') as f:
                f.writelines(_job_id+"\n")
            idx += 1
        sleep(5)
        if idx == end_job_num+1 and schedule.schedule_type.num_of_job_inqueue(jobid_pool) == 0:
            return


def run_multi_vasp_without_job(job_name='task',end_job_num=1,node_name="short_q",cpu_num=24,node_num=1,start_job_num=0,par_job_num=4,cwd=""):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=os.path.join(cwd,'run-'+str(os.getpid())+'.log'),
                        filemode='a')
    main_pid = os.getpid()
    job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(main_pid))
    with open(job_id_file,'w') as f:
        pass
    submit_job_idx = 0
    start_job_num,end_job_num,par_job_num = int(start_job_num),int(end_job_num),int(par_job_num)
    jobid_pool = []
    idx = start_job_num
    for ii in range(min(par_job_num,end_job_num-start_job_num)):
        _job_id,submit_job_idx = schedule.schedule_type.submit_job_without_job(job_name+str(ii+start_job_num),node_name,cpu_num,node_num=1,submit_job_idx=submit_job_idx)
        jobid_pool.append(_job_id)
        with open(job_id_file,'a') as f:
            f.writelines(_job_id+"\n")
        idx += 1
    if idx == end_job_num + 1:
        return
    while True:
        inqueue_num = schedule.schedule_type.num_of_job_inqueue(jobid_pool)
        logging.info(str(inqueue_num)+" in queue")
        if inqueue_num < par_job_num and idx < end_job_num+1:
            _job_id,submit_job_idx = schedule.schedule_type.submit_job_without_job(job_name + str(idx),node_name,cpu_num,node_num=1,submit_job_idx=submit_job_idx)
            jobid_pool.append(_job_id)
            with open(job_id_file,'a') as f:
                f.writelines(_job_id+"\n")
            idx += 1
            sleep(5)
        sleep(5)
        if idx == end_job_num+1 and schedule.schedule_type.num_of_job_inqueue(jobid_pool) == 0:
            return


def run_multi_vasp_with_shell(work_name,shell_file,end_job_num=1,start_job_num=0,par_job_num=4):
    cwd = os.getcwd()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=os.path.join(cwd,'run-'+str(os.getpid())+'.log'),
                        filemode='a')
    main_pid = os.getpid()
    job_id_file = os.path.join(os.path.expanduser("~"),'.config','pyvaspflow',str(main_pid))

    start_job_num,end_job_num,par_job_num = int(start_job_num),int(end_job_num),int(par_job_num)
    pid_pool = []
    idx = start_job_num
    for ii in range(min(par_job_num,end_job_num-start_job_num)):
        if os.path.isdir(work_name+str(idx)):
            shutil.rmtree(work_name+str(idx))
        os.makedirs(work_name+str(idx))
        shutil.copyfile("POSCAR"+str(idx),work_name+str(idx)+"/POSCAR")
        new_lines = add_log_shell_file(shell_file,cwd,main_pid)
        with open(work_name+str(idx)+"/"+shell_file,"w") as f:
            f.writelines(new_lines)
        res = subprocess.Popen(['bash',shell_file],cwd=work_name+str(idx))
        pid_pool.append(res.pid)
        idx += 1
        sleep(5)
    if idx == end_job_num+1:
        return
    while True:
        inqueue_num = get_number_of_running_shell_files(shell_file,main_pid)
        logging.info(str(inqueue_num)+" in queue")
        if inqueue_num < par_job_num and idx < end_job_num+1:
            if os.path.isdir(work_name+str(idx)):
                shutil.rmtree(work_name+str(idx))
            os.makedirs(work_name+str(idx))
            shutil.copyfile("POSCAR"+str(idx),work_name+str(idx)+"/POSCAR")
            new_lines = add_log_shell_file(shell_file,cwd,main_pid)
            with open(work_name+str(idx)+"/"+shell_file,"w") as f:
                f.writelines(new_lines)
            res = subprocess.Popen(['bash',shell_file],cwd=work_name+str(idx))
            pid_pool.append(res.pid)
            idx += 1
            sleep(5)
        if idx == end_job_num+1 and get_number_of_running_shell_files(shell_file,main_pid) == 0:
            break
        sleep(60)
