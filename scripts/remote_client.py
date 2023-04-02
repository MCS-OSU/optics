import sys, os
import time
from remote_control.remote_client_messenger import RemoteClientMessenger
from remote_control.constants import REMOTE_USERS, CLIENT_POLLING_DELAY, REMOTE_ROOT

def usage():
    print('usage: python3 remote.py <user>')
    sys.exit(1)

if __name__=='__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit()
    user = sys.argv[1]
    if not user in REMOTE_USERS:
        print(f'invalid user: {user}')
        usage()

    messenger = RemoteClientMessenger(user, REMOTE_ROOT)
    while True:
        while not messenger.has_received_command():
            messenger.scan_for_commands()
            time.sleep(CLIENT_POLLING_DELAY)
        commands = messenger.get_commands()
        for command in commands:
            timestamp = command.timestamp
            command_text = command.command_text
            command_type = command.command_type
            command_fname = command.command_fname
            print(f'{user} : {command}')
            # re-use the file so it has the command in it already
            response_fname = f'{timestamp}_{user}_response.txt'
            os.system(f'mv {command_fname} {response_fname}')
            f = open(response_fname, 'a')
            f.write('\n\n         - response -\n\n')
            f.close()
            cmd = f'{command_text} >> {response_fname}'
            os.system(cmd)
            messenger.send_response(response_fname)
            


