# session status 
NO_MORE_SCENES_TO_RUN = 'NO_MORE_SCENES_TO_RUN'
SESSION_KILLED = 'SESSION_KILLED'

# test conversation between tman and trun
JOB_REQUEST       = 'TRUN_JOB_REQUEST'
JOB_REQUEST_SMOKE = 'TRUN_JOB_REQUEST_SMOKE'
JOB_ASSIGN        = 'TMAN_JOB_ASSIGN'

TEST_SET_ORDER = 'test_set_order'
SMOKE_TEST  = 'smoke_test'

MCS_CONTROLLER           = 'mcs'       # NOTE - must be in sync with opics.common.launch.Eval6Agent
REPLAY_CONTROLLER        = 'replay'    # NOTE - must be in sync with opics.common.launch.Eval6Agent

TEST_HISTORY_FIRST_LINE_PREFIX = '# test history for scene: '


EC2_MACHINE_HOME = '/home/ubuntu'
#EC2B_UNAME_OUTPUT = 'ip-172-31-72-254'
EC2B_UNAME_OUTPUT = 'ip-172-31-12-56'
EC2A_UNAME_OUTPUT = 'ip-172-31-32-89'

EC2A_IP_ADDRESS = '3.208.150.109'
#EC2B_IP_ADDRESS = '3.221.218.227'
EC2B_IP_ADDRESS = '3.20.113.119'

EC2A_URL = f'ubuntu@{EC2A_IP_ADDRESS}'
EC2B_URL = f'ubuntu@{EC2B_IP_ADDRESS}'