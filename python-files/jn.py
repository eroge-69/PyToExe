import time
import ctypes
import sys

# Hide the console cursor
kernel32 = ctypes.windll.kernel32
class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_int), ("bVisible", ctypes.c_bool)]

cursor = CONSOLE_CURSOR_INFO()
kernel32.GetConsoleCursorInfo(kernel32.GetStdHandle(-11), ctypes.byref(cursor))
cursor.bVisible = False
kernel32.SetConsoleCursorInfo(kernel32.GetStdHandle(-11), ctypes.byref(cursor))

# Keep the window open indefinitely
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    sys.exit()
