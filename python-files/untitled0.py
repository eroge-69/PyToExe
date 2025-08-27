# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:36:41 2023

@author: parmars
"""

import win32api, time, random, win32con, os, datetime

while(1):
    a = random.randint(200,820)
    b = random.randint(400,780)
    c = random.randint(2,61)
    now = datetime.datetime.now()
    hb = now.replace(hour=17, minute=(12), second=6, microsecond=0)
    if now > hb:
       os.system("shutdown.exe /h")
    print(str(now.strftime("%H:%M:%S"))+' - ('+str(a)+', '+str(b)+')')
    win32api.SetCursorPos((a,b))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,a,b,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,a,b,0,0)
    time.sleep(c)
