import PySimpleGUI as sg
import threading
import sys, os
from remote_control.runner_names import RunnerNames
from remote_control.remote_messenger import RemoteMessenger

def get_name_row(name, specs):

    row = [sg.Text(name, size=(10,2), font=('Helvetica', 14)), sg.Listbox(values=specs, size=(30,1), font=('Helvetica', 14), key='spec_names')]
    row.append(sg.Button('Load',  size=(5,2), font=('Helvetica', 14), key = f'messenger_load_{name}'))
    row.append(sg.Text('', size=(10,2), font=('Helvetica', 14), key = f'load_status_{name}', justification='left'))
    row.append(sg.Button('Run',   size=(4,2), font=('Helvetica', 14), key = f'messenger_run_{name}'))
    row.append(sg.Text('', size=(10,2), font=('Helvetica', 14), key = f'run_status_{name}', justification='left'))
    row.append(sg.Button('Stop',  size=(5,2), font=('Helvetica', 14), key = f'messenger_stop_{name}'))
    row.append(sg.Text('', size=(10,2), font=('Helvetica', 14), key = f'stop_status_{name}', justification='left'))
    row.append(sg.Button('Clean', size=(6,2), font=('Helvetica', 14), key = f'messenger_clean_{name}'))
    row.append(sg.Text('', size=(10,2), font=('Helvetica', 14), key = f'clean_status_{name}', justification='left'))
    #row.append(sg.Text('', size=(30,2), font=('Helvetica', 14), key = f'status_{name}', justification='left'))
    # for spec in specs:
    #     spec_name_width = 15
    #     key = f'control_{name}_{spec}'
    #     if spec == 'Off':
    #         spec_name_width = 5
    #     row.append(sg.Radio(spec, name, enable_events=True, default=False, size=(spec_name_width,2), font=('Courier', 14), key=key))
        #row.append(sg.Button(spec,size=(spec_name_width,2), font=('Courier', 14)))
    return row

def control_message(remote_messenger, cmd, window):
    remote_messenger.send_control_command(cmd, window)




def ui_loop():
    specs = ['spec1', 'spec2', 'spec3']
    runner_names = RunnerNames()
    layout = []
    for name in runner_names.names:
        name_row = get_name_row(name, specs)
        layout.append(name_row)
    
    remote_messengers = {}
    for name in runner_names.names:
        remote_messengers[name] = RemoteMessenger(name)
    #sg.theme('LightGrey')   # Add a touch of color
    layout.append([sg.Button('Quit') ])
    # All the stuff inside your window.
    

    # Create the Window 
    window = sg.Window('Optics Container Run Control', layout, margins = (10,10))

    while True:
        event, values = window.read()
        print(f'event: {event}, values: {values}')
        if event in (None, 'Quit'):   # if user closes window or clicks cancel
            break
        
        if event.startswith('messenger_'):
            cmd, name = event.split('_')[1:]
            remote_messenger = remote_messengers[name]
            threading.Thread(target=control_message, args=(remote_messenger, cmd, window), daemon=True).start()
        
if __name__ == '__main__':
    if os.environ.get('OPTICS_HOME') is None:
        print('OPTICS_HOME is not set')
        sys.exit(1)
    if os.environ.get('OPTICS_DATASTORE') is None:
        print('OPTICS_DATASTORE is not set - set to either ec2a or ec2b')
        sys.exit(1)
    ui_loop()