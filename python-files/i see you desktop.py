from PIL import Image, ImageGrab, ImageDraw, ImageFont, ImageFilter
from random import randrange as rand
from tkinter import messagebox
import time
from win32gui import *
from win32api import *
from win32con import *
time = time.localtime(time.time())
msb = messagebox.showwarning(time, "I SEE YOU DESKTOP")

scr = ImageGrab.grab()  
scr.save('I SEE YOU DESKTOP.png')

font = ImageFont.truetype("arial.ttf", 20)
img = Image.open("I SEE YOU DESKTOP.png")

edit = ImageDraw.Draw(img)
x, y = img.size

for i in range(0, 100):
    edit.text((rand(x), rand(y)), "VIRUS IS START", 'red', font)

img.show()

#_______________________________________________________________________

for i in range(0, 100):
    hdc = GetDC(0)

    x = GetSystemMetrics(0)
    y = GetSystemMetrics(1)

    x_cursor, y_cursor = GetCursorPos()

    DrawIcon(hdc, x_cursor, y_cursor, LoadIcon(None, IDI_ERROR))
    StretchBlt(hdc, 20, 20, x - 40, y - 40, hdc, 0, 0, x, y, SRCCOPY)
    LineTo(hdc, rand(x), rand(y))

    Sleep(225)
