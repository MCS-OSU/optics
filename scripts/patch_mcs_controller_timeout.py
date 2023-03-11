
import os


if __name__ == '__main__':
    #/home/ubuntu/anaconda3/envs/env_opics_pvoe/lib/python3.7/site-packages/machine_common_sense/__init__.py

    mcs_init_path = '/home/ubuntu/anaconda3/envs/env_opics_pvoe/lib/python3.7/site-packages/machine_common_sense/__init__.py'
    f = open(mcs_init_path,'r')
    lines = f.readlines()
    f.close()
    mcs_init_tmp_path = '/home/ubuntu/anaconda3/envs/env_opics_pvoe/lib/python3.7/site-packages/machine_common_sense/tmp__init__.py'
    f = open(mcs_init_tmp_path,'w')
    for line in lines:
        if line.startswith('TIME_LIMIT_SECONDS'):
            f.write('TIME_LIMIT_SECONDS = 3600\n')
        else:
            f.write(line)
    f.close()

    os.system(f'rm {mcs_init_path}')
    os.system(f'mv {mcs_init_tmp_path} {mcs_init_path}')
    print('timeout setting now is: ')
    os.system(f'cat {mcs_init_path} | grep TIME_LIMIT_SECONDS')
