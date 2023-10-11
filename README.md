# TAPO L530 Control

This is a small practice project for controlling a TAPO L530 lightbulb. The project uses the plugp100 API to control the lightbulb, and it also uses speech_recognition for voice commands. The application has a GUI for configuration, built using PySimpleGUI. This GUI is used to input the user's credentials (username and password) and the IP address of the lightbulb. These details are saved in a configuration file and are used to establish a connection with the lightbulb.

One of the key features of this application is the ability to control the lightbulb using voice commands. The application continuously listens for specific voice commands such as "light", "toggle", "lamp", "turn on", and "turn off". When these commands are detected, the application sends the corresponding command to the lightbulb.

In addition to voice commands, the project includes a tray app created with pystray that has a simple interface with an exit button and a toggle button for turning the light on/off. The toggle button is used to manually turn the lightbulb on or off, while the exit button is used to close the application.
## Features

- Control TAPO L530 lightbulb
- Voice commands
- Tray app with toggle and exit buttons
- GUI for configuration

## Prerequisites

- Python 3.10 or higher
- pipenv

## Dependencies

- plugp100
- speech_recognition
- pystray
- PySimpleGUI

## Installation

1. Clone the repository

       git clone https://github.com/Zept0n/Tapo-L530-Control.git 

3. Navigate to the project directory

5. Install the dependencies
   
       pipenv install 

## Usage

1. Run the GUI for configuration
   
       pipenv run python .\src\gui.py
3. Enter your username, password, and the IP of the lightbulb
4. Click 'Save'
5. Click 'Run' to start the tray app
6. Use the tray app to control the lightbulb or use voice commands

## License
[MIT](https://choosealicense.com/licenses/mit/)
