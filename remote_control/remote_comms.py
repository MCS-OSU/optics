import sys, os
import time
from remote_control.message_mux import MessageMux
from remote_control.constants import SERVER_POLLING_DELAY
from remote_control.runner_names import RunnerNames
from remote_control.constants import PING, CONTAINER_GET

def usage():
    print('usage: <user> <command>')
    print('        <user> ping')
    print('        <user> cget <container_name>')

def is_legal_command(command):
    if command == PING or command == CONTAINER_GET:
        return True
    return False

if __name__=='__main__':
    if not 'OPTICS_HOME' in os.environ:
        print('please set OPTICS_HOME environment variable')
        sys.exit(1)

    runner_names = RunnerNames()
    message_mux = MessageMux(runner_names.names)
    while True:
        print(f'available users: {runner_names.names}')
        print('enter command in the form: user command')
        full_command = input('$$ ')
        command_parts = full_command.split()
        if len(command_parts) == 0:
            continue
        if len(command_parts) == 1:
            usage()
            continue
        user = command_parts[0]
        if not user in runner_names.names:
            print(f'invalid user: {user}')
            continue
        command_name = command_parts[1]
        command = ''
        for i in range(1, len(command_parts)):
            command += command_parts[i] + ' '
        if is_legal_command(command_name):
            message_mux.send_control_message(user, command_name, command)
            while not message_mux.has_incoming_messages():
                time.sleep(SERVER_POLLING_DELAY)
                message_mux.scan_for_user_responses()
            message_mux.print_responses()
            message_mux.archive_inbound_messages()
        else:
            print(f'invalid command: {command}')
            usage()
            continue

    
