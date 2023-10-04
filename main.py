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
import importlib


class LightControl:
    def __init__(self,username,password,ip):
        self.exiting = False
        self.state = False
        self.username=username
        self.password=password
        self.ip=ip
        self.loop = None

    async def login(self):
        # create generic tapo api
        credential = AuthCredential(self.username, self.password)
        self.client = await TapoClient.connect(credential, self.ip)
        self.light = LightDevice(self.client)
        responce = await self.light.get_state()
        self.state = responce.value.device_on
        self.name = responce.value.info.nickname

        
    async def run(self):
        try:
            self.loop = asyncio.get_running_loop()
            self._tray_icon()
            listen_thread = threading.Thread(target=self.listen)
            listen_thread.start()
            while listen_thread.is_alive():
                await asyncio.sleep(0.1)  # Sleep for a short time to avoid busy waiting
        except Exception as e:
            print(f"Error: {e}")
            await self._cleanup()
        finally:
            await self._cleanup()

    async def _cleanup(self):
        self.exiting=True
        # Close the TapoClient connection
        await self.close_client()
        # Close the tray app
        self.icon.stop()

    async def close_client(self):
        try:
            # Close the TapoClient connection
            await self.client.close()
            print("TapoClient connection closed.")
        except Exception as e:
            print("Error closing TapoClient connection")


    def _tray_icon(self):
        image = Image.open('favicon.ico') # Load the icon image

        #TODO create toggle menu item - problem with async functions
        # Create the menu items
        menu = (
            item('Toggle',self.toggle_light_wrapper),
            item('Exit', self.exit_action),
        )

        # Create the system tray icon
        icon = pystray.Icon('name',image, 'L530 Control',menu)

        self.icon = icon
        # Create a separate thread for the system tray icon
        icon_thread = threading.Thread(target=self.icon.run)
        icon_thread.daemon = True
        icon_thread.start()

    def listen(self):
        asyncio.run(self.listen_coroutine())

    async def listen_coroutine(self):
        try:
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
                                    asyncio.run_coroutine_threadsafe(self.toggle_light(), self.loop)
                                elif "turn on" in command:
                                    self._run_command(self.light.on)
                                elif "turn off" in command:
                                    self._run_command(self.light.off)

                            except sr.UnknownValueError:
                                print("Google Speech Recognition could not understand audio")
                            except sr.RequestError as e:
                                print(f"Could not request results from Google Speech Recognition service; {e}")
                            except pyaudio.paBadStreamPtr:
                                # Ignore this exception if the program is exiting
                                if not self.exiting:
                                    raise
                        await asyncio.sleep(0)
        except Exception as e:
            sys.exit()

    def exit_action(self,icon,item):
        self.exiting = True
        try:
            self.icon.stop()
            sys.exit()
        except Exception as e:
            print(f"Error: {e}")
        except SystemExit:
            pass
        
    def _run_command(self,command):
        asyncio.run_coroutine_threadsafe(command(), self.loop)

    def toggle_light_wrapper(self,icon,item):
        asyncio.run_coroutine_threadsafe(self.toggle_light(), self.loop)

    async def toggle_light(self):
        print(f'Toggling {self.name}')
        # Toggle the light state
        if self.state:
            await self.light.off()
            self.state = False
        else:
            await self.light.on()
            self.state = True

        await asyncio.sleep(2)  # Add a 2-second delay between toggles 


async def main():
    importlib.reload(config)
    try:
        light_control = LightControl(config.USERNAME,config.PASSWORD,config.IP)
        await light_control.login()
    except Exception as e:
        print(f"Login failed ${e}")
        sys.exit()
    try:
        await light_control.run()
    except Exception as e:
        print(f"Run failed ${e}")
        sys.exit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exiting')
        sys.exit()


