import sys, os
import time
import threading
import PySimpleGUI as sg

from remote_control.client_commands import ClientCommands
from remote_control.messenger import Messenger
from remote_control.runner_names import RunnerNames
from remote_control.constants import CLIENT_POLLING_DELAY

ENABLEMENT_PROMPT = 'Container Runs'
ENABLED = 'Container Runs Enabled'
DISABLED = 'Container Runs Disabled'
STATUS = '-STATUS-'
STATUS_DISABLED           = 'status: optics container runs disabled'
STATUS_FETCHING_CONTAINER = 'status: fetching_container'
STATUS_RUNNING_SCENES     = 'status: running_scenes'


def usage():
    print('usage: python3 remote_client.py <user>')
    sys.exit(1)


def messaging_loop(enablement_dict, log_window, poll_counter, status_text_field):
    while True:
        time.sleep(2)
        count = 1
        while not messenger.has_incoming_messages():
            poll_counter.update(f'{count}')
            messenger.scan_for_inbound_commands()
            time.sleep(CLIENT_POLLING_DELAY)
            count+=1
        
        client_commands = ClientCommands(messenger)
        for client_command in client_commands.commands:
            log_window.update(log_window.get() + '\n' + f'processing command: {client_command.command}')
            status_text_field.update(f'processing command: {client_command.command}')
            client_command.execute(enablement_dict['is_run_enabled'])
            status_text_field.update(f'sending response for command: {client_command.command}')
            log_window.update(log_window.get() + '\n' + f'(sending response)')
            messenger.send_response_message(client_command)
            status_text_field.update(f'awaiting next command')


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
    #fbig = ('gothic', 30)
    container_runs_text = sg.Text(text=ENABLEMENT_PROMPT, key=ENABLEMENT_PROMPT, border_width=3, text_color='white', background_color='red')
    enable_radio = sg.Radio(text='Enabled',  group_id='radiogroup', enable_events=True, key=ENABLED)
    disable_radio = sg.Radio(text='Disabled', group_id='radiogroup', enable_events=True, key=DISABLED, default=True)
    poll_count_label = sg.Text(text='poll count: ', key='poll_count_label', border_width=3, text_color='black', background_color='white')
    poll_counter = sg.Text(text='', key='poll_counter', border_width=3, text_color='black', background_color='white')
    status_label = sg.Text(text='status: ', key='status_label', border_width=3, text_color='black', background_color='white')
    status_text = sg.Text(text='', key=STATUS, border_width=3, text_color='black', background_color='white')
    layout = [  [container_runs_text, enable_radio, disable_radio],
                #[sg.Text(text='---', key=STATUS)],
                [status_label, status_text, poll_count_label, poll_counter],
                [sg.Multiline(default_text='--log--', size=(80, 20), key='log', autoscroll=True)],
                [sg.Button('Quit') ]]

    # Create the Window 
    #status_dict = {'status': STATUS_DISABLED, 'is_run_enabled': False}
    enablement_dict = {'is_run_enabled': False}
    status_dict     = {'status': STATUS_DISABLED}
    window = sg.Window('Optics Container Run Control', layout, margins = (10,10))
    threading.Thread(target=messaging_loop, args=(enablement_dict, window['log'], window['poll_counter'], window[STATUS]), daemon=True).start()

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Quit'):   # if user closes window or clicks cancel
            break
        window[STATUS].update(status_dict['status'])
        if event == ENABLED:
            enablement_dict['is_run_enabled'] = True
            window[STATUS].update(ENABLED)
            window[ENABLEMENT_PROMPT].update(background_color='green')
            continue 
        if event == DISABLED:
            enablement_dict['is_run_enabled'] = False
            window[STATUS].update(DISABLED)
            window[ENABLEMENT_PROMPT].update(background_color='red')
            continue
   
            


