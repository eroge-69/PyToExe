import win32api 
import win32con 
import win32gui 
import math 
from random import * 
import random 
import time 
 
def sines(): 
    desktop = win32gui.GetDesktopWindow() 
    hdc = win32gui.GetWindowDC(desktop) 
    sw = win32api.GetSystemMetrics(0) 
    sh = win32api.GetSystemMetrics(1) 
    angle = 0
    desktop = win32gui.GetDesktopWindow() 
    hdc = win32gui.GetWindowDC(desktop) 
    sw = win32api.GetSystemMetrics(0) 
    sh = win32api.GetSystemMetrics(1) 
    angle = 90

    desktop = win32gui.GetDesktopWindow() 
    hdc = win32gui.GetWindowDC(desktop) 
    sw = win32api.GetSystemMetrics(0) 
    sh = win32api.GetSystemMetrics(1) 
    angle = 180
     desktop = win32gui.GetDesktopWindow() 
    hdc = win32gui.GetWindowDC(desktop) 
    sw = win32api.GetSystemMetrics(0) 
    sh = win32api.GetSystemMetrics(1) 
    angle = 270 
 
    while True: 
        hdc = win32gui.GetWindowDC(desktop) 
        for i in range(int(sw + sh)): 
            a = int(math.sin(angle) * randrange(9999)) 
            win32gui.BitBlt(hdc, randrange(999), i, sw, randrange(999), hdc, 0, i, win32con.SRCCOPY) 
            angle += math.pi / random.randint(10, 9999) 
        win32gui.ReleaseDC(desktop, hdc) 
        time.sleep(0.01) 
 
if __name__ == '__main__': 
    sines() 
 
