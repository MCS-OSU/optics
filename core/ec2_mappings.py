
import os
from core.constants import EC2A_UNAME_OUTPUT, EC2C_UNAME_OUTPUT, EC2D_UNAME_OUTPUT
from core.constants import EC2A_URL, EC2C_URL, EC2D_URL


url_for_ec2_machine_name = {}
url_for_ec2_machine_name['ec2a'] = EC2A_URL
url_for_ec2_machine_name['ec2c'] = EC2C_URL
url_for_ec2_machine_name['ec2d'] = EC2D_URL

def get_url_for_ec2_machine_name(machine_name):
    if machine_name in url_for_ec2_machine_name:
        return url_for_ec2_machine_name[machine_name]
    else:
        raise Exception(f'ERROR:  machine name {machine_name} not recognized in get_url_for_ec2_machine_name()')

uname_output_for_ec2_machine_name = {}
uname_output_for_ec2_machine_name['ec2a'] = EC2A_UNAME_OUTPUT
uname_output_for_ec2_machine_name['ec2c'] = EC2C_UNAME_OUTPUT
uname_output_for_ec2_machine_name['ec2d'] = EC2D_UNAME_OUTPUT


def get_uname_output_for_ec2_machine_name(machine_name):
    if machine_name in uname_output_for_ec2_machine_name:
        return uname_output_for_ec2_machine_name[machine_name]
    else:
        raise Exception(f'ERROR:  machine name {machine_name} not recognized in get_uname_output_for_ec2_machine_name()')

ec2_machine_name_for_uname_output = {}
ec2_machine_name_for_uname_output[EC2A_UNAME_OUTPUT] = 'ec2a'
ec2_machine_name_for_uname_output[EC2C_UNAME_OUTPUT] = 'ec2c'
ec2_machine_name_for_uname_output[EC2D_UNAME_OUTPUT] = 'ec2d'

def get_ec2_machine_name_for_uname_output(uname_output):
    if uname_output in ec2_machine_name_for_uname_output:
        return ec2_machine_name_for_uname_output[uname_output]
    else:
        return uname_output

def is_running_on_ec2_machine():
    uname_output = os.uname()[1]
    return uname_output in ec2_machine_name_for_uname_output
