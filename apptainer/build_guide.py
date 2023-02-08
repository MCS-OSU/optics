import sys, os
from core.optics_spec_loader import OpticsSpec
from datetime import datetime

def usage():
    print(f'usage:   python build_guide.py <optics_spec_path>')

def log_build_info(optics_spec_name, info):
    build_histories_dir = 'build_histories'
    build_history_path = os.path.join(build_histories_dir, 'hist_' + optics_spec_name + '.txt')
    f = open(build_history_path, 'a')
    timestamp = str(datetime.now()).split('.')[0]
    f.write(timestamp + '  ' + info + '\n')
    f.close()


def rebuild_base_container(optics_spec_name, base_name):
    print('=======================================================================================')
    print(f'                REBUILDING BASE CONTAINER {base_name}.sif')
    print('=======================================================================================')
    sif_path = f'sifs/{base_name}.sif'
    log_build_info(optics_spec_name, f'{sif_path} - deleting prior')
    os.system(f'rm {sif_path}')
    log_build_info(optics_spec_name, f'{sif_path} - build begin')
    os.system(f'apptainer build {sif_path} defs/{base_name}.def 2>&1 | tee build_log_container_{base_name}.txt')
    if os.path.exists(sif_path):
        log_build_info(optics_spec_name, f'{sif_path} - build complete')

def regen_final_container_def_file(optics_spec_path, base_container_path):
    optics_spec_name = os.path.basename(optics_spec_path).split('.')[0]
    print('=======================================================================================')
    print(f'                REGENRATING FINAL CONTAINER DEF defs/{optics_spec_name}.def')
    print('=======================================================================================')
    os.system(f'python gen_apptainer_def.py {optics_spec_path} {base_container_path} ')
    log_build_info(optics_spec_name, f'{optics_spec_name}.def - regenerated')

def rebuild_outer_container(optics_spec_name):
    print('=======================================================================================')
    print(f'                REBUILDIUNG FINAL CONTAINER DEF defs/{optics_spec_name}.def')
    print('=======================================================================================')
    sif_path = f'sifs/{optics_spec_name}.sif'
    log_build_info(optics_spec_name, f'{sif_path} - deleting prior')
    os.system(f'rm {sif_path}')
    log_build_info(optics_spec_name, f'{sif_path} - build begin')
    os.system(f'apptainer build {sif_path} defs/{optics_spec_name}.def 2>&1 | tee build_log_container_{optics_spec_name}.txt')
    if os.path.exists(sif_path):
        log_build_info(optics_spec_name, f'{sif_path} - build complete')


def collect_comment_for_log(optics_spec_name):
    print("WHy this rebuild? (comment will be added to log)")
    comment = input('')
    log_build_info(optics_spec_name, comment)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit()

    optics_spec_path   = sys.argv[1]
    if not os.path.exists(optics_spec_path):
        print(f'given spec path does not exist {optics_spec_path}')
        sys.exit()

    base_name = 'ubuntu_python'
    cur_dir = os.getcwd()
    base_container_path = f'{cur_dir}/sifs/{base_name}.sif'
    optics_spec_fname = os.path.basename(optics_spec_path)
    optics_spec_name = optics_spec_fname.split('.')[0]
    optics_spec = OpticsSpec(optics_spec_path)
    repo_name   = optics_spec.apptainer_repo_to_clone
    branch      = optics_spec.apptainer_branch_to_pull
    s = 'What is the lowest-number piece that has been changed to motivate this build?:\n'
    s += f'1. {base_name}.def    (the base container def file)\n'
    s += '2. gen_apptainer_def.py (the script the builds the def for the full container as per the optics spec)\n'
    s += f'3. {optics_spec_fname}\n'
    s += '4. an optics code change\n'
    s += f'5. a code change for repo {repo_name} branch {branch}\n'
    print(s)
    answer = input(':')
    if answer == '1':
        print('here is the plan:')
        print(f'    - rebuild sifs/{base_name}.sif  (takes a while)')
        print('    - run gen_apptainer_def.py using optics_spec values (instantaneous)')
        print(f'    - rebuild sifs/{optics_spec_name}.sif (takes a while)')
        print('')
        ans = input('is this correct? y/n\n')
        if ans == 'n':
            sys.exit()
        collect_comment_for_log(optics_spec_name)
        rebuild_base_container(optics_spec_name, base_name)
        regen_final_container_def_file(optics_spec_path, base_container_path)
        rebuild_outer_container(optics_spec_name)

    elif answer == '2' or answer == '3':
        print('here is the plan:')
        print('    - run gen_apptainer_def.py using optics_spec values (instantaneous)')
        print(f'    - rebuild sifs/{optics_spec_name}.sif  (takes a while)')
        print('')
        ans = input('is this correct? y/n\n')
        if ans == 'n':
            sys.exit()
        collect_comment_for_log(optics_spec_name)
        regen_final_container_def_file(optics_spec_path, base_container_path)
        rebuild_outer_container(optics_spec_name)

    elif answer == '4' or answer == '5':
        print('here is the plan:')
        print(f'   - rebuild sifs/{optics_spec_name}.sif   (takes a while)')
        print('')
        ans = input('is this correct? y/n\n')
        if ans == 'n':
            sys.exit()
        collect_comment_for_log(optics_spec_name)
        rebuild_outer_container(optics_spec_name)



