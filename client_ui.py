import PySimpleGUI as sg
import os



def start_run():
    os.system('python scripts/dummy_timer_loop_for_testing.py&')

def stop_run():
    os.system('pkill -f dummy_timer_loop_for_testing.py')




ENABLE = 'Enable Container Runs'
DISABLE = 'Disable Container Runs'
sg.theme('LightGrey')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('inter_rajesh_mapping_v2')],
            [sg.Button(ENABLE, size=(30,2), button_color = 'green', font=('Helvetica', 14))],
            [sg.Button(DISABLE, size=(30,2), button_color = 'red', font=('Helvetica', 14), disabled=True)],
            [sg.Button('Quit') ]]

# Create the Window 
window = sg.Window('Optics Container Run Control', layout, margins = (300,150))
# Event Loop to process "events" and get the "values" of the inputs
#sg.theme_previewer()
while True:
    event, values = window.read()
    if event in (None, 'Quit'):   # if user closes window or clicks cancel
        break
    elif event == ENABLE:
        enable_button = window[ENABLE]
        enable_button.update( disabled=True)
        disable_button = window[DISABLE]
        disable_button.update( disabled=False)
        start_run()
        
    elif event == DISABLE:
        enable_button = window[ENABLE]
        enable_button.update( disabled=False)
        disable_button = window[DISABLE]
        disable_button.update( disabled=True)
        stop_run()
