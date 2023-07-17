import sys, os
import time
from remote_control.message_mux import MessageMux
from remote_control.constants import SERVER_POLLING_DELAY, SHOW_HUB_LOG, legal_commands
from remote_control.runner_names import RunnerNames
from remote_control.constants import HUB_SCAN_COUNT_LIMIT, PING, CONTAINER_GET, CONTAINER_RUN, CONTAINER_STOP
from remote_control.constants import CONTAINER_RUN_TEST, CONTAINER_STOP_TEST, CONTAINER_LIST, CONTAINER_DELETE

def usage():
    print('usage: <user> <command>')
    print('        <user> ping')
    print('        <user> cget <container_name>')

def is_legal_command(command):
    if command in legal_commands:
        return True
    return False

def scan_for_responses(message_mux):
    scan_count = 0
    while not message_mux.has_incoming_messages() and scan_count < HUB_SCAN_COUNT_LIMIT:
        time.sleep(SERVER_POLLING_DELAY)
        message_mux.scan_for_user_responses()
        scan_count += 1
    if not scan_count == HUB_SCAN_COUNT_LIMIT:
        # i.e. we got here because we received an answer
        message_mux.print_and_log_responses_from_clients()
        message_mux.archive_inbound_messages()

if __name__=='__main__':
    if not 'OPTICS_HOME' in os.environ:
        print('please set OPTICS_HOME environment variable')
        sys.exit(1)

    optics_home = os.environ['OPTICS_HOME']
    hub_log_path = os.path.join(optics_home, 'remote_control', 'hub_log.txt')
    runner_names = RunnerNames()
    message_mux = MessageMux(runner_names.names)
    while True:
        print(f'\nusers: {runner_names.names}')
        print('enter command in the form: user command')
        full_command = input('$$ ')
        command_parts = full_command.split()
        
        if len(command_parts) == 1:
            if command_parts[0] == SHOW_HUB_LOG:
                with open(hub_log_path, 'r') as f:
                    for line in f:
                        print(line, end='')
                continue
            else:
                usage()
                continue
        if len(command_parts) == 0:
            scan_for_responses(message_mux)
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
            timestamp = message_mux.send_control_message(user, command_name, command)
            scan_for_responses(message_mux)
            
        else:
            print(f'invalid command: {command}')
            usage()
            continue

    
