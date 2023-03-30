
import sys, os

def ensure_target_dir(target_dir):
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    else:
        print(f'WARNING: target_dir already exists: {target_dir}')
        answer = input('(r)replace, (a)abort? ')
        if answer == 'r':
            print('removing target_dir')
            os.system(f'rm -rf {target_dir}')
            os.makedirs(target_dir)
        elif answer == 'a':
            print('aborting')
            sys.exit()
        else:
            print('invalid answer, aborting')
            sys.exit()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage:  python archive_results.py <target_dir>')
        sys.exit()
    doc_lines = []
    target_dir = sys.argv[1]
    ensure_target_dir(target_dir)
    optics_data_dir = '/home/ubuntu/eval6_systest'
    projects = ['avoe', 'inter', 'pvoe']
    for proj in projects:
        proj_target_dir = os.path.join(target_dir, proj)
        os.makedirs(proj_target_dir, exist_ok=True)

        proj_data_dir = os.path.join(optics_data_dir, proj)
        os.chdir(proj_data_dir)
        # if proj == 'avoe':
        #     doc_lines.append('# for AVOE, the eval5 scenes are too huge for a versatile archive process, so we omit them')
        #     doc_lines.append('# they exist in renamed form on Jed\'s vm and also in the AVOE box folder')
        #     cmd = f'zip -rq {proj_target_dir}/scenes_and_test_sets.zip  scenes test_sets -x scenes/eval5/**\*'
        # else:
        cmd = f'zip -rq {proj_target_dir}/scenes_and_test_sets.zip  scenes test_sets'
        print(f'running cmd: {cmd}')
        os.system(cmd)
        versions_dir = os.path.join(proj_data_dir, 'versions')
        version_dirs = os.listdir(versions_dir)
        for version_dir in version_dirs:
            cmd = f'zip -rq {proj_target_dir}/version_{version_dir}.zip versions/{version_dir} -x versions/{version_dir}/videos/**\*'
            print(f'running cmd: {cmd}', flush=True)
            os.system(cmd)
            

# ubuntu@ip-172-31-12-56:~/eval6_systest/inter/versions$ ls -1
# 021423_pranay_movtarg
# 021523_pranay_movtarg
# 021923_rajesh_mapping_v3
# 030623_val6
# 030723_5w_6new
# 030823_sltk
# 031323_val6
# 031923_5unweighted
# 031923_5w_6new
# 031923_ramps
# 031923_tools
# 031923_val6
# 032123_tools
# diego_mapping_merge_122322
# diego_mapping_merge_container
# rajesh_mapping_v2_020523
# v5_final
# v6_mapping_1



# zip -r version_032123_tools.zip versions/032123_tools -x versions/032123_tools/videos/**\*