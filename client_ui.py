import PySimpleGUI as sg
import os, sys
import threading
from scripts.machines import EC2B
from ui.container_job_scanner import ContainerJobScanner
from ui.container_manager import ContainerManager

STATUS_DISABLED           = 'status: optics container runs disabled'
STATUS_FETCHING_CONTAINER = 'status: fetching_container'
STATUS_RUNNING_SCENES     = 'status: running_scenes'
def start_run(assigned_container):
    os.system(f'python scripts/dummy_timer_loop_for_testing.py {assigned_container}&')


def stop_run():
    os.system('pkill -f dummy_timer_loop_for_testing.py')

def container_loop(user_name, window, status_key):
    scanner = ContainerJobScanner(user_name, window, status_key)
    
    while True:
        assigned_container = scanner.scan()
        cm = ContainerManager(window, assigned_container)
        container = cm.fetch_container()
        if not container.is_ready():
            print(f'ERROR - failed to fetch  container {assigned_container}')
        else:
            container.run()

def fetch_container(container_name):
    ec2b = EC2B()
    remote_src_path = '/home/ubuntu/containers/{container_name}'
    ec2b.get_file(remote_src_path, '.')
    
def ui_loop(user_name):
    ENABLE = 'Enable Container Runs'
    DISABLE = 'Disable Container Runs'
    STATUS = '-STATUS-'
    sg.theme('LightGrey')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text(text=STATUS_DISABLED, key=STATUS)],
                [sg.Button(ENABLE, size=(30,2), button_color = 'green', font=('Helvetica', 14))],
                [sg.Button(DISABLE, size=(30,2), button_color = 'red', font=('Helvetica', 14), disabled=True)],
                [sg.Button('Quit') ]]

    # Create the Window 
    window = sg.Window('Optics Container Run Control', layout, margins = (300,150))
    threading.Thread(target=container_loop, args=(user_name, window,STATUS,), daemon=True).start()
    # Event Loop to process "events" and get the "values" of the inputs
    #sg.theme_previewer()
    while True:
        if window[STATUS] == STATUS_CHECKING_FOR_JOB:
            
            if assigned_container is None:
                print(f'no container assigned to {name}')
                # remain in checking_for_job_state
                continue
            if not os.path.exists(assigned_container):
                print(f'fetching container {assigned_container}')
                fetch_container(assigned_container)
            if not os.path.exists(assigned_container):
                print(f'failed to fetch container {assigned_container}')
                continue
            start_run(assigned_container)
            disable_button = window[DISABLE]
            disable_button.update( disabled=False)
        event, values = window.read()
        if event in (None, 'Quit'):   # if user closes window or clicks cancel
            break
        elif event == ENABLE:
            window[STATUS].update(STATUS_CHECKING_FOR_JOB)
            enable_button = window[ENABLE]
            enable_button.update( disabled=True)
            threading.Thread(target=run_loop, args=(window,), daemon=True).start()
            
            
        elif event == DISABLE:
            enable_button = window[ENABLE]
            enable_button.update( disabled=False)
            disable_button = window[DISABLE]
            disable_button.update( disabled=True)
            stop_run()


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