
import os


class McsControllerInit():
    def __init__(self, known_paths):
        self.known_paths = known_paths
        
    def patch_timeout_for_path(self, path, num_minutes):
        if os.path.exists(path):
            print(f'mcs init file located at : {path}')
            print(f'{num_minutes} minutes will be converted to {int(num_minutes)*60} seconds for the TIME_LIMIT_SECONDS value ')
            f = open(path,'r')
            lines = f.readlines()
            f.close()
            mcs_init_tmp_path = 'tmp_patch_copy'
            f = open(mcs_init_tmp_path,'w')
            for line in lines:
                if line.startswith('TIME_LIMIT_SECONDS'):
                    print(f'...initally set as:')
                    print(line)
                    f.write(f'TIME_LIMIT_SECONDS = {int(num_minutes)*60}\n')
                else:
                    f.write(line)
            f.close()

            os.system(f'rm {path}')
            os.system(f'mv {mcs_init_tmp_path} {path}')
            print(f'...now set to: ')
            os.system(f'cat {path} | grep "TIME_LIMIT_SECONDS ="')
            print('')
            return True
        return False

    def use_conda_env_prefix_to_find_file(self):
        if not 'CONDA_PREFIX' in os.environ:
            return False
        root = os.environ['CONDA_PREFIX']
        tmp_file = 'junk.txt'
        os.system(f'find {root} | grep machine_common_sense/__init > {tmp_file}')
        f = open(tmp_file, 'r')
        lines = f.readlines()
        f.close()
        os.system(f'rm {tmp_file}')
        for line in lines:
            if line.startswith(root):
                return line.rstrip()
        return False


    def patch_timeout(self, num_minutes):
        print('')
        print('attempting to patch installed package machine_common_sense/__init__.py TIME_LIMIT_SECONDS value...')
        print('')
        patched = False
        for path in self.known_paths:
            if os.path.exists(path):
                print(f'mcs init file found at {path} - will attempt to patch')
                if self.patch_timeout_for_path(path, num_minutes):
                    print('patch successful')
                    patched = True

        if not patched:
            print('mcs init file not found in known locations - searching using CONDA ENV prefix')
            error_string = '\nERROR - unable to patch machine_common_sense/__init__.py with new timeout - file not in expected locations - did you forget to activate the conda environment?\n'
            path = self.use_conda_env_prefix_to_find_file()
            if path!= False:
                if os.path.exists(path):
                    if self.patch_timeout_for_path(path, num_minutes):
                        print('patch successful')
                    else:
                        print(error_string)
                else:
                    print(error_string)
            else:
                print('failed to find mcs controller __init__.py file')
                
                
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
    