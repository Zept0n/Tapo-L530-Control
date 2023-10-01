import asyncio
import os
import time
import threading
import sys
import speech_recognition as sr
import pyaudio
import config
import pystray
from pystray import MenuItem as item
from PIL import Image
from plugp100.api.tapo_client import TapoClient, AuthCredential
from plugp100.api.light_device import LightDevice
from functools import partial 
import concurrent.futures

# Define the exiting flag
exiting = False
state = False


async def main():
    # create generic tapo api
    username = config.USERNAME
    password = config.PASSWORD
    ip = config.IP

    credential = AuthCredential(username, password)
    client = await TapoClient.connect(credential, ip)
    light = LightDevice(client)
    print('Loading...')
    toggle_light = await create_toggle_light(light)  # Create the toggle_light function
    
    image = Image.open('light-bulb.png') # Load the icon image

    #TODO create toggle menu item - problem with async functions
    # Create the menu items
    menu = (
        item('Exit', exit_action),
    )


    # Create the system tray icon
    icon = pystray.Icon('name',image, 'L530 Control',menu)

    # Create a separate thread for the system tray icon
    icon_thread = threading.Thread(target=icon.run)
    icon_thread.daemon = True
    icon_thread.start()

    try:
        await listen(light,toggle_light)
    except Exception as e:
        print(f"Error: {e}")
        try:
            # Close the TapoClient connection
            await client.close()
            print("TapoClient connection closed.")
        except Exception as e:
            print(f"Error: {e}")
        # Close the tray app
        icon.stop()
    finally:
        try:
            await client.close()
            print("TapoClient connection closed.")
        except Exception as e:
            print(f"Error: {e}")
        icon.stop()

async def listen(light,toggle_light):
    global exiting
    # start listening for voice commands
    r = sr.Recognizer()
    m= sr.Microphone()
    with m as source:
            r.adjust_for_ambient_noise(source,duration=1) # ambient noise adjust
            while not exiting:  # loop to continuously listen for commands
                print("Listening...")
                try:
                    audio = r.listen(source, phrase_time_limit=3)
                except sr.WaitTimeoutError as e:
                    print(f"Timeout error: {e}")
                    continue  # Continue the loop when a timeout error occurs

                if audio:
                    try:
                        commands = ["white", "light", "toggle", "lamp", "night"]
                        command = r.recognize_google(audio).lower()
                        print(f"You said: {command}")

                        if any(word in command for word in commands):
                            await toggle_light()
                        elif "turn on" in command:
                            await light.on()
                        elif "turn off" in command:
                            await light.off()

                    except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                    except pyaudio.paBadStreamPtr:
                        # Ignore this exception if the program is exiting
                        if not exiting:
                            raise

def exit_action(icon,item):
    global exiting
    exiting = True
    try:
        icon.stop()
        sys.exit()
    except Exception as e:
        print(f"Error: {e}")
    except SystemExit:
        pass
    
async def create_toggle_light(light):
    responce = await light.get_state()
    light_state = responce.value.device_on
    light_name = responce.value.info.nickname
    async def toggle_light():
        print(f'Toggling {light_name}')
        nonlocal light_state
        # Toggle the light state
        if light_state:
            await light.off()
            light_state = False
        else:
            await light.on()
            light_state = True

        time.sleep(2)  # Add a 2-second delay between toggles 
    return toggle_light


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        exiting = True
    finally:
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()


        
    

    

    

    