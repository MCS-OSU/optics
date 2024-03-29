import os
import time
import configparser
import logging
import sys
import inspect
from pathlib import Path
from core.constants  import EC2A_UNAME_OUTPUT, EC2C_UNAME_OUTPUT, EC2D_UNAME_OUTPUT,EC2A_URL, EC2C_URL, EC2D_URL
from core.constants import legal_datastores
from core.ec2_mappings import get_url_for_ec2_machine_name, get_uname_output_for_ec2_machine_name


def get_optics_datastore_from_env():
    if not 'OPTICS_DATASTORE' in os.environ:
        optics_fatal(f"env variable OPTICS_DATASTORE not defined - please set it to one of {legal_datastores} or position ~/.optics.ini with valid 'datastore' setting")
    if os.environ['OPTICS_DATASTORE'].lower() not in legal_datastores:
        optics_fatal(f"env variable OPTICS_DATASTORE must be set to one of {legal_datastores} or position ~/.optics.ini with valid 'datastore' setting")
    return os.environ['OPTICS_DATASTORE']

def get_optics_datastore():
    home_dir = str(Path.home())
    ini_path = os.path.join(home_dir, '.optics.ini')
    if not os.path.exists(ini_path):
        print(f'WARNING - ~/.optics.ini not found - will attempt to use OPTICS_DATASTORE env variable')
        return get_optics_datastore_from_env()

    config = configparser.ConfigParser()
    config.read(ini_path)
    datastore = config['EC2']['datastore']
    #print(f'datastore read as {datastore}')
    if datastore.lower() not in legal_datastores:
        optics_fatal(f"~/.optics.ini value for datastore must be set to one of {legal_datastores} - currently set to {datastore}")
    return datastore

def get_optics_datastore_url():
    # if this is being called, we know we are in the 'manager is remote' situation
    # so we just need to find which url correlates to the datastore
    optics_datastore = get_optics_datastore()
    return get_url_for_ec2_machine_name(optics_datastore)

def get_optics_datastore_proximity():
    if is_datastore_remote():
        return 'remote'
    else:
        return 'local'

def is_running_on_ec2a():
    uname_output = os.uname()[1]
    return uname_output == EC2A_UNAME_OUTPUT


def is_running_on_ec2c():
    uname_output = os.uname()[1]
    return uname_output == EC2C_UNAME_OUTPUT

def is_running_on_ec2d():
    uname_output = os.uname()[1]
    return uname_output == EC2D_UNAME_OUTPUT

# def is_running_on_ec2():
#     return is_running_on_ec2a() or is_running_on_ec2b()


def is_datastore_remote():
    datastore = get_optics_datastore()
    uname_output_for_datastore = get_uname_output_for_ec2_machine_name(datastore)
    uname_output_this_machine = os.uname()[1]
    return uname_output_for_datastore != uname_output_this_machine


def verify_key_file_present_if_needed():
    if not is_datastore_remote():
        return 
    key_path = get_public_key_path()
    if os.path.exists(key_path):
        return 
    raise Exception(f'key file for accessing ec2 machine is missing from {key_path}')

def get_public_key_path():
    if not 'OPTICS_HOME' in os.environ:
        optics_fatal('OPTICS_HOME not defined - please set it to the root of the optics repo pull')
    opics_home = os.environ['OPTICS_HOME']
    return opics_home + '/scripts/ec2/shared-with-opics.pem'

def remote_mv_file(remote_path, target_dir):
    remote_url = get_optics_datastore_url()
    public_key = get_public_key_path()
    cmd = f'ssh -i {public_key} {remote_url} mv {remote_path} {target_dir}'
    optics_debug(f'running command {cmd}')
    os.system(cmd)

def remote_delete_file(remote_path):
    remote_url = get_optics_datastore_url()
    public_key = get_public_key_path()
    cmd = f'ssh -i {public_key} {remote_url} rm {remote_path}'
    optics_debug(f'running command {cmd}')
    os.system(cmd)
    
def remote_copy_file(src, dest):
    fname = os.path.basename(src)
    optics_info(f'...sending {fname}...')
    remote_url = get_optics_datastore_url()
    remote_dir = os.path.dirname(dest)
    remote_ensure_dir_exists(remote_dir)
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key} {src} {remote_url}:{dest}'
    optics_debug(f'running command {cmd}')
    os.system(cmd)


def remote_copy_file_quiet(src, dest):
    remote_url = get_optics_datastore_url()
    remote_dir = os.path.dirname(dest)
    remote_ensure_dir_exists(remote_dir)
    public_key = get_public_key_path()
    cmd = f'scp -q -i {public_key} {src} {remote_url}:{dest}'
    optics_debug(f'running command {cmd}')
    os.system(cmd)

def remote_get_file(remote_src, local_dest):
    remote_url = get_optics_datastore_url()
    remote_fname = os.path.basename(remote_src)
    optics_info(f'...fetching {remote_fname}...')
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key} {remote_url}:{remote_src} {local_dest}'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)

def remote_get_file_quiet(remote_src, local_dest):
    remote_url = get_optics_datastore_url()
    optics_info(f'...fetching remote file {remote_src}')
    public_key = get_public_key_path()
    cmd = f'scp -q -i {public_key} {remote_url}:{remote_src} {local_dest} 2>/dev/null'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)

def remote_run_os_command_and_return_results(run_dir, cmd, output_path):
    remote_url = get_optics_datastore_url()
    optics_debug(f'...running remote command: {cmd}...')
    optics_debug(f'...in this run_dir {run_dir}...')
    public_key = get_public_key_path()
    cmd = f'ssh -i {public_key} {remote_url} "export PYTHONPATH=~/eval6;export OPICS_HOME=~/eval6;cd {run_dir};{cmd} > {output_path}"'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)
    cmd = f'scp -q -i {public_key} {remote_url}:{run_dir}/{output_path} .'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)
    cmd = f'ssh -q -i {public_key} {remote_url} "rm {run_dir}/{output_path}"'
    optics_debug(f'running command: {cmd}')
    os.system(cmd)
    return output_path

def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    
def ensure_dirs_exist(dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
def remote_ensure_dir_exists(dir):
    remote_url = get_optics_datastore_url()
    public_key = get_public_key_path()
    cmd = f'ssh -i {public_key} {remote_url} "mkdir -p {dir}"'
    optics_debug(f'funning command: {cmd}')
    os.system(cmd)
    print('.', end='', flush=True)

def remote_ensure_dirs_exist(dirs):
    for d in dirs:
        remote_ensure_dir_exists(d)
    print('.')

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
    remote_url = get_optics_datastore_url()
    # fetch the file from the remote machine
    fname = os.path.basename(path)
    public_key = get_public_key_path()
    cmd = f'scp -q -i {public_key}  {remote_url}:{path} .'
    optics_debug(f'running command: {cmd}')
    print('<-')
    os.system(cmd)
    f = open(fname, 'r')
    lines = f.readlines()
    f.close()
    result = lines[-1].rstrip()
    optics_debug(f'remote_last_line found as : {result}')
    optics_debug(f'removing file {fname}')
    print('.', end='', flush=True)
    os.remove(fname)
    print('.')
    return result

#Keeping this snippet for now, but it is not used
# def remote_add_last_line(path, s):
#     remote_url = get_optics_datastore_url()
#     optics_debug(f'adding last line {s} to remote {path}')
#     fname = os.path.basename(path)
#     #...pulling remote file ...
#     public_key = get_public_key_path()
#     cmd = f'scp -q -i {public_key}  {remote_url}:{path} .'
#     optics_debug(f'running command: {cmd}')
#     print('.', end='', flush=True)
#     os.system(cmd)
#     #...adding line ...
#     f = open(fname, 'a')
#     f.write(s + '\n')
#     f.close()
#     #...pushing file back...
#     public_key = get_public_key_path()
#     cmd = f'scp -q -i {public_key}  {fname} {remote_url}:{path}'
#     optics_debug(f'running command: {cmd}')
#     print('.', end='', flush=True)
#     os.system(cmd)
#     optics_debug(f'removing file {fname}')
#     print('.')
#     os.remove(fname)


def remote_add_last_line(path, s):
    remote_url = get_optics_datastore_url()
    optics_debug(f'adding last line {s} to remote {path}')
    fname = os.path.basename(path)

    # Using ssh command to echo the line into the file
    cmd = f'ssh -i {get_public_key_path()} {remote_url} "echo \'{s}\' >> {path}"'
    #print(f' running this command {cmd}')
    optics_debug(f'running command: {cmd}')
    print('->')
    os.system(cmd)




def parse_job_assign(job_assign):
    fields = job_assign.split(';')
    machine = fields[1]
    command = fields[2]
    scene_path = fields[3]
    optics_debug(f'...parsed job_assign as: {machine}, {command}, {scene_path}')
    return machine, command, scene_path

def translate_ec2_machine_name(name):
    if name == EC2A_UNAME_OUTPUT:
        return 'ec2a'
    if name == EC2C_UNAME_OUTPUT:
        return 'ec2c'
    if name == EC2D_UNAME_OUTPUT:
        return 'ec2d'
    return name 

def parse_job_request(job_request):
    fields = job_request.split(';')
    machine = fields[1]
    machine = translate_ec2_machine_name(machine)
    command = fields[2]
    optics_debug(f'...parsed job_request as: {machine}, {command}')
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
        optics_debug(f'time_delta computed as {time_delta}')
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
    optics_debug(f'video local path {src_path} ; video target path {dest_path}')
    return (src_path, dest_path)


def get_level_from_config_ini(config_ini_path):
    config_ini = configparser.ConfigParser()
    config_ini.read(config_ini_path)
    level = config_ini['MCS']['metadata']
    optics_debug(f'metadata level from {config_ini_path} is {level}')
    return level


def get_config_ini_path(cfg_dir):
    optics_debug(f'cwd: {os.getcwd()}')
    optics_debug("cfg_dir: ", cfg_dir)
    ini_path = os.path.join(cfg_dir, "mcs_config.ini")
    optics_info("ini_path: ", ini_path)
    os.system(f'cat {ini_path}')
    if not os.path.exists(ini_path):
        raise FileNotFoundError("mcs_config.ini missing from cfg dir")
    return ini_path


def get_scene_name_from_path(scene_path):
    fname = os.path.basename(scene_path)
    scene_name = fname.split('.')[0]
    return scene_name

def get_depth_prefix():
    depth = len(inspect.stack(0)) - 2
    result = ''
    for i in range(depth):
        result += '   '
    return result

def optics_info(m):
    om = f'{get_depth_prefix()}[optics]...{m}'
    #print(om)
    depth = str(len(inspect.stack(0)))
    logger = logging.getLogger()
    logger.info(om)

def optics_error(m):
    om = f'{get_depth_prefix()}[optics]...ERROR!...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.info(om)

def optics_debug(m):
    om = f'{get_depth_prefix()}[optics]...{m}'
    logger = logging.getLogger()
    logger.debug(om)

def optics_warning(m):
    om = f'{get_depth_prefix()}[optics]...WARNING...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.warning(om)

def optics_fatal(m):
    om = f'{get_depth_prefix()}[optics]...FATAL ERROR...{m}'
    #print(om)
    logger = logging.getLogger()
    logger.critical(om)
    sys.exit()

# def exit_with(msg):
#     print(msg)
    
