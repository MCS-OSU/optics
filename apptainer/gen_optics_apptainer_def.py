
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

def get_section_environment(proj, run_time_root_name):
    s =  f'    export OPTICS_HOME=$HOME/{run_time_root_name}\n'
    if proj == 'avoe':
        s += f'    export OPICS_HOME=$OPTICS_HOME/opics\n'
    else:
        s += f'    export OPICS_HOME=$OPTICS_HOME/opics_{proj}\n'
    s += f'    export PYTHONPATH=$OPTICS_HOME:$OPTICS_HOME/opics_common\n'
    s += f'    export PATH=/miniconda3/bin:$PATH\n'
    s += f'    export OPTICS_DATASTORE=ec2b\n'
    s += '\n'
    s += '\n'
    return s

def get_section_position_run_script(spec_name):
    s =  f'    cp /tmp/run_{spec_name}.sh /\n'
    s += f'    chmod 770 /run_{spec_name}.sh\n\n'
    return s


def get_section_opics_project_code(optics_branch, proj, project_branch,  pull_time_root_name):
    s =  '    ############################################################################\n'
    s += '    # clone the optics repo early in case of permissions challenge\n'
    s += '    ############################################################################\n'
    s += '    cd /\n'
    s += f'    git clone --recurse-submodules https://github.com/MCS-OSU/optics.git {pull_time_root_name}\n'
    s += '    ############################################################################\n'
    s += '    # put the correct branches into play\n'
    s += '    ############################################################################\n'
    s += f'    cd {pull_time_root_name}\n'
    s += f'    git checkout {optics_branch}\n'
    s += f'    git submodule update --init --recursive\n'
    # git the correct branch for the project
    dirname_for_proj = f'opics_{proj}'
    proj_pull_dir = os.path.join(pull_time_root_name, dirname_for_proj)
    s += f'    cd /{proj_pull_dir}\n'
    s += f'    git checkout {project_branch}\n'

    # checkout opics_common  main
    opics_common_pull_dir = os.path.join(pull_time_root_name, 'opics_common')
    s += f'    cd /{opics_common_pull_dir}\n'
    s += f'    git checkout main\n'

    s += '\n'
    s += '\n'
    return s


def get_section_opics_dependencies(proj, pull_time_root_name, lib_config_steps):
    s =  '    ############################################################################\n'
    s += '    # install python dependencies\n'
    s += '    ############################################################################\n'
    s += f'    export OPTICS_HOME=/{pull_time_root_name}\n'
    s += '    echo "==============  python dependencies  ==================="\n'
    dirname_for_proj = f'opics_{proj}'
    proj_pull_dir = os.path.join(pull_time_root_name, dirname_for_proj)
    s += f'    cd /{proj_pull_dir}\n'
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

def get_section_controller_timeout_patch():
    s = '    ############################################################################\n'
    s += '    #                   --- mcs controller timeout patch ---\n'
    s += '    # changing from 3 mins to 1 hour:\n'
    s += '    ############################################################################\n'
    s += '    cd $OPTICS_HOME/scripts'
    s += '    python3 patch_mcs_controller_timeout.pyn'
    s += '\n'
    s += '\n'
    return s



def get_section_run_script(spec_name):
    s = f'/run_{spec_name}.sh $1 $2\n'
    return s

def generate_run_script(proj, pull_time_root_name, optics_spec_fname, spec_name):
    s =  f'#!/bin/bash\n'
    s += f'echo "...checking if {pull_time_root_name} needs to be wiped..."\n'
    s += f'if [ -d "$OPTICS_HOME" ]; then\n'
    s += f'    echo "...deleting prior copy..."\n'
    s += f'    rm -rf $OPTICS_HOME\n'
    s += f'    echo "...done with delete..."\n'
    s += f'fi\n'
    s += f'echo "...copying image /{pull_time_root_name} to runnable directory $OPTICS_HOME"\n'
    s += f'cp -r /{pull_time_root_name} $OPTICS_HOME\n'

    if proj == 'avoe':
        s += f'echo "...adding avoe pull to path since its not installed by poetry for eval6"\n'
        s += f'export PYTHONPATH=$PYTHONPATH:$OPTICS_HOME/opics\n'
    else:
        s += f'echo "...running  . /miniconda3/etc/profile.d/conda.sh"\n'
        s += f'. /miniconda3/etc/profile.d/conda.sh\n'
        s += f'echo "...conda activate env_opics_{proj}"\n'
        s += f'conda activate env_opics_{proj}\n'
        s += f'echo "...conda activate complete"\n'
        s += f'pip list\n'

    s += f'echo "...positioning key file for ec2b ssh commands"\n'
    s += f'cd $OPTICS_HOME/scripts/ec2\n'
    s += f'wget --no-check-certificate "https://docs.google.com/uc?export=download&id=1BGff0DlqdUGEHtkCSK2FPjVcw7m5XpnY" -O shared-with-opics.pem\n'
    s += f'chmod 600 shared-with-opics.pem\n'
    s += f'echo "arg decides on optics run vs run_opics_scene"\n'
    s += f'if [[ $1 == optics ]]; then\n'
    s += f'    echo "...running optics test_runner for {optics_spec_fname}:"\n'
    s += f'    cat $OPTICS_HOME/specs/{optics_spec_fname}\n'
    s += f'    cd $OPTICS_HOME\n'
    s += f'    echo ""\n'
    s += f'    echo ""\n'
    s += f'    echo "running - python3 optics.py container_run specs/{optics_spec_fname}"\n'
    s += f'    python3 optics.py container_run specs/{optics_spec_fname}\n'
    s += f'elif [[ $1 == run_opics_scene ]]; then\n'
    s += f'    if [ -z "$2" ]; then\n'
    s += f'        echo "run_opics_scene arg requires the scene path to be the additional arg"\n'
    s += f'    else\n'
    s += f'        echo "...running single optics scene $2:"\n'
    s += f'        cd $OPTICS_HOME/scripts\n'
    s += f'        echo ""\n'
    s += f'        echo ""\n'
    s += f'        echo "running - python3 run_opics_scene.py --scene $2 --controller mcs --log_dir logs"\n'
    s += f'        python3 run_opics_scene.py --scene $2 --controller mcs --log_dir logs\n'
    s += f'    fi\n'
    s += f'else\n'
    s += f'    echo "command $1 not recognized"\n'
    s += f'fi\n'

    os.makedirs('run_scripts', exist_ok = True)
    run_script_path = os.path.join('run_scripts', 'run_' + spec_name + '.sh')
    f = open(run_script_path, 'w')
    f.write(s)
    f.close()
    command = f'cp {run_script_path} /tmp/run_{spec_name}.sh'
    os.system(command)


def usage():
    print(f'usage:   python gen_optics_apptainer_def.py <optics_spec_path> <local_image_full_path>')
    print('')
    print(f'(where optics_spec_path refers to an optics cfg file configured with the following keys:')
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

    if not 'OPTICS_HOME' in os.environ:
        print('...Please define OPTICS_HOME...')
        sys.exit()

    optics_home = os.environ['OPTICS_HOME']
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
    project_branch      = optics_spec.apptainer_branch_to_pull
    lib_config_steps    = optics_spec.apptainer_lib_config_steps
    model_config_steps  = optics_spec.apptainer_model_config_steps
    spec_name           = optics_spec.config_name
    pull_time_root_name = f'{CONTAINER_PULL_ROOT_PREFIX}{spec_name}'
    run_time_root_name   = f'{RUN_SYSTEM_PREFIX}{spec_name}'

    optics_branch = 'main'

    generate_run_script(proj, pull_time_root_name, optics_spec_fname, spec_name)



    s = get_section_base_container(local_image_full_path)
    s += '%environment\n'
    s += get_section_environment(proj, run_time_root_name)
    s += '%post\n'
    s += get_section_position_run_script(spec_name)
    s += get_section_opics_project_code(optics_branch, proj, project_branch, pull_time_root_name)
    s += get_section_opics_dependencies(proj, pull_time_root_name, lib_config_steps)
    s += get_section_models(model_config_steps)
    s += get_section_numpy_hack(proj)
    s += get_section_controller_timeout_patch()
    s += '%runscript\n'
    s += get_section_run_script(spec_name)

    print(s)
    defs_dir = os.path.join(optics_home, 'apptainer', 'defs')
    os.makedirs(defs_dir, exist_ok=True)
    def_fname = optics_spec_fname.split('.')[0] + '.def'
    def_path = os.path.join(defs_dir, def_fname)
    f = open(def_path, 'w')
    f.write(s)
    f.close()

