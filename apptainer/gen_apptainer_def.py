
import sys, os
from core.optics_spec_loader import OpticsSpec

# image is pulled into / in the container, then copied under ~/test_for running (so that files can be written)
CONTAINER_PULL_ROOT_PREFIX='image__'
RUN_SYSTEM_PREFIX='test__'

def get_section_base_container():
    s =  'Bootstrap: docker\n'
    s += 'From : ubuntu:20.04\n'
    s += '\n'
    s += '\n'
    return s

def get_section_environment(run_time_root_name):
    s =  f'    export OPICS_HOME=$HOME/{run_time_root_name}\n'
    s += f'    export PYTHONPATH=$OPICS_HOME:$OPICS_HOME/scripts/optics\n'
    s += f'    export PATH=/miniconda3/bin:$PATH\n'
    s += '\n'
    s += '\n'
    return s


def get_section_ubuntu_configure():
    s =  '    ############################################################################\n'
    s += '    # install basic linux dependencies\n'
    s += '    ############################################################################\n'
    s += '    apt-get update -y\n'
    s += '    apt-get install -y git\n'
    s += '    apt-get install -y wget\n'
    s += '    apt-get install -y unzip\n'
    s += '    apt-get install -y curl\n'

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

# def get_section_pem_file(run_time_root_name):
#     s =  '    ############################################################################\n'
#     s += f'    # pull in the key file to access ec2b machine\n'
#     s += f'    ############################################################################\n'
#     s += f'    cd /{run_time_root_name}/scripts/ec2\n'
#     s += f"    wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1BGff0DlqdUGEHtkCSK2FPjVcw7m5XpnY' -O shared-with-opics.pem\n"
#     s += '    \n'
#     s += '    \n'
#     return s

def get_section_python():
    s =  '    ############################################################################\n'
    s += '    # Install python and other tools\n'
    s += '    # Non-interactive is used to ensure prompts are omitted.\n'
    s += '    ############################################################################\n'
    s += '    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \\\n'
    s += '    build-essential \\\n'
    s += '    python3-dev \\\n'
    s += '    python3-tk \\\n'
    s += '    python3-pip \\\n'
    s += '    python3-setuptools \\\n'
    s += '    systemd \\\n'
    s += '    imagemagick \\\n'
    s += '    openslide-tools \\\n'
    s += '    libopencv-dev\n'
    s += '\n'
    s += '\n'
    return s


def get_section_miniconda_path():
    s =  '    ############################################################################\n'
    s += '    # conda env init\n'
    s += '    ############################################################################\n'
    s += '    echo "Setting conda init..."\n'
    s += '    export CONDA_PATH=$(conda info | grep -i "base environment" | cut -d ":" -f2 | cut -d " " -f2)\n'
    s += '    . $CONDA_PATH/etc/profile.d/conda.sh\n'
    s += '    echo "Setting up environment..."\n'
    s += '\n'
    s += '\n'
    return s

def get_section_opics_dependencies(pull_time_root_name, lib_config_steps):
    s =  '    ############################################################################\n'
    s += '    # install python dependencies\n'
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

def get_section_miniconda():
    s = '    ############################################################################\n'
    s += '    # install miniconda\n'
    s += '    ############################################################################\n'
    s += '    wget https://repo.anaconda.com/miniconda/Miniconda3-py39_22.11.1-1-Linux-x86_64.sh\n'
    s += '    bash Miniconda3-py39_22.11.1-1-Linux-x86_64.sh -b -p /miniconda3\n'
    s += '    export PATH=/miniconda3/bin:$PATH\n'
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
    s += '    python -m pip uninstall -y numpy\n'
    s += '    python -m pip install numpy==1.23.5\n'
    s += '\n'
    s += '\n'
    return s

def section_run_script(pull_time_root_name, optics_spec_fname):
    s =  f'    echo "...copying image /{pull_time_root_name} to runnable directory $OPICS_HOME"\n'
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
    print(f'usage:   python gen_apptainer_def.py <optics_spec_path>')
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



if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit()
    if not 'OPICS_HOME' in os.environ:
        print('...Please define OPICS_HOME...')
        sys.exit()
    opics_home = os.environ['OPICS_HOME']
    optics_spec_path   = sys.argv[1]
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

    section_base_container     = get_section_base_container()
    section_environment        = get_section_environment(run_time_root_name)
    section_ubuntu_configure   = get_section_ubuntu_configure()
    section_opics_project_code = get_section_opics_project_code(repo, branch, pull_time_root_name)
    #section_pem_file           = get_section_pem_file(run_time_root_name)
    section_python             = get_section_python()
    section_miniconda          = get_section_miniconda()
    section_miniconda_path     = get_section_miniconda_path()
    section_opics_dependencies = get_section_opics_dependencies(pull_time_root_name, lib_config_steps)
    section_models             = get_section_models(model_config_steps)
    section_numpy_hack         = get_section_numpy_hack(proj)
    section_run_script         = section_run_script(pull_time_root_name, optics_spec_fname)

    s = section_base_container
    s += '%environment\n'
    s += section_environment
    s += '%post\n'
    s += section_ubuntu_configure
    s += section_opics_project_code
    #s += section_pem_file
    s += section_python
    s += section_miniconda
    s += section_miniconda_path
    s += section_opics_dependencies
    s += section_models
    s += section_numpy_hack
    s += '%runscript\n'
    s += section_run_script

    print(s)
    optics_home = os.path.join(opics_home, 'scripts', 'optics')
    defs_dir = os.path.join(optics_home, 'apptainer', 'defs')
    os.makedirs(defs_dir, exist_ok=True)
    def_fname = optics_spec_fname.split('.')[0] + '_apptainer.def'
    def_path = os.path.join(defs_dir, def_fname)
    f = open(def_path, 'w')
    f.write(s)
    f.close()

