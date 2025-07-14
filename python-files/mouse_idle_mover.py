
import pyautogui
import time
import random
import ctypes

def get_idle_duration():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

def move_mouse_randomly_if_idle(threshold_seconds=(180, 300)):
    while True:
        idle_time = get_idle_duration()
        if idle_time >= random.randint(*threshold_seconds):
            x, y = pyautogui.position()
            dx = random.randint(-30, 30)
            dy = random.randint(-30, 30)
            pyautogui.moveTo(x + dx, y + dy, duration=0.5)
        time.sleep(15)

if __name__ == "__main__":
    move_mouse_randomly_if_idle()
