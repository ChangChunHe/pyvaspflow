import os,subprocess,shutil,logging
from time import sleep
from pyvaspflow.utils import read_config


config = read_config()


class Schedule():
    def __init__(self):

        if config["Task_Schedule"]["default_schedule"] == "SLURM":
            self.schedule_type = Slurm()

        elif config["Task_Schedule"]["default_schedule"] == "LSF":
            self.schedule_type = LSF()


class Slurm():
    def __init__(self):
        pass

    def is_inqueue(self,pid):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        que_res = p.stdout.readlines()
        p.stdout.close()
        for ii in que_res:
            if str(pid) in ii.decode('utf-8'):
                return True
        return False

    def num_of_job_inqueue(self,pid_list):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        num = 0
        for _pid in pid_list:
            for line in sinf_res:
                if len(line.strip()) == 0:
                    continue
                if  _pid in line.split()[0]:
                    num += 1
        return num

    def node_is_idle(self,node_name):
        p = subprocess.Popen('sinfo',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        for line in sinf_res:
            if 'idle' in line and node_name in line:
                return True
        return False

    def is_job_running(self,pid):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        for line in sinf_res:
            if ' R ' in  line and pid in line:
                return True
        return False

    def is_job_pd(self,pid):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        for line in sinf_res:
            if ' PD ' in  line and pid in line:
                return True
        return False

    def cancel_job(self,pid):
        while True:
            p = subprocess.Popen(['scancel',pid],stdout=subprocess.PIPE)
            if not self.is_inqueue(pid):
                break

    def write_job_file(self,node_name,cpu_num,node_num,job_name):
        with open(os.path.join(os.getcwd(),job_name,'job.sh'),'w') as f:
            f.writelines('#!/bin/bash -l\n')
            f.writelines('#SBATCH -J '+job_name+'\n')
            f.writelines('#SBATCH -p '+node_name+' -N '+ str(int(node_num)) +' -n '+str(int(cpu_num))+'\n\n')
            f.writelines(config['RUN_VASP']['prepend']+'\n')
            f.writelines(config['RUN_VASP']['exec']+'\n')
            if "append" in config["RUN_VASP"]:
                f.writelines(config['RUN_VASP']['append']+'\n')

    def submit_job(self,job_name):
        res = subprocess.Popen(['/bin/my_sbatch', './job.sh'],stdout=subprocess.PIPE,cwd=job_name)
        std = res.stdout.readlines()
        res.stdout.close()
        pid = std[0].decode("utf-8").split()[-1]
        try:
            int(pid)
        except:
            raise ValueError("Too many jobs you have submitted")
        logging.info(job_name+" calculation has been submitted, the queue id is "+pid)
        logging.info("The work dir is "+os.path.join(os.getcwd(),job_name))
        return pid

    def submit_job_without_job(self,job_name,node_name,cpu_num,node_num=1,submit_job_idx=0):
        has_write_job = False
        for idx in range(len(node_name)):
            if self.node_is_idle(node_name[idx]):
                self.write_job_file(job_name=job_name,node_name=node_name[idx],cpu_num=cpu_num[idx],node_num=node_num)
                has_write_job = True
                node_submitted = node_name[idx]
                break
        if not has_write_job:
            self.write_job_file(job_name=job_name,node_name=node_name[submit_job_idx],cpu_num=cpu_num[submit_job_idx],node_num=node_num)
            node_submitted = node_name[submit_job_idx]
            submit_job_idx += 1
            if submit_job_idx == len(node_name):
                submit_job_idx = 0
        res = subprocess.Popen(['/bin/my_sbatch', './job.sh'],stdout=subprocess.PIPE,cwd=job_name)
        std = res.stdout.readlines()
        res.stdout.close()
        pid = std[0].decode('utf-8').split()[-1]
        try:
            int(pid)
        except:
            raise ValueError("Too many jobs you have submitted")
        logging.info(job_name+" calculation has been submitted, the queue id is "+pid)
        logging.info("The work dir is "+os.path.join(os.getcwd(),job_name))
        sleep(5)
        return pid,submit_job_idx



class LSF():
    def __init__(self):
        pass

    def is_inqueue(self,pid):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        que_res = p.stdout.readlines()
        p.stdout.close()
        for ii in que_res:
            if str(pid) in ii.decode('utf-8'):
                return True
        return False

    def num_of_job_inqueue(self,pid_list):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        num = 0
        for _pid in pid_list:
            for line in sinf_res:
                if len(line.strip()) == 0:
                    continue
                if  _pid in line.split()[0]:
                    num += 1
        return num

    def node_is_idle(self,node_name):
        p = subprocess.Popen('sinfo',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        for line in sinf_res:
            if 'idle' in line and node_name in line:
                return True
        return False

    def is_job_running(self,pid):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        for line in sinf_res:
            if ' R ' in  line and pid in line:
                return True
        return False

    def is_job_pd(self,pid):
        p = subprocess.Popen('squeue',stdout=subprocess.PIPE)
        sinf_res = p.stdout.read()
        sinf_res = sinf_res.decode('utf-8').split('\n')
        p.stdout.close()
        for line in sinf_res:
            if ' PD ' in  line and pid in line:
                return True
        return False

    def cancel_job(self,pid):
        while True:
            p = subprocess.Popen(['scancel',pid],stdout=subprocess.PIPE)
            if not self.is_inqueue(pid):
                break

    def write_job_file(self,node_name,cpu_num,node_num,job_name):
        with open(os.path.join(os.getcwd(),job_name,'job.sh'),'w') as f:
            f.writelines('#!/bin/sh -l\n')
            f.writelines('#BSUB -q '+node_name +'\n')
            f.writelines('#BSUB -n '+cpu_num +'\n')
            f.writelines('#BSUB -e %J.err\n')
            f.writelines('#BSUB -o %J.out\n')
            f.writelines('#BSUB -R "span[ptile=24]"\n')
            f.writelines('hostfile=`echo $LSB_DJOB_HOSTFILE`\n')
            f.writelines('NP=`cat $hostfile | wc -l`\n\n')
            f.writelines(config['RUN_VASP']['prepend']+'\n')
            f.writelines(config['RUN_VASP']['exec']+'\n')
            if "append" in config["RUN_VASP"]:
                f.writelines(config['RUN_VASP']['append']+'\n')

    def submit_job(self,job_name):
        res = subprocess.Popen(['/bin/my_sbatch', './job.sh'],stdout=subprocess.PIPE,cwd=job_name)
        std = res.stdout.readlines()
        res.stdout.close()
        pid = std[0].decode("utf-8").split()[-1]
        try:
            int(pid)
        except:
            raise ValueError("Too many jobs you have submitted")
        logging.info(job_name+" calculation has been submitted, the queue id is "+pid)
        logging.info("The work dir is "+os.path.join(os.getcwd(),job_name))
        return pid

    def submit_job_without_job(self,job_name,node_name,cpu_num,node_num=1,submit_job_idx=0):
        has_write_job = False
        for idx in range(len(node_name)):
            if self.node_is_idle(node_name[idx]):
                self.write_job_file(job_name=job_name,node_name=node_name[idx],cpu_num=cpu_num[idx],node_num=node_num)
                has_write_job = True
                node_submitted = node_name[idx]
                break
        if not has_write_job:
            self.write_job_file(job_name=job_name,node_name=node_name[submit_job_idx],cpu_num=cpu_num[submit_job_idx],node_num=node_num)
            node_submitted = node_name[submit_job_idx]
            submit_job_idx += 1
            if submit_job_idx == len(node_name):
                submit_job_idx = 0
        res = subprocess.Popen(['/bin/my_sbatch', './job.sh'],stdout=subprocess.PIPE,cwd=job_name)
        std = res.stdout.readlines()
        res.stdout.close()
        pid = std[0].decode('utf-8').split()[-1]
        try:
            int(pid)
        except:
            raise ValueError("Too many jobs you have submitted")
        logging.info(job_name+" calculation has been submitted, the queue id is "+pid)
        logging.info("The work dir is "+os.path.join(os.getcwd(),job_name))
        sleep(5)
        return pid,submit_job_idx
