

REMOTE_USERS = ['jed','atharva']
CLIENT_POLLING_DELAY = 2
SERVER_POLLING_DELAY = 2

REMOTE_ROOT =  '/home/ubuntu/optics_remote_control'
TO_USER_REMOTE_DIR = 'messages_to_user'
FROM_USER_REMOTE_DIR = 'messages_from_user'

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
    'shell':   12
}
