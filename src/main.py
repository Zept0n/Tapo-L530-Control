import importlib
import config as config
import asyncio
from light_control import LightControl

async def main():
    importlib.reload(config)
    try:
        light_control = LightControl(config.USERNAME,config.PASSWORD,config.IP)
        await light_control.login()
    except Exception as e:
        print(f"Login failed: {e}")
    try:
        await light_control.run()
    except Exception as e:
        print("Run failed: {e}")



