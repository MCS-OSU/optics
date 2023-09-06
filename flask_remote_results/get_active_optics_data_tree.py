import json
import os

optics_data_root = '/home/ubuntu/eval6_systest'


def get_runs_with_data_for_proj(proj):
    runs_with_data = {}
    versions_root = os.path.join(optics_data_root, proj, 'versions')
    all_runs = os.listdir(versions_root)
    for run_name in all_runs:
        stdout_dir = os.path.join(versions_root, run_name, 'stdout_logs')
        if os.path.exists(stdout_dir):
            #print(f'scanning stdout_dir {stdout_dir}')
            type_names = os.listdir(stdout_dir)
            for type_name in type_names:
                type_dir = os.path.join(stdout_dir, type_name,)
                #print(f'scanning type_dir {type_dir}')
                stdout_log_names = os.listdir(type_dir)
                for stdout_log_name in stdout_log_names:
                    if not run_name in runs_with_data:
                        runs_with_data[run_name] = {}
                    if not type_name in runs_with_data[run_name]:
                        runs_with_data[run_name][type_name] = {}
                        runs_with_data[run_name][type_name]['scene_names'] = []
                    scene_name = stdout_log_name.replace('_stdout.txt','')
                    runs_with_data[run_name][type_name]['scene_names'].append(scene_name)
    return runs_with_data
            


if __name__ == '__main__':
    projects = ['avoe','inter','pvoe']
    result = {}
    result['projects'] = {}
    for proj in projects:
        result['projects'][proj] = get_runs_with_data_for_proj(proj)
    s = json.dumps(result, indent=2)
    print(s)