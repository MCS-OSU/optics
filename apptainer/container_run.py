import os

from apptainer.gen_apptainer_def import CONTAINER_PULL_ROOT_PREFIX

# This script will be configured in the container as the script that will execute when the container is run.
# -assumes OPICS_HOME is set in the container
# -assumes the opics_pull dir is at the root of the container and named with prefix opics_pull_
# -assumes the optics_spec_name will be the remainder of the opics_pull dir name beyond the prefix opics_pull_
def get_opics_read_only_image_dirname():
    items = os.listdir('/')
    for item in items:
        if item.startswith(CONTAINER_PULL_ROOT_PREFIX):
            return item

def get_optics_spec_fname(opics_pull_dirname):
    return opics_pull_dirname.replace(CONTAINER_PULL_ROOT_PREFIX, '') + '.cfg'

def get_opics_home():
    if not 'OPICS_HOME' in os.environ:
        raise Exception('OPICS_HOME not set in this container - cannot run scenes for optics.')
    return os.environ['OPICS_HOME']

if __name__ == '__main__':
    # find the dir under container root that starts with opics_pull
    opics_read_only_image_dirname = get_opics_read_only_image_dirname()
    opics_pull_dir = os.path.join('/', opics_read_only_image_dirname)  
    print(f'...opics_pull is found at {opics_pull_dir} in the container...')

    opics_run_dir = get_opics_home()
    print(f'...copying it into {opics_run_dir} under your home dir so that it can write to the filesystem...')
  
    # pull in the pem file 
    os.chdir(f'{opics_run_dir}/scripts/ec2')
    print(f'...pulling pem file for accessing ec2b...')
    os.system("wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1BGff0DlqdUGEHtkCSK2FPjVcw7m5XpnY' -O shared-with-opics.pem")


    # get the name of the optics spec file to run
    optics_spec_file = get_optics_spec_fname(opics_read_only_image_dirname)
    print(f'...running optics with spec file {optics_spec_file}:')
    os.system('cat {opics_run_dir}/scripts/optics/specs/{optics_spec_file}')
    # cd into optics
    optics_dir = os.path.join(opics_run_dir, 'scripts', 'optics')
    os.chdir(optics_dir)
    print('')
    print('')
    print(f'...now launching optics to run scenes...')
    print('')
    print('')
    os.system(f'python3 optics.py container_run specs/{optics_spec_file}')


