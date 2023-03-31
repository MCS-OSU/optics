import PySimpleGUI as sg
import os, sys
import threading
import time
# from scripts.machines import EC2B
from ui.container_job_scanner import ContainerJobScanner
from ui.container_manager import ContainerManager
from remote_control.remote_messenger import RemoteMessenger

ENABLE = 'Enable Container Runs'
DISABLE = 'Disable Container Runs'
STATUS = '-STATUS-'
STATUS_DISABLED           = 'status: optics container runs disabled'
STATUS_FETCHING_CONTAINER = 'status: fetching_container'
STATUS_RUNNING_SCENES     = 'status: running_scenes'
def start_run(assigned_container):
    os.system(f'python scripts/dummy_timer_loop_for_testing.py {assigned_container}&')


def stop_run():
    os.system('pkill -f dummy_timer_loop_for_testing.py')

def messaging_loop(user_name, window, status_key):
    count = 1
    messenger = RemoteMessenger(user_name)
    while True:
        commands = messenger.await_control_commands()
        window[STATUS].update(f'waiting for commands...{count}')
        count+=1
        
    # scanner = ContainerJobScanner(user_name, window, status_key)
    
    # while True:
    #     assigned_container = scanner.scan()
    #     cm = ContainerManager(window, assigned_container)
    #     container = cm.fetch_container()
    #     if not container.is_ready():
    #         print(f'ERROR - failed to fetch  container {assigned_container}')
    #     else:
    #         container.run()

def ui_loop(user_name):
    
    sg.theme('LightGrey')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text(text=STATUS_DISABLED, key=STATUS)],
                [sg.Radio(text="Runs enabled", group_id='radiogroup', font=('Helvetica', 14))],
                [sg.Radio(text="Runs disabled", group_id='radiogroup', font=('Helvetica', 14))],
                [sg.Text('', size=(10,2), font=('Helvetica', 14), key = STATUS, justification='left')],
                [sg.Button('Quit') ]]

    # Create the Window 
    window = sg.Window('Optics Container Run Control', layout, margins = (300,150))
    threading.Thread(target=messaging_loop, args=(user_name, window,STATUS,), daemon=True).start()
    # Event Loop to process "events" and get the "values" of the inputs
    #sg.theme_previewer()
    while True:
        event, values = window.read()
        if event in (None, 'Quit'):   # if user closes window or clicks cancel
            break



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python client_ui.py <name>')
        sys.exit()
    name = sys.argv[1].lower()
    valid_names = ['ridha', 'rajesh', 'matthew', 'mazen', 'pranay', 'atharva', 'shreya', 'venkat', 'venkatesh', 'jed']
    if not name in valid_names:
        print(f'unknown name: {name}')
        print(f'name must be one of: {valid_names}')
        sys.exit()
    
    ui_loop(name)