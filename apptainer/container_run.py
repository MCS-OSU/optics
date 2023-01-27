import os

# This script will be positioned as the script that will run when the container is run.
# -assumes OPICS_HOME is set in the container
# -assumes the opics_pull dir is at the root of the container and named with prefix opics_pull_
# -assumes the optics_spec_name will be the remainder of the opics_pull dir name beyond the prefix opics_pull_
def get_opics_pull_dirname():
    items = os.listdir('/')
    for item in items:
        if item.startswith('opics_pull_'):
            return item

def get_optics_spec_file(opics_pull_dirname):
    return opics_pull_dirname.replace('opics_pull_', '') + '.cfg'

def get_target_dir_under_home():
    if not 'OPICS_HOME' in os.environ:
        raise Exception('OPICS_HOME not set in this container')
    return os.environ['OPICS_HOME']

if __name__ == '__main__':
    # find the dir under container root that starts with opics_pull
    opics_pull_dirname = get_opics_pull_dirname()
    opics_pull_dir = os.path.join('/', opics_pull_dirname)
    print(f'...opics_pull is found at {opics_pull_dir} in the container...')

    opics_run_dir = get_target_dir_under_home()
    print(f'...copying it into {opics_run_dir} under your home dir so that it can write to the filesystem...')
    # copy the opics_pull dir to the target dir under home so that the system can write to disk
    os.system(f'cp -r {opics_pull_dir} {opics_run_dir}')

    # get the name of the optics spec file to run
    optics_spec_file = get_optics_spec_file(opics_pull_dirname)
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


