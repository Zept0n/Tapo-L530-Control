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

# Define the exiting flag
exiting = False
state = False


async def main():
    global exiting
    # create generic tapo api
    username = config.USERNAME
    password = config.PASSWORD
    ip = config.IP

    credential = AuthCredential(username, password)
    client = await TapoClient.connect(credential, ip)
    light = LightDevice(client)
    toggle_light = create_toggle_light(light)  # Create the toggle_light function
    print('Initiliazing...')
    print(loop)
    await toggle_light()
    await toggle_light()

    async def toggle_light_wrapper():
        await toggle_light()


    
    image = Image.open('light-bulb.png') # Load the icon image

    # Create the menu items
    menu = (
        item('Exit', exit_action),
        item('Toggle', lambda icon, item: toggle_light_wrapper()),
    )



    # Create the system tray icon
    icon = pystray.Icon('name',image, 'L530 Control',menu)

    try:
        # Create a separate thread for the system tray icon
        icon_thread = threading.Thread(target=icon.run)
        icon_thread.daemon = True
        icon_thread.start()

        # start listening for voice commands
        r = sr.Recognizer()
        with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source,duration=1) # ambient noise adjust
                while not exiting:  # loop to continuously listen for commands
                    print("Listening...")
                    try:
                        audio = r.listen(source, timeout=6, phrase_time_limit=3)
                    except sr.WaitTimeoutError as e:
                        print(f"Timeout error: {e}")
                        continue  # Continue the loop when a timeout error occurs

                    if audio:
                        try:
                            command = r.recognize_google(audio).lower()
                            print(f"You said: {command}")

                            if "white" in command:
                                await toggle_light()
                            elif "light" in command:
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
        
    except Exception as e:
        print(f"Error: {e}")
        try:
            await client.close()
            print("TapoClient connection closed.")
        except Exception as e:
            print(f"Error: {e}")
        icon.stop()
    finally:
        try:
            await client.close()
            print("TapoClient connection closed.")
        except Exception as e:
            print(f"Error: {e}")
        # Close the TapoClient connection
        icon.stop()


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
    
def create_toggle_light(light):
    light_state = False
    async def toggle_light():
        print('toggling light1')
        nonlocal light_state
        # Toggle the light state
        if light_state:
            await light.off()
            light_state = False
        else:
            await light.on()
            light_state = True

        time.sleep(2)  # Add a 2-second delay between toggles (you can adjust the delay as needed)

    def toggle_light_sync():
        print('toggling light2')
        future = asyncio.run_coroutine_threadsafe(toggle_light(), loop)
        # Wait for the Future to complete
        future.result()

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


        
    

    

    

    