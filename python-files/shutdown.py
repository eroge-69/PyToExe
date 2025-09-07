import os
import subprocess
import ctypes
import time
os.system("shutdown/s")
VK_RETURN = 0x0D
def press_enter():
    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)     # key down
    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 2, 0)     # key up
time.sleep(0.8)
press_enter()