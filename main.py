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

# Define the exiting flag
exiting = False

async def main():
    global exiting
    # create generic tapo api
    username = config.USERNAME
    password = config.PASSWORD
    ip = config.IP
    

    credential = AuthCredential(username, password)
    client = await TapoClient.connect(credential, ip)

    light = LightDevice(client)

    image = Image.open('light-bulb.png') # Load the icon image

    # Create the system tray icon
    icon = pystray.Icon('name', image, 'L530 Control')

    # Create the menu items
    menu = (
        item('Exit', exit_action(icon, client)),
    )
    
    # Assign the menu to the icon
    icon.update_menu(menu)

    try:
        # Create a separate thread for the system tray icon
        icon_thread = threading.Thread(target=icon.run)
        icon_thread.daemon = True
        icon_thread.start()

        # start listening for voice commands
        r = sr.Recognizer()
        with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source,duration=3) # ambient noise adjust
                while not exiting:  # loop to continuously listen for commands
                    print("Listening...")
                    try:
                        audio = r.listen(source, timeout=5, phrase_time_limit=3)  # Wrap in a try-except block
                    except sr.WaitTimeoutError as e:
                        print(f"Timeout error: {e}")
                        continue  # Continue the loop when a timeout error occurs

                    if audio:
                        try:
                            command = r.recognize_google(audio).lower()
                            print(f"You said: {command}")

                            if "turn on" in command:
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
    except KeyboardInterrupt:
        exiting = True
        icon.stop()
    finally:
        icon.stop()

def exit_action(icon, client):
    global exiting
    exiting = True
    icon.stop()
    # Clean up resources
    try:
        # Release the microphone
        with sr.Microphone() as source:
            source.stop_stream()
            source.close()
        print("Microphone released.")

        # Close the TapoClient connection
        if client:
            client.close()
            print("TapoClient connection closed.")

    except Exception as e:
        print(f"Error during cleanup: {e}")

    # Exit the script
    sys.exit()
    


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        exiting = True
    finally:
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()


        
    

    

    

    