import sys, os
import time
import threading
import PySimpleGUI as sg

from remote_control.client_commands import ClientCommands
from remote_control.messenger import Messenger
from remote_control.runner_names import RunnerNames
from remote_control.constants import CLIENT_POLLING_DELAY


ENABLED = 'Container Runs Enabled'
DISABLED = 'Container Runs Disabled'
STATUS = '-STATUS-'
STATUS_DISABLED           = 'status: optics container runs disabled'
STATUS_FETCHING_CONTAINER = 'status: fetching_container'
STATUS_RUNNING_SCENES     = 'status: running_scenes'


def usage():
    print('usage: python3 remote_client.py <user>')
    sys.exit(1)


def messaging_loop(status_dict, enablement_dict):
    while True:
        time.sleep(2)
        count = 1
        while not messenger.has_incoming_messages():
            status_dict['status'] = f'listening for commands...{count}'
            messenger.scan_for_inbound_commands()
            time.sleep(CLIENT_POLLING_DELAY)
            count+=1
        
        client_commands = ClientCommands(messenger)
        for client_command in client_commands.commands:
            status_dict['status'] = f'processing command: {client_command.command}'
            client_command.execute(enablement_dict['is_run_enabled'])
            status_dict['status'] = f'(sending response)'
            messenger.send_response_message(client_command)
        


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

    sg.theme('LightGrey')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text(text=STATUS_DISABLED, key=STATUS)],
                [sg.Radio(text=ENABLED,  group_id='radiogroup', enable_events=True, font=('Helvetica', 14), key = ENABLED)],
                [sg.Radio(text=DISABLED, group_id='radiogroup', enable_events=True, font=('Helvetica', 14), key = DISABLED)],
                [sg.Text('', size=(10,2), font=('Helvetica', 14), key = STATUS, justification='left')],
                [sg.Button('Quit') ]]

    # Create the Window 
    #status_dict = {'status': STATUS_DISABLED, 'is_run_enabled': False}
    enablement_dict = {'is_run_enabled': False}
    status_dict     = {'status': STATUS_DISABLED}
    window = sg.Window('Optics Container Run Control', layout, margins = (300,150))
    threading.Thread(target=messaging_loop, args=(status_dict, enablement_dict), daemon=True).start()

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Quit'):   # if user closes window or clicks cancel
            break
        window[STATUS].update(status_dict['status'])
        if event == ENABLED:
            enablement_dict['is_run_enabled'] = True
            window[STATUS].update(ENABLED)
            continue 
        if event == DISABLED:
            enablement_dict['is_run_enabled'] = False
            window[STATUS].update(DISABLED)
            continue
   
            


