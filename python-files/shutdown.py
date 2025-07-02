import subprocess
from pynput.mouse import Controller
import time
import pystray
import PIL.Image

mouse = Controller()
last_pos = mouse.position

icon = pystray.Icon("ShutDown_Auto",PIL.Image.open("C:/Users/Akhil/Desktop/icon.png"),title="ShutDown_Auto")
icon.run()

while True:
    time.sleep(30 * 60)
    if last_pos != mouse.position:
        last_pos = mouse.position
    else:
        subprocess.run(["shutdown", "/s", "/t"])
        break











