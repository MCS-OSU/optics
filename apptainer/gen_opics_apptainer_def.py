
import sys, os
from core.optics_spec_loader import OpticsSpec

# image is pulled into / in the container, then copied under ~/test_for running (so that files can be written)
CONTAINER_PULL_ROOT_PREFIX='image__'
RUN_SYSTEM_PREFIX='test__'

def get_section_base_container(local_image_full_path):
    s =  'Bootstrap: localimage\n'
    s += f'From : {local_image_full_path}\n'
    s += '\n'
    s += '\n'
    return s

def get_section_environment(run_time_root_name):
    s =  f'    export OPICS_HOME=$HOME/{run_time_root_name}\n'
    s += f'    export PYTHONPATH=$OPICS_HOME:$OPICS_HOME/scripts/optics\n'
    s += f'    export PATH=/miniconda3/bin:$PATH\n'
    s += f'    export OPTICS_DATASTORE=ec2b\n'
    s += '\n'
    s += '\n'
    return s


def get_section_opics_project_code(repo, branch, run_time_root_name):
    s =  '    ############################################################################\n'
    s += '    # clone the repo early in case of permissions challenge\n'
    s += '    ############################################################################\n'
    s += '    cd /\n'
    s += f'    git clone --recurse-submodules {repo} {run_time_root_name}\n'
    s += '    ############################################################################\n'
    s += '    # put the correct branches into play\n'
    s += '    ############################################################################\n'
    s += f'    cd {run_time_root_name}\n'
    s += f'    git checkout {branch}\n'
    s += f'    cd /{run_time_root_name}/scripts/optics\n'
    s += '    git checkout main\n'
    s += '\n'
    s += '\n'
    return s


def get_section_opics_dependencies(pull_time_root_name, lib_config_steps):
    s =  '    ############################################################################\n'
    s += '    # install python dependencies\n'
    s += '    #  NOTE - OPICS_HOME below is different than the one defined in the environment section\n'
    s += '    #  NOTE - OPICS_HOME here is applied during build time\n'
    s += '    #  NOTE - OPICS_HOME in the environment section is applied at container boot time\n'
    s += '    ############################################################################\n'
    s += f'    export OPICS_HOME=/{pull_time_root_name}\n'
    s += '    echo "==============  python dependencies  ==================="\n'
    for step in lib_config_steps:
        s += f'    {step}\n'
    s += '\n'
    s += '\n'
    return s


def get_section_models(model_config_steps):
    s =  '    ############################################################################\n'
    s += '    # position models\n'
    s += '    ############################################################################\n'
    s += '    echo "==============  loading models ==================="\n'
    for step in model_config_steps:
        s += f'    {step}\n'
    s += '\n'
    s += '\n'
    return s


def get_section_numpy_hack(proj):
    if proj != 'inter':
        return ''
    s = '    ############################################################################\n'
    s += '    #                   --- numpy version hack ---\n'
    s += '    # Reduce numpy version to solve error when 1.24.1 is in place:\n'
    s += "    # AttributeError: module 'numpy' has no attribute 'float'\n"
    s += '    ############################################################################\n'
    s += '    python3 -m pip uninstall -y numpy\n'
    s += '    python3 -m pip install numpy==1.23.5\n'
    s += '\n'
    s += '\n'
    return s


def section_run_script(pull_time_root_name, optics_spec_fname):

    s =  f'    echo "...checking if {pull_time_root_name} needs to be wiped..."\n'
    s += f'    if [ -d "$OPICS_HOME" ]; then\n'
    s += f'        echo "...deleting prior copy..."\n'
    s += f'        rm -rf $OPICS_HOME\n'
    s += f'        echo "...done with delete..."\n'
    s += f'    fi\n'
    s += f'    echo "...copying image /{pull_time_root_name} to runnable directory $OPICS_HOME"\n'
    s += f'    cp -r /{pull_time_root_name} $OPICS_HOME\n'
    s += f'    echo "...positioning key file for ec2b ssh commands"\n'
    s += f'    cd $OPICS_HOME/scripts/ec2\n'
    s += f'    wget --no-check-certificate "https://docs.google.com/uc?export=download&id=1BGff0DlqdUGEHtkCSK2FPjVcw7m5XpnY" -O shared-with-opics.pem\n'
    s += f'    chmod 600 shared-with-opics.pem\n'
    s += f'    echo "...running optics test_runner for {optics_spec_fname}:"\n'
    s += f'    cat $OPICS_HOME/scripts/optics/specs/{optics_spec_fname}\n'
    s += f'    cd $OPICS_HOME/scripts/optics\n'
    s += f'    echo ""\n'
    s += f'    echo ""\n'
    s += f'    echo ""\n'
    s += f'    python3 optics.py container_run specs/{optics_spec_fname}\n'
    return s


def usage():
    print(f'usage:   python gen_opics_apptainer_def.py <optics_spec_path> <local_image_full_path>')
    print('')
    print(f'(where optics_spec_path refers to an optics cfg file configured with the following keys:')
    print('')
    print(f'    apptainer.repo_to_clone:<some_repo>    (where some_repo == opics|opics-pvoe|opics-inter)')
    print('')
    print(f'    apptainer.branch_to_pull:some_branch_name>')
    print('')
    print(f'    ...one or more linux commands to configure the python dependencies, such as...')
    print(f'    apptainer.config_step.libs:./setup_python_dependencies.sh')
    print('')
    print(f'    ...one or more linux commands to position the models, such as...')
    print(f'    apptainer.config_step.models:./load_models.sh')
    print('')
    print('')
    print(f'   and <local_image_full_path> is the full bath of the base_container that has ubuntu and python')
    print('')
    print('')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
        sys.exit()

    if not 'OPICS_HOME' in os.environ:
        print('...Please define OPICS_HOME...')
        sys.exit()

    opics_home = os.environ['OPICS_HOME']
    optics_spec_path   = sys.argv[1]
    if not os.path.exists(optics_spec_path):
        print(f'given spec path does not exist {optics_spec_path}')
        sys.exit()

    local_image_full_path = sys.argv[2]
    if not os.path.exists(local_image_full_path):
        print(f'given base_container does not exist {local_image_full_path}')
        sys.exit()

    optics_spec_fname  = os.path.basename(optics_spec_path)
    optics_spec = OpticsSpec(optics_spec_path)
    proj                = optics_spec.proj
    repo_name           = optics_spec.apptainer_repo_to_clone
    repo                = 'https://github.com/MCS-OSU/' + repo_name + '.git'
    branch              = optics_spec.apptainer_branch_to_pull
    lib_config_steps    = optics_spec.apptainer_lib_config_steps
    model_config_steps  = optics_spec.apptainer_model_config_steps
    spec_name           = optics_spec.config_name
    pull_time_root_name = f'{CONTAINER_PULL_ROOT_PREFIX}{spec_name}'
    run_time_root_name   = f'{RUN_SYSTEM_PREFIX}{spec_name}'

    
    s = get_section_base_container(local_image_full_path)
    s += '%environment\n'
    s += get_section_environment(run_time_root_name)
    s += '%post\n'
    s += get_section_opics_project_code(repo, branch, pull_time_root_name)
    s += get_section_opics_dependencies(pull_time_root_name, lib_config_steps)
    s += get_section_models(model_config_steps)
    s += get_section_numpy_hack(proj)
    s += '%runscript\n'
    s += section_run_script(pull_time_root_name, optics_spec_fname)

    print(s)
    optics_home = os.path.join(opics_home, 'scripts', 'optics')
    defs_dir = os.path.join(optics_home, 'apptainer', 'defs')
    os.makedirs(defs_dir, exist_ok=True)
    def_fname = optics_spec_fname.split('.')[0] + '.def'
    def_path = os.path.join(defs_dir, def_fname)
    f = open(def_path, 'w')
    f.write(s)
    f.close()
