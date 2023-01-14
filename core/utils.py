import os
import time
import configparser
import logging
import sys

ec2b_url = 'ubuntu@3.221.218.227'
remote_url = ec2b_url

def get_public_key_path():
    if not 'OPICS_HOME' in os.environ:
        optics_fatal('OPICS_HOME not defined - please set it to the root of the opics repo pull')
    opics_home = os.environ['OPICS_HOME']
    return opics_home + '/scripts/ec2/shared-with-opics.pem'

def remote_copy_file(src, dest):
    remote_dir = os.path.dirname(dest)
    remote_ensure_dir_exists(remote_dir)
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key} {src} {remote_url}:{dest}'
    optics_debug(f'running command {cmd}')
    os.system(cmd)

def remote_get_file(remote_src, local_dest):
    optics_info(f'...fetching remote file {remote_src}')
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key} {remote_url}:{remote_src} {local_dest}'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)

def remote_run_os_command_and_return_results(run_dir, cmd, output_path):
    optics_info(f'...running remote command: {cmd}...')
    optics_info(f'...in this run_dir {run_dir}...')
    public_key = get_public_key_path()
    cmd = f'ssh -i {public_key} {remote_url} "export PYTHONPATH=~/eval6;export OPICS_HOME=~/eval6;cd {run_dir};{cmd} > {output_path}"'
    optics_debug(f'funning command: {cmd}')
    os.system(cmd)
    cmd = f'scp -i {public_key} {remote_url}:{run_dir}/{output_path} .'
    optics_debug(f'funning command: {cmd}')
    os.system(cmd)
    cmd = f'ssh -i {public_key} {remote_url} "rm {run_dir}/{output_path}"'
    optics_debug(f'funning command: {cmd}')
    os.system(cmd)
    return output_path

def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    
def ensure_dirs_exist(dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
def remote_ensure_dir_exists(dir):
    public_key = get_public_key_path()
    cmd = f'ssh -i {public_key} {remote_url} "mkdir -p {dir}"'
    optics_debug(f'funning command: {cmd}')
    os.system(cmd)

def remote_ensure_dirs_exist(dirs):
    for d in dirs:
        remote_ensure_dir_exists(d)

def get_last_line(path):
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    last_line = lines[-1].rstrip()
    optics_debug(f'last line found as : {last_line}')
    return last_line
    
def get_first_line(path):
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    first_line = lines[0].rstrip()
    optics_debug(f'first line found as : {first_line}')
    return first_line

def add_last_line(path, s):
    optics_debug(f'adding last line {s}')
    f = open(path, 'a')
    if not s.endswith('\n'):
        s += '\n'
    f.write(s)
    f.close()

def read_file(path):
    f = open(path, 'r')
    lines = f.read()
    f.close()
    return lines

def remote_get_last_line(path):
    # fetch the file from the remote machine
    fname = os.path.basename(path)
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key}  {remote_url}:{path} .'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()
    result = lines[-1].rstrip()
    optics_debug(f'remote_last_line found as : {result}')
    optics_debug(f'removing file {fname}')
    os.remove(fname)
    return result

def remote_add_last_line(path, s):
    optics_debug(f'adding last line {s} to remote {path}')
    fname = os.path.basename(path)
    #...pulling remote file ...
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key}  {remote_url}:{path} .'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)
    #...adding line ...
    f = open(fname, 'a')
    f.write(s + '\n')
    f.close()
    #...pushing file back...
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key}  {fname} {remote_url}:{path}'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)
    optics_debug(f'removing file {fname}')
    os.remove(fname)


def parse_job_assign(job_assign):
    fields = job_assign.split(';')
    machine = fields[1]
    command = fields[2]
    scene_path = fields[3]
    optics_info(f'...parsed job_assign as: {machine}, {command}, {scene_path}')
    return machine, command, scene_path

def parse_job_request(job_request):
    fields = job_request.split(';')
    machine = fields[1]
    command = fields[2]
    optics_info(f'...parsed job_request as: {machine}, {command}')
    return machine, command

def parse_run_state(s):
    fields = s.split(';')
    optics_debug(f'parsed run state as {fields[2]}')
    return fields[2]

def get_session_message(run_state):
    t = int(time.time())
    machine = os.uname()[1]
    return f'{t};{machine};{run_state}'

def get_register_status_message(status):
    t = int(time.time())
    machine = os.uname()[1]
    return f'{t};{machine};{status}'

def get_register_control_message(control, control_arg):
    t = int(time.time())
    machine = os.uname()[1]
    return f'{t};{machine};{control};{control_arg}'

def is_test_running_on_ec2b():
    return os.path.exists('/home/ubuntu/.opics_systest_manager_home')

def convert_time_field_to_delta(s):
    optics_debug('converting time field to delta')
    fields = s.split(';')
    time_index = '?'
    for i in range(len(fields)):
        if fields[i].startswith('16631'):
            time_index = i
            break
    if time_index == '?':
        optics_error(f'could not determine time index - 16631 not present in {s}')
        optics_error('bailing out by returning "?"')
        return s    
    else:
        secs_since_epoch = fields[time_index]
        optics_debug(f'secs_since_epoch found as {secs_since_epoch}')
        time_delta = int(float(time.time()) - float(secs_since_epoch))
        optics_debug(f'time_delta computed as {time_delta)')
        fields[time_index] = ' as of ' + str(time_delta) + ' sec ago'
    return ';'.join(fields)

def get_time_between_final_two_entries(path):
    optics_debug(f'get time between final two entries of {path}')
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    if len(lines) < 2:
        optics_debug('less than two lines - NA')
        return 'not enough lines'
    else:
        t2 = lines[-1].split(';')[0]
        optics_debug(f't2 found as : {t2}')
        t1 = lines[-2].split(';')[0]
        optics_debug(f't1 found as : {t1}')
        if is_time(t1) and is_time(t2):
            result = int(t2) - int(t1)
            optics_debug(f'delta determined as {result}')
            return result
        optics_debug('one of the times is not a time, return empty string')
        return ''
    
def get_scene_type_for_state_path(state_path):
    fname = os.path.basename(state_path)
    return fname.split('_')[0]

def get_state_path_for_scene_path(scene_path, scene_state_dir):
    scene_name = os.path.basename(scene_path).split('.')[0]
    scene_type = scene_name.split('_')[0]
    state_path = os.path.join(scene_state_dir, scene_type, scene_name + '_state.txt')
    return state_path

def is_time(s):
    if s.startswith('166') and len(s) == 10 and s.isdigit():
        return True
    return False

def header(s):
    h = '\n------------------------------------------------\n'
    h += '         ' + s + '\n'
    h += '------------------------------------------------'
    return h

def get_scene_type_from_scene_name(scene_name):
    parts = scene_name.split('_')
    return parts[0]


def email_mcs_optics_status(s):
    email = 'jedirv@gmail.com'
    os.system(f'echo "{s}" | mail -s "MCS Optics Status" {email}')


def notify_mcs_optics_status(s):
    notify('mcs_optics_status_osu', s)

def notify(topics, s):
    os.system(f'curl -d  {s} ntfy.sh/{topics}')

def filter_pathnames_for_smoke_test(paths):
    scene_types = set()
    smoke_test_paths = []
    for path in paths:
        scene_types.add(get_scene_type_from_scene_name(os.path.basename(path)))
    for scene_type in scene_types:
        smoke_test_paths.append(get_first_for_type(paths, scene_type))
    return smoke_test_paths

def get_first_for_type(paths, scene_type):
    for path in paths:
        cur_scene_type = get_scene_type_from_scene_name(os.path.basename(path))
        if scene_type == cur_scene_type:
            return path
    print(f'[optics] WARNING - no scene of type {scene_type} found in get_first_for_type')
    return None

def clean_video_fname(fname):
    fname = fname.replace('_level2__','')
    fname = remove_datestamp(fname)
    return fname

def get_video_of_type(videos_dirname, video_id):
    files = os.listdir(videos_dirname)
    for file in files:
        if file.endswith('.mp4'):
            if video_id in file:
                return file
    return "not_found"

def remove_datestamp(fname):
    suffix = fname.split('.')[1]
    date_index = fname.index('_202')
    dateless_fname = fname[:date_index]
    return dateless_fname + '.' + suffix


def get_pathnames_for_video(videos_dir, scene_type, target_dir, video_id):
    src_fname  = get_video_of_type(videos_dir, video_id)
    dest_fname = clean_video_fname(src_fname)
    src_path   = os.path.join(videos_dir, src_fname)
    dest_path  = os.path.join(target_dir, scene_type, dest_fname)
    optics_info(f'video local path {src_path} ; video target path {dest_path}')
    return (src_path, dest_path)


def get_level_from_config_ini(config_ini_path):
    config_ini = configparser.ConfigParser()
    config_ini.read(config_ini_path)
    level = config_ini['MCS']['metadata']
    optics_debug(f'metadata level from {config_ini_path} is {level}')
    return level


def get_config_ini_path(cfg_dir):
    optics_info(f'cwd: {os.getcwd()}')
    optics_info("cfg_dir: ", cfg_dir)
    ini_path = os.path.join(cfg_dir, "mcs_config.ini")
    optics_info("ini_path: ", ini_path)
    if not os.path.exists(ini_path):
        raise FileNotFoundError("mcs_config.ini missing from cfg dir")
    return ini_path


def get_scene_name_from_path(scene_path):
    fname = os.path.basename(scene_path)
    scene_name = fname.split('.')[0]
    return scene_name


def optics_info(m):
    om = f'[optics]...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.info(om)

def optics_error(m):
    om = f'[optics]...ERROR!...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.info(om)

def optics_debug(m):
    logger = logging.getLogger()
    logger.debug(m)

def optics_warning(m):
    om = f'[optics]...WARNING...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.warning(om)

def optics_fatal(m):
    om = f'[optics]...FATAL ERROR...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.criical(om)
    sys.exit()

# def exit_with(msg):
#     print(msg)
    
