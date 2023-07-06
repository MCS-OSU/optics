OPTICS_DATA_ROOT_DIR = '/home/ubuntu/eval6_systest'

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

MAX_ROOM_DIMENSION = 30

EC2_MACHINE_HOME = '/home/ubuntu'
EC2D_UNAME_OUTPUT = '172-31-10-162'
EC2C_UNAME_OUTPUT = 'ip-172-31-72-254'
EC2A_UNAME_OUTPUT = 'ip-172-31-32-89'

EC2A_IP_ADDRESS = '3.208.150.109'
EC2C_IP_ADDRESS = '3.221.218.227'
EC2D_IP_ADDRESS = '52.72.153.236'

EC2A_URL = f'ubuntu@{EC2A_IP_ADDRESS}'
EC2C_URL = f'ubuntu@{EC2C_IP_ADDRESS}'
EC2D_URL = f'ubuntu@{EC2D_IP_ADDRESS}'


legal_datastores = ['ec2a','ec2c', 'ec2d']
active_ec2_machines = ['ec2a','ec2c', 'ec2d']
