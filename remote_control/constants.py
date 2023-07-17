
CLIENT_POLLING_DELAY = 1.5
SERVER_POLLING_DELAY = 1.5

REMOTE_ROOT =  '/home/ubuntu/optics_remote_control'
TO_USER_REMOTE_DIR = 'messages_to_runner'
FROM_USER_REMOTE_DIR = 'messages_from_runner'

# commands
HUB_SCAN_COUNT_LIMIT = 20
PING = 'ping'
SHOW_CLIENT_LOG = 'clog'
SHOW_HUB_LOG = 'hlog'
CONTAINER_GET = 'cget'
CONTAINER_RUN_TEST = 'cruntest'
CONTAINER_STOP_TEST = 'cstoptest'
CONTAINER_RUN = 'crun'
CONTAINER_STOP = 'cstop'
CONTAINER_LIST = 'clist'
CONTAINER_DELETE = 'cdel'

legal_commands = []
legal_commands.append(PING)
legal_commands.append(SHOW_CLIENT_LOG)
legal_commands.append(SHOW_HUB_LOG)
legal_commands.append(CONTAINER_GET)
legal_commands.append(CONTAINER_RUN_TEST)
legal_commands.append(CONTAINER_STOP_TEST)
legal_commands.append(CONTAINER_RUN)
legal_commands.append(CONTAINER_STOP)
legal_commands.append(CONTAINER_LIST)
legal_commands.append(CONTAINER_DELETE)

# roughly 3x average
max_run_time_for_type = {
    # pvoe
    'coll': 5,
    'op':   6,
    'sc':   5,
    'stc':  5,
    'sc':  5,
    #avoe
    'irrat':    6,
    'multa':    6,
    'socimit': 15,
    'socapp':   6,
    'anona':    6,
    'opref':    6,
    #inter
    'holes':   90,
    'lava':    40,
    'agentid': 18,
    'cont':    30,
    'movtarg': 15,
    'obst':    12,
    'tool':    90,
    'occl':    30,
    'ramps':   60,
    'solid':    9,
    'spelim':  12,
    'suprel':   6,
    'iop':     12,
    'math':    15,
    'numcomp':  9,
    'imit':    33,
    'setrot':   9,
    'spatref': 12,
    'reor':     9,
    'tlch':    60,
    'tlas':    60,
    'hidtraj': 12,
    'coltraj': 12,
    'sltk':     5,
    'shell':   12,


    # #inter
    # 'holes':   1,
    # 'lava':    1,
    # 'agentid': 1,
    # 'cont':    1,
    # 'movtarg': 1,
    # 'obst':    1,
    # 'tool':    1,
    # 'occl':    1,
    # 'ramps':   1,
    # 'solid':    1,
    # 'spelim':  1,
    # 'suprel':   1,
    # 'iop':     1,
    # 'math':    1,
    # 'numcomp':  1,
    # 'imit':    1,
    # 'setrot':   1,
    # 'spatref': 1,
    # 'reor':     1,
    # 'tlch':    1,
    # 'tlas':    1,
    # 'hidtraj': 1,
    # 'coltraj': 1,
    # 'sltk':     1,
    # 'shell':   1
}
