import sys
import time
from remote_control.message_mux import MessageMux
from remote_control.constants import REMOTE_USERS, SERVER_POLLING_DELAY

def usage():
    print('usage: <user> <command>')
    print('        <user> ping')

def is_legal_command(command):
    if command == 'ping':
        return True
    return False

if __name__=='__main__':
    message_mux = MessageMux(REMOTE_USERS)
    while True:
        print(f'available users: {REMOTE_USERS}')
        print('enter command in the form: user command')
        full_command = input('$$ ')
        command_parts = full_command.split()
        if len(command_parts) == 0:
            continue
        if len(command_parts) == 1:
            usage()
            continue
        user = command_parts[0]
        if not user in REMOTE_USERS:
            print(f'invalid user: {user}')
            continue
        command = command_parts[1]
        if is_legal_command(command):
            message_mux.send_control_message(user, command)
            while not message_mux.has_responses():
                time.sleep(SERVER_POLLING_DELAY)
                message_mux.scan_for_user_responses()
            message_mux.print_responses()
        else:
            print(f'invalid command: {command}')
            usage()
            continue

    
