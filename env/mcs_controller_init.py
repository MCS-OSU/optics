
import os


class McsControllerInit():
    def __init__(self, known_paths):
        self.known_paths = known_paths
        
    def patch_timeout(self, num_seconds):
        print('')
        print('attempting to patch installed package machine_common_sense/__init__.py TIME_LIMIT_SECONDS value...')
        print('')
        patched = False
        for path in self.known_paths:
            if os.path.exists(path):
                print(f'mcs init file located at : {path}')
                f = open(path,'r')
                lines = f.readlines()
                f.close()
                mcs_init_tmp_path = 'tmp_patch_copy'
                f = open(mcs_init_tmp_path,'w')
                for line in lines:
                    if line.startswith('TIME_LIMIT_SECONDS'):
                        print(f'...initally set as:')
                        print(line)
                        f.write(f'TIME_LIMIT_SECONDS = {num_seconds}\n')
                    else:
                        f.write(line)
                f.close()

                os.system(f'rm {path}')
                os.system(f'mv {mcs_init_tmp_path} {path}')
                print(f'...now set to: ')
                os.system(f'cat {path} | grep "TIME_LIMIT_SECONDS ="')
                print('')
                patched = True
        if not patched:
            print('')
            print('ERROR - unable to patch machine_common_sense/__init__.py with new timeout - file not in expected location - did you forget to activate the conda environment?')
            print('')
                
                
                
class McsControllerInitPvoe(McsControllerInit):
    def __init__(self):
        known_paths = []
        # container
        known_paths.append('/miniconda3/envs/env_opics_pvoe/lib/python3.7/site-packages/machine_common_sense/__init__.py')
        # ec2
        known_paths.append('/home/ubuntu/anaconda3/envs/env_opics_pvoe/lib/python3.7/site-packages/machine_common_sense/__init__.py')
        super(McsControllerInitPvoe, self).__init__(known_paths)
    
     
class McsControllerInitAvoe(McsControllerInit):
    def __init__(self):
        known_paths = []
        # container
        known_paths.append('/miniconda3/envs/env_avoe/lib/python3.7/site-packages/machine_common_sense/__init__.py')
        # ec2
        known_paths.append('/home/ubuntu/anaconda3/envs/env_avoe/lib/python3.7/site-packages/machine_common_sense/__init__.py')
        super(McsControllerInitAvoe, self).__init__(known_paths)
    
     
class McsControllerInitInter(McsControllerInit):
    def __init__(self):
        known_paths = []
        # container
        known_paths.append('/miniconda3/envs/env_opics_inter/lib/python3.9/site-packages/machine_common_sense/__init__.py')
        # ec2
        known_paths.append('/home/ubuntu/anaconda3/envs/env_opics_inter/lib/python3.9/site-packages/machine_common_sense/__init__.py')
        super(McsControllerInitInter, self).__init__(known_paths)
    