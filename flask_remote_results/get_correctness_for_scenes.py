import sys, os
import json
from opics_common.opics_logging.stdout_logs import StdoutLogs
from opics_common.results.avoe_pairs import AvoePairs

optics_data_root = '/home/ubuntu/eval6_systest'

def get_correctness_string_from_inter_log(lines):
    for line in lines:
        if '; RESULT ; error ;' in line:
            return 'exception'
        if '; RESULT ; False ;' in line:
            return 'incorrect'
        if '; RESULT ; True ;' in line:
            return 'correct'
    return 'unknown'


def get_correctness_string_from_pvoe_log(lines):
    for line in lines:
        if '; RESULT ;' in line:
            if '_implaus_' in line and ' implausible ' in line:
                return 'correct'
            elif '_plaus_' in line and ' plausible ' in line:
                return 'correct'
            else:
                return 'incorrect'
    return 'unknown'

def get_correctness_string(proj, run, scene_type, scene_name):
    versions_root = os.path.join(optics_data_root, proj, 'versions')
    scene_log_dir = os.path.join(versions_root, run, 'logs', scene_type)
    files = os.listdir(scene_log_dir)
    files.sort()
    most_recent_log = ''
    for log_file in files:
        if log_file.startswith(scene_name):
            most_recent_log = log_file
    if '' == most_recent_log:
        return 'unknown'
    scene_log_path = os.path.join(scene_log_dir, most_recent_log)
    f = open(scene_log_path, 'r')
    lines = f.readlines()

    f.close()
    if proj == 'inter':
        return get_correctness_string_from_inter_log(lines)
    elif proj == 'pvoe':
        return get_correctness_string_from_pvoe_log(lines)
    else:
        return 'unknown'
    

def get_stdout_logs_instance(proj, run, scene_type):
    stdout_logs = StdoutLogs()
    versions_root = os.path.join(optics_data_root, proj, 'versions')
    stdout_log_dir = os.path.join(versions_root, run, 'stdout_logs')
    type_dir = os.path.join(stdout_log_dir, scene_type)
    if os.path.exists(type_dir):
        files = os.listdir(type_dir)
        #print(type_dir)
        for file in files:
            filepath = os.path.join(type_dir, file)
            #print(f'log file {filepath}')
            if os.path.isfile(filepath):
                # print(f'file:  {filepath}')
                stdout_logs.load_file(filepath, proj, scene_type)
    return stdout_logs

def get_avoe_pair_for_scene_name(pairs, scene_name):
    for pair in pairs:
        if pair.log_01.scene_name in scene_name or pair.log_02.scene_name in scene_name:
            return pair 
    return None

def get_correctness(proj, run, scene_type):
    result = {}
    versions_root = os.path.join(optics_data_root, proj, 'versions')
    log_dir = os.path.join(versions_root, run, 'logs')
    if not os.path.exists(log_dir):
        return {}
    type_dir = os.path.join(log_dir, scene_type)
    log_names = os.listdir(type_dir)
    result['scene_names'] = []
    result['correctness'] = {}
    for log_name in log_names:
        if proj == 'avoe':
            scene_name = log_name.split('__')[0]
        else:
            scene_name = log_name.replace('.log','')
        result['scene_names'].append(scene_name)
    if proj == 'pvoe' or proj == 'inter':
        for log_name in log_names:
            scene_name = log_name.replace('.log','')
            result['correctness'][scene_name] = get_correctness_string(proj, run, scene_type, scene_name)
    if proj == 'avoe':
        # avoe is scored in a pairwise way
        stdout_logs = get_stdout_logs_instance(proj, run, scene_type)
        avoe_pairs = AvoePairs(stdout_logs)
        if not scene_type in avoe_pairs.pairs_for_type:
            result['correctness'][scene_name] = 'unknown'
        else:
            pairs_for_type = avoe_pairs.pairs_for_type[scene_type]
            for scene_name in result['scene_names']:
                avoe_pair = get_avoe_pair_for_scene_name(pairs_for_type, scene_name)
                if avoe_pair is None:
                    result['correctness'][scene_name] = 'unknown'
                elif avoe_pair.is_osu_agent_correct():
                    result['correctness'][scene_name] = 'correct'
                else:
                    result['correctness'][scene_name] = 'incorrect'
    return result

if __name__ == '__main__':
    if not len(sys.argv) == 4:
        print('Usage:  python get_correctness_for_scenes <proj> <run_name> <scene_type>')
        sys.exit()
    proj = sys.argv[1]
    run_name = sys.argv[2]
    scene_type = sys.argv[3]
    result_object = get_correctness(proj, run_name, scene_type)
    s = json.dumps(result_object, indent=2)
    print(s)
    