# gui.py
import PySimpleGUI as sg
import os
import src.config as config
import asyncio
from threading import Thread
import src.main as main

def start():
    layout = [
        [sg.Text('Username'), sg.Input(default_text=config.USERNAME, key='-USERNAME-')],
        [sg.Text('Password'), sg.Input(default_text=config.PASSWORD, key='-PASSWORD-', password_char='*')],
        [sg.Text('IP Address'), sg.Input(default_text=config.IP, key='-IP-')],
        [sg.Button('Save'), sg.Button('Clear Config')],
        [sg.Button('Run')]
    ]

    window = sg.Window('Light Control Config', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'Save':
            with open('config.py', 'w') as configfile:
                configfile.write(f"USERNAME = '{values['-USERNAME-']}'\n")
                configfile.write(f"PASSWORD = '{values['-PASSWORD-']}'\n")
                configfile.write(f"IP = '{values['-IP-']}'\n")
                configfile.flush()
                os.fsync(configfile.fileno())
        elif event =='Run':
            #Thread(target=run_main, daemon=True).start()
            Thread(target=asyncio.run, args=(main.main(),)).start()
            break
        elif event == 'Clear Config':
            with open('config.py', 'w') as configfile:
                configfile.write("USERNAME = ''\n")
                configfile.write("PASSWORD = ''\n")
                configfile.write("IP = ''\n")
            window['-USERNAME-'].update('') 
            window['-PASSWORD-'].update('') 
            window['-IP-'].update('')  


    window.close()

start()