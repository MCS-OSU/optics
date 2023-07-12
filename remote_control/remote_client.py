import sys, os
import time
from remote_control.client_commands import ClientCommands
from remote_control.messenger import Messenger
from remote_control.runner_names import RunnerNames
from remote_control.constants import CLIENT_POLLING_DELAY, REMOTE_ROOT

def usage():
    print('usage: python3 remote_client.py <user>')
    sys.exit(1)

if __name__=='__main__':
    if not 'OPTICS_HOME' in os.environ:
        print('please set OPTICS_HOME environment variable')
        sys.exit(1)

    if len(sys.argv) != 2:
        usage()
        sys.exit()
    runner_names = RunnerNames()
    user = sys.argv[1]
    if not user in runner_names.names:
        print(f'invalid user: {user}')
        usage()

    messenger = Messenger(user, 'client')
    while True:
        while not messenger.has_incoming_messages():
            messenger.scan_for_inbound_commands()
            time.sleep(CLIENT_POLLING_DELAY)
        client_commands = ClientCommands(messenger)
        for client_command in client_commands.commands:
            client_command.execute()
            messenger.send_response_message(client_command)
            


