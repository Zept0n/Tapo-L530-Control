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

class LightControl:
    def __init__(self,username,password,ip):
        self.exiting = False
        self.state = False
        self.username=username
        self.password=password
        self.ip=ip

    async def run(self):
        # create generic tapo api
        credential = AuthCredential(self.username, self.password)
        client = await TapoClient.connect(credential, self.ip)
        self.light = LightDevice(client)
        print('Loading...')
        responce = await self.light.get_state()
        self.state = responce.value.device_on
        self.name = responce.value.info.nickname

        #toggle_light = await self.create_toggle_light(light)  # Create the toggle_light function
        
        image = Image.open('light-bulb.png') # Load the icon image

        #TODO create toggle menu item - problem with async functions
        # Create the menu items
        menu = (
            item('Exit', self.exit_action),
        )


        # Create the system tray icon
        icon = pystray.Icon('name',image, 'L530 Control',menu)

        # Create a separate thread for the system tray icon
        icon_thread = threading.Thread(target=icon.run)
        icon_thread.daemon = True
        icon_thread.start()

        try:
            await self.listen()
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

    async def listen(self):
        # start listening for voice commands
        r = sr.Recognizer()
        m= sr.Microphone()
        with m as source:
                r.adjust_for_ambient_noise(source,duration=1) # ambient noise adjust
                while not self.exiting:  # loop to continuously listen for commands
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

                            #TODO Implement commands for color and brightness
                            if any(word in command for word in commands):
                                await self.toggle_light()
                            elif "turn on" in command:
                                await self.light.on()
                            elif "turn off" in command:
                                await self.light.off()

                        except sr.UnknownValueError:
                            print("Google Speech Recognition could not understand audio")
                        except sr.RequestError as e:
                            print(f"Could not request results from Google Speech Recognition service; {e}")
                        except pyaudio.paBadStreamPtr:
                            # Ignore this exception if the program is exiting
                            if not self.exiting:
                                raise

    def exit_action(self,icon,item):
        self.exiting = True
        try:
            icon.stop()
            sys.exit()
        except Exception as e:
            print(f"Error: {e}")
        except SystemExit:
            pass
        

    async def toggle_light(self):
        print(f'Toggling {self.name}')
        # Toggle the light state
        if self.state:
            await self.light.off()
            self.state = False
        else:
            await self.light.on()
            self.state = True

        time.sleep(2)  # Add a 2-second delay between toggles 


if __name__ == "__main__":
    light_control = LightControl(config.USERNAME,config.PASSWORD,config.IP)
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(light_control.run())
    except KeyboardInterrupt:
        exiting = True
    finally:
        loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()


        
    

    

    

    