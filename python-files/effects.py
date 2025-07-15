 import win32api 
import win32gui 
import win32ui 
import win32con 
import ctypes 
import math 
from random import * 
import random 
from time import sleep 
user32 = ctypes.windll.user32 
user32.SetProcessDPIAware() 
[sw, sh] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]  
desktop = win32gui.GetDesktopWindow() 
hdc = win32gui.GetDC(0) 
user32 = ctypes.windll.user32 
user32.SetProcessDPIAware() 
[w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)] 
hdc = win32gui.GetWindowDC(desktop) 
sw = win32api.GetSystemMetrics(0) 
sh = win32api.GetSystemMetrics(1) 
desk = win32gui.GetDC(0) 
desc = win32gui.GetDC(0) 
xx = win32api.GetSystemMetrics(0) 
yy = win32api.GetSystemMetrics(1) 
user32 = ctypes.windll.user32 
user32.SetProcessDPIAware() 
[sw, sh] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]  
hdc = win32gui.GetDC(0) 
dx = dy = 1 
angle = 0 
size = 1 
speed = 40 
sleep(1) 
while True: 
    hdc = win32gui.GetDC(0) 
    color = (random.randint(0, 122), random.randint(0, 430), random.randint(0, 310)) 
    brush = win32gui.CreateSolidBrush(win32api.RGB(*color)) 
    win32gui.SelectObject(hdc, brush) 
    win32gui.BitBlt(hdc, random.randint(-10, 10), random.randint(-10, 10), sw, sh, hdc, 0, 0, win32con.SRCCOPY) 
    win32gui.BitBlt(hdc, random.randint(-10, 10), random.randint(-10, 10), sw, sh, hdc, 0, 0, win32con.PATINVERT) 
    x = y = 0 
    win32gui.DrawIcon(hdc, x , y , win32gui.LoadIcon(None, win32con.IDI_ERROR)) # Change IDI_ERROR to something else to change the icon being displayed 
    x = x + 30 
    if x >= w: 
        y = y + 30 
        x = 0 
    if y >= h: 
        x = y = 0 
    brush = win32gui.CreateSolidBrush(win32api.RGB( 
        randrange(255), 
        randrange(255), 
        randrange(255), 
        )) 
    win32gui.SelectObject(desc, brush) 
    win32gui.PatBlt(desc, randrange(xx), randrange(yy), randrange(xx), randrange(yy), win32con.PATINVERT) 
    win32gui.DeleteObject(brush) 
    sleep(0.01) 
    text = "твой пк как котлета)" 
    size = size + 1 
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, dx, dy, win32con.SRCCOPY) 
    dx = math.ceil(math.sin(angle) * size * 10) 
    dy = math.ceil(math.cos(angle) * size * 10) 
    angle += speed / 10 
    win32gui.DrawText(desk, text, len(text), (randrange(xx), randrange(yy), randrange(xx), randrange(yy)), win32con.DT_LEFT) 
    win32gui.DrawText(desk, text, len(text), (randrange(xx), randrange(yy), randrange(xx), randrange(yy)), win32con.DT_LEFT) 
    if angle > math.pi : 
        angle = math.pi * -1 
 