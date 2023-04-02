import sys
import time
from remote_control.message_mux import MessageMux
from remote_control.constants import REMOTE_USERS, SERVER_POLLING_DELAY, REMOTE_ROOT


if __name__=='__main__':
    message_mux = MessageMux(REMOTE_USERS, REMOTE_ROOT)
    while True:
        print(f'available users: {REMOTE_USERS}')
        user = input('enter user: ')
        if not user in REMOTE_USERS:
            print(f'invalid user: {user}')
            continue
        command = input(f'{user} : ')
        message_mux.create_and_send_message(user, command)
        while not message_mux.has_responses():
            time.sleep(SERVER_POLLING_DELAY)
            message_mux.scan_for_responses()
        message_mux.print_responses()

    
