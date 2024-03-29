
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
        s += f'    export PYTHONPATH=$OPTICS_HOME:$OPTICS_HOME/opics_common:$OPTICS_HOME/opics\n'
    else:
        s += f'    export OPICS_HOME=$OPTICS_HOME/opics_{proj}\n'
        s += f'    export PYTHONPATH=$OPTICS_HOME:$OPTICS_HOME/opics_common\n'
    if proj == "inter":
        s += f'    export PYTHONPATH=$PYTHONPATH:$OPTICS_HOME/opics_inter/opics_inter/inter/planner/pddl/pddlstream/\n'
    s += f'    export PATH=/miniconda3/bin:$PATH\n'
    s += f'    export REPLAY_HOME=$OPICS_HOME/replay_scenes\n'
    s += '\n'
    s += '\n'
    return s

def get_section_position_run_script(spec_name):
    s =  f'    cp /tmp/run_{spec_name}.sh /\n'
    s += f'    chmod 775 /run_{spec_name}.sh\n\n'
    return s

def get_dirname_for_project(proj):
    if proj == 'avoe':
        return 'opics'
    else:
        return f'opics_{proj}'

def get_section_opics_project_code(optics_branch, proj, project_branch,  pull_time_root_name):
    s =  '    ############################################################################\n'
    s += '    # add private key for github auth\n'
    s += '    ############################################################################\n'
    s += '    eval "$(ssh-agent -s)"\n'
    s += '    mkdir /root/.ssh\n'
    s += '    cp /tmp/config /root/.ssh\n'
    s += '    cp /tmp/id_ed25529_031623  /root/.ssh\n'
    s += '    ssh-add /root/.ssh/id_ed25529_031623\n'
    s += '    cd /\n'
    s += f'   git clone git@github.com:MCS-OSU/optics.git {pull_time_root_name}\n'
    s += '    ############################################################################\n'
    s += '    # put the correct branches into play\n'
    s += '    ############################################################################\n'
    s += f'    cd {pull_time_root_name}\n'
    s += f'    git checkout {optics_branch}\n'
    s += '    ############################################################################\n'
    s += '    # copy the ssh version of .gitmodules into place to bypass authentication\n'
    s += '    ############################################################################\n'
    s += f'    cp ssh_urls_for_git_modules.txt .gitmodules\n'
    s += '    ############################################################################\n'
    s += '    # credential helper for good measure - may be unnecessary with ssh in play\n'
    s += '    ############################################################################\n'
    s += f'    git config --global user.name jedirv\n'
    s += f'    git config --global credential.helper store\n'
    s += f'    git submodule update --init --recursive\n'
    # git the correct branch for the project
    dirname_for_proj = get_dirname_for_project(proj)
    proj_pull_dir = os.path.join(pull_time_root_name, dirname_for_proj)
    s += f'    cd /{proj_pull_dir}\n'
    s += f'    git checkout {project_branch}\n'
    s += f'    if [ -d /{proj_pull_dir}/opics_inter/inter/planner/pddl/pddlstream ]; then \n'
    s += f'        echo " - "\n'
    s += f'        echo "NOTE - DETECTED PDDL SUBMODULE REFERENCE - attempting to pull that in..."\n'
    s += f'        echo " - "\n'
    s += f'        cd /{proj_pull_dir}\n'
    s += f'        git submodule update --init --recursive\n'
    s += f'        if [ -f /{proj_pull_dir}/opics_inter/inter/planner/pddl/pddlstream/downward/build.py ]; then \n'
    s += f'            echo " - "\n'
    s += f'            echo "NOTE - SUCCESSFULLY PULLED IN DOWNWARD... attempting downward build..."\n'
    s += f'            echo " - "\n'
    s += f'            gcc --version\n'
    s += f'            apt update\n'
    s += f'            apt -y install cmake\n'
    s += f'            cd /{proj_pull_dir}/opics_inter/inter/planner/pddl/pddlstream\n'
    s += f'            ./downward/build.py\n'
    s += f'        else\n'
    s += f'            echo " - "\n'
    s += f'            echo "NOTE - FAILED TO PULL IN DOWNWARD"\n'
    s += f'            echo " - "\n'
    s += f'        fi\n'
    s += f'    else\n'
    s += f'        echo " - "\n'
    s += f'        echo "NOTE - DID NOT DETECT PDDLSTREAM SUBMODULE REFERENCE"\n'
    s += f'        echo " - "\n'
    s += f'    fi\n'
    # checkout opics_common  main
    opics_common_pull_dir = os.path.join(pull_time_root_name, 'opics_common')
    s += f'    cd /{opics_common_pull_dir}\n'
    s += f'    git checkout main\n'

    s += '\n'
    s += '\n'
    return s


def get_section_scene_gen_code(spec_name):
    s =  '    ############################################################################\n'
    s += '    # add scene_gen repo into play\n'
    s += '    ############################################################################\n'
    s += '    cd /\n'
    s += f'    git clone https://github.com/MCS-OSU/scene-gen.git scene-gen__{spec_name}\n'
    s += f'    cd scene-gen__{spec_name}\n'
    s += '    git checkout main\n'
    s += '    ./install.sh\n'
    s += '\n'
    s += '\n'
    return s


def get_section_opics_dependencies(proj, pull_time_root_name, lib_config_steps):
    s =  '    ############################################################################\n'
    s += '    # install python dependencies\n'
    s += '    ############################################################################\n'
    s += f'    export OPTICS_HOME=/{pull_time_root_name}\n'
    if proj == 'avoe':
        s += f'    export OPICS_HOME=/{pull_time_root_name}/opics\n'
    s += '    echo "==============  python dependencies  ==================="\n'
    dirname_for_proj = get_dirname_for_project(proj)
    print(f'....dirname for project will be {dirname_for_proj}')
    proj_pull_dir = os.path.join(pull_time_root_name, dirname_for_proj)
    s += f'    cd /{proj_pull_dir}\n'
    for step in lib_config_steps:
        s += f'    {step}\n'
    s += '\n'
    s += '\n'
    return s


def get_section_models(model_config_steps, proj):
    s =  '    ############################################################################\n'
    s += '    # position models\n'
    s += '    ############################################################################\n'
    s += '    echo "==============  loading models ==================="\n'
    for step in model_config_steps:
        s += f'    {step}\n'

    # once models are in place, change all dir permissions so that image can be successfully copied on dgx run
    s += f'    cd /\n'
    s += f'    echo "contents of slash is : "\n'
    s += f'    ls\n'
    s += f'    ls -la /{pull_time_root_name}\n'
    if proj == 'pvoe':
        s += f'    ls -la /{pull_time_root_name}/opics_pvoe\n'
        s += f'    ls -la /{pull_time_root_name}/opics_pvoe/ckpts\n'
        s += f'    ls -la /{pull_time_root_name}/opics_pvoe/ckpts/vision\n'
        s += f'    ls -la /{pull_time_root_name}/opics_pvoe/ckpts/vision/tracker\n'
    s += f'    echo "find {pull_time_root_name} -type d -print0 | xargs -0 chmod 775"\n'
    s += f'    find {pull_time_root_name} -type d -print0 | xargs -0 chmod 775\n'
    if proj == 'pvoe':
        s += f'    ls -la /{pull_time_root_name}/opics_pvoe/ckpts/vision/tracker\n'
    s += '\n'
    s += '\n'
    return s


def get_section_numpy_hack(proj):
    if proj == 'pvoe':
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

def get_section_controller_timeout_patch(proj):
    s = '    ############################################################################\n'
    s += '    #                   --- mcs controller timeout patch ---\n'
    s += '    # changing from 3 mins to 1 hour:\n'
    s += '    ############################################################################\n'
    s += '    export PYTHONPATH=$OPTICS_HOME\n'
    s += '    cd $OPTICS_HOME/scripts\n'
    s += f'    python3 patch_mcs_controller_timeout.py {proj} 60\n'
    s += '\n'
    s += '\n'
    return s



def get_section_version_comparison(proj):
    s = '    ############################################################################\n'
    s += '    #                   --- compare versions of python dependencies ---\n'
    s += '    ############################################################################\n'
    s += '    export PYTHONPATH=$OPTICS_HOME\n'
    s += '    cd $OPTICS_HOME/scripts\n'
    s += f'   python3 compare_pip_lists.py {proj}\n'
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

    #s += f'cp -r /scene-gen__{spec_name} ~/scene_gen__{spec_name}\n'

    s += f'echo "...running  . /miniconda3/etc/profile.d/conda.sh"\n'
    s += f'. /miniconda3/etc/profile.d/conda.sh\n'
    if proj == 'avoe':
        s += f'echo "...conda activate env_{proj}"\n'
        s += f'conda activate env_{proj}\n'
    else:
        s += f'echo "...conda activate env_opics_{proj}"\n'
        s += f'conda activate env_opics_{proj}\n'
    s += f'echo "...conda activate complete"\n'
    s += f'pip list\n'

    s += f'echo "...positioning key file for OPTICS_DATASTORE ssh commands"\n'
    s += f'cd $OPTICS_HOME/scripts/ec2\n'
    s += f'wget --no-check-certificate "https://docs.google.com/uc?export=download&id=1BGff0DlqdUGEHtkCSK2FPjVcw7m5XpnY" -O shared-with-opics.pem\n'
    s += f'chmod 600 shared-with-opics.pem\n'
    s += f'echo "arg decides on optics run vs run_opics_scene"\n'
    s += f'if [[ $1 == optics ]]; then\n'
    s += f'    if [[ {proj} == "inter" ]]; then\n'
    s += f'        if [ -z "$2" ]; then\n'
    s += f'            echo ""\n'
    s += f'            echo ""\n'
    s += f'            echo "ERROR - optics for inter requires scene type handling as additional arg: scene_type_provided|scene_type_deduced"\n'
    s += f'            echo ""\n'
    s += f'            echo ""\n'
    s += f'            exit 1\n'
    s += f'        else\n'
    # see opics_common/opics_common/launch/constants.py for the following constant scene_type handling definitions
    s += f'            if [[ $2 == "scene_type_provided" ]] || [[ $2 == "scene_type_deduced" ]]; then\n'
    s += f'                export OPICS_SCENE_TYPE_HANDLING=$2\n'
    s += f'            else\n'
    s += f'                echo ""\n'
    s += f'                echo ""\n'
    s += f'                echo "ERROR - scene_type_handling must be scene_type_provided|scene_type_deduced"\n'
    s += f'                echo ""\n'
    s += f'                echo ""\n'
    s += f'                exit 1\n'
    s += f'            fi\n'
    s += f'        fi\n'
    s += f'    fi\n'
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
    s += f'        scene_name=$(echo $2 | cut -d. -f1 | rev | cut -d/ -f1 | rev)\n'
    s += f'        mkdir -p logs\n'
    s += f'        echo "...determined scene_name for log file as $scene_name"\n'
    s += f'        log_suffix="_log"\n'
    s += f'        echo "...running - python3 run_opics_scene.py --scene $2 --controller mcs --log_dir logs  2>&1 | tee -a logs/$scene_name$log_suffix.txt"\n'
    s += f'        python3 run_opics_scene.py --scene $2 --controller mcs --log_dir logs  2>&1 | tee -a logs/$scene_name$log_suffix.txt\n'
    s += f'    fi\n'
    s += f'else\n'
    s += f'    echo "command $1 not recognized"\n'
    s += f'fi\n'

    os.makedirs('run_scripts', exist_ok = True)
    run_script_path = os.path.join('run_scripts', 'run_' + spec_name + '.sh')
    f = open(run_script_path, 'w')
    f.write(s)
    f.close()
    # put it in /tmp in case need to debug it, it will be moved into / of the container as per get_section_position_run_script
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
    s += get_section_models(model_config_steps, proj)
    s += get_section_numpy_hack(proj)
    s += get_section_controller_timeout_patch(proj)
    s += get_section_version_comparison(proj)
    #s += get_section_scene_gen_code(spec_name)
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

