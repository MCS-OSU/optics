# session status 
NO_MORE_SCENES_TO_RUN = 'NO_MORE_SCENES_TO_RUN'
SESSION_KILLED = 'SESSION_KILLED'

# test conversation between tman and trun
JOB_REQUEST       = 'TRUN_JOB_REQUEST'
JOB_REQUEST_SMOKE = 'TRUN_JOB_REQUEST_SMOKE'
JOB_ASSIGN        = 'TMAN_JOB_ASSIGN'

TEST_SET_ORDER = 'test_set_order'
SMOKE_TEST  = 'smoke_test'

TEST_HISTORY_FIRST_LINE_PREFIX = '# test history for scene: '

EC2_MACHINE_HOME = '/home/ubuntu'
EC2D_UNAME_OUTPUT = '172-31-10-162'
EC2C_UNAME_OUTPUT = 'ip-172-31-72-254'
EC2B_UNAME_OUTPUT = 'ip-172-31-12-56'
EC2A_UNAME_OUTPUT = 'ip-172-31-32-89'

EC2A_IP_ADDRESS = '3.208.150.109'
EC2B_IP_ADDRESS = '3.20.113.119'
EC2C_IP_ADDRESS = '3.221.218.227'
EC2D_IP_ADDRESS = '52.72.153.236'

EC2A_URL = f'ubuntu@{EC2A_IP_ADDRESS}'
EC2B_URL = f'ubuntu@{EC2B_IP_ADDRESS}'
EC2C_URL = f'ubuntu@{EC2C_IP_ADDRESS}'
EC2D_URL = f'ubuntu@{EC2D_IP_ADDRESS}'

MAX_ROOM_DIMENSION = 30


def get_alias_for_machine(machine):
    if machine == 'ip-172-31-32-89':
        return 'ec2a'
    elif machine == 'ip-172-31-12-56':
        return 'ec2b'
    elif machine == 'ip-172-31-72-254':
        return 'ec2c'
    elif machine == 'ip-172-31-10-162':
        return 'ec2d'
    else:
        return machine