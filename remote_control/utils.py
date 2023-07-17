
from pathlib import Path
import os
import configparser

from core.utils import optics_fatal, get_public_key_path
from core.constants import legal_datastores
from core.ec2_mappings import get_url_for_ec2_machine_name #, get_uname_output_for_ec2_machine_name


def get_optics_containerstore():
    home_dir = str(Path.home())
    ini_path = os.path.join(home_dir, '.optics.ini')
    if not os.path.exists(ini_path):
        optics_fatal(f'FATAL - ~/.optics.ini not found - cannot find optics_containerstore')

    config = configparser.ConfigParser()
    config.read(ini_path)
    containerstore = config['EC2']['containerstore']
    print(f'containerstore read as {containerstore}')
    if containerstore.lower() not in legal_datastores:
        optics_fatal(f"~/.optics.ini value for containerstore must be set to one of {legal_datastores} - currently set to {containerstore}")
    return containerstore

def get_local_container_dir():
    return os.path.join(str(Path.home()),'optics_containers')

def get_remote_container_path(container_name):
    container_path = os.path.join('/home/ubuntu/containers', container_name)
    return container_path

def get_optics_containerstore_url():
    containerstore = get_optics_containerstore()
    return get_url_for_ec2_machine_name(containerstore)


def remote_get_container_quiet(remote_src, local_dest):
    remote_url = get_optics_containerstore_url()
    print(f'...fetching remote file {remote_src}')
    public_key = get_public_key_path()
    cmd = f'scp -q -i {public_key} {remote_url}:{remote_src} {local_dest} 2>/dev/null'
    os.system(cmd)


def remote_get_container(remote_src, local_dest, client_log_path):
    remote_url = get_optics_containerstore_url()
    print(f'...fetching remote file {remote_src}')
    public_key = get_public_key_path()
    cmd = f'scp -i {public_key} {remote_url}:{remote_src} {local_dest} 2>&1 | tee -a {client_log_path}'
    os.system(cmd)

def get_log_path(log_type):
    optics_home = os.environ['OPTICS_HOME']
    log_path = os.path.join(optics_home, 'remote_control', f'{log_type}.log')
    return log_path