import random
from win32process import REALTIME_PRIORITY_CLASS
import time
import winsound
import keyboard
import pyautogui
from pynput.mouse import Listener, Button
import os
from ctypes import *
import platform

version = "JXXY"

# =================== KEYBINDS ===================
kill_script_keybind = "f9"                       # PANIC KEY (kills the script)
toggle_running_keybind = "f1"               # TASTE AN/AUS
change_pixel_color_keybind = "f10"          # WECHSEL PIXEL COLOR

# ================== UTILITIES ===================
user = windll.LoadLibrary("user32.dll")     # User32.dll
dc = user.GetDC(0)                          # Device context
gdi = windll.LoadLibrary("gdi32.dll")       # Graphics Device Interface

running = True                              # Running state
alive = True                                # Alive state
right_mouse_pressed = False                 # Right mouse button pressed state

def resize_terminal():
    if platform.system() == "Windows":
        os.system("mode con cols=60 lines=20")  # Größe angepasst für ASCII-Header

def print_header():
    os.system('cls')
    print("╔════════════════════════════════════════════════════╗")
    print("║             ██╗██╗  ██╗██╗  ██╗██╗   ██╗           ║")
    print("║             ██║╚██╗██╔╝╚██╗██╔╝╚██╗ ██╔╝           ║")
    print("║             ██║ ╚███╔╝  ╚███╔╝  ╚████╔╝            ║")
    print("║        ██   ██║ ██╔██╗  ██╔██╗   ╚██╔╝             ║")
    print("║        ╚█████╔╝██╔╝ ██╗██╔╝ ██╗   ██║              ║")
    print("║         ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝              ║")
    print("╠════════════════════════════════════════════════════╣")
    print("╠════════════════════════════════════════════════════╣")
    print(f"║ {kill_script_keybind.upper():<15} - PANIC KEY{' ' * 25}║")
    print(f"║ {toggle_running_keybind.upper():<15} - TOGGLE ON/OFF{' ' * 18}║")
    print(f"║ {change_pixel_color_keybind.upper():<15} - UPDATE PIXEL COLOR{' ' * 11}║")
    print("╚════════════════════════════════════════════════════╝")

def kill_script():
    global alive
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    alive = not alive

def toggle_running():
    global running
    running = not running
    if running:
        pass
    else:
        winsound.PlaySound("SystemExit", winsound.SND_ASYNC)

# ==================== MOUSE LISTENER ====================
def on_click(x, y, button, pressed):
    global right_mouse_pressed
    if button == Button.right:
        right_mouse_pressed = pressed 

mouse_listener = Listener(on_click=on_click)
mouse_listener.start()

# ================ PIXEL COLOR DETECTION =================
x = user.GetSystemMetrics(0) // 2 
y = user.GetSystemMetrics(1) // 2
search_color = 5197761 # Anfangsfarbe

def get_pixel():
    return gdi.GetPixel(dc, x, y)

def check():
    global search_color
    if get_pixel() == search_color:
        pyautogui.mouseDown()
        time.sleep(random.uniform(0.06, 0.2))
        pyautogui.mouseUp()

def change_pixel_color():
    global search_color
    search_color = get_pixel()

# ================= SET PRIORITY ===================
kernel32 = windll.kernel32
pid = os.getpid()
handle = kernel32.OpenProcess(0x1F0FFF, False, pid)
kernel32.SetPriorityClass(handle, REALTIME_PRIORITY_CLASS)
kernel32.CloseHandle(handle)

# ==================== MAIN LOOP ===================
keyboard.add_hotkey(toggle_running_keybind, toggle_running)
keyboard.add_hotkey(kill_script_keybind, kill_script)
keyboard.add_hotkey(change_pixel_color_keybind, change_pixel_color)

resize_terminal()
print_header()

while alive:
    # Optional: Fenstergröße prüfen (du kannst das auch rausnehmen, wenn du willst)
    if platform.system() == "Windows":
        if os.get_terminal_size().columns != 60 or os.get_terminal_size().lines != 20:
            resize_terminal()
            print_header()

    while running and right_mouse_pressed:
        check()
    time.sleep(0.001)

# Stoppe den Mouse Listener
mouse_listener.stop()
mouse_listener.join()
