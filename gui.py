# gui.py
import PySimpleGUI as sg
import os
import config
import asyncio
from threading import Thread
import main

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
    if event == 'Save':
        with open('config.py', 'w') as configfile:
            configfile.write(f"USERNAME = '{values['-USERNAME-']}'\n")
            configfile.write(f"PASSWORD = '{values['-PASSWORD-']}'\n")
            configfile.write(f"IP = '{values['-IP-']}'\n")
            configfile.flush()
            os.fsync(configfile.fileno())
    elif event =='Run':
        Thread(target=asyncio.run, args=(main.main(),)).start()
        window.hide()
        break
    elif event == 'Clear Config':
        with open('config.py', 'w') as configfile:
            configfile.write("USERNAME = ''\n")
            configfile.write("PASSWORD = ''\n")
            configfile.write("IP = ''\n")
        window['-USERNAME-'].update('')  # Clear the 'Username' input box
        window['-PASSWORD-'].update('')  # Clear the 'Password' input box
        window['-IP-'].update('')  # Clear the 'IP Address' input box

window.close()