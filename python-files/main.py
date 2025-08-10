import tkinter as tk
import pyautogui
import keyboard
import threading
import math
import time

running = False
radius = 50
center_x, center_y = 0, 0

def circle_move():
    global running, center_x, center_y, radius
    angle = 0
    while running:
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        pyautogui.moveTo(int(x), int(y))
        angle += 0.1
        if angle >= 2 * math.pi:
            angle = 0
        time.sleep(0.01)

def toggle_circle():
    global running, center_x, center_y
    if not running:
        center_x, center_y = pyautogui.position()
        running = True
        threading.Thread(target=circle_move, daemon=True).start()
    else:
        running = False

def set_small_radius():
    global radius
    radius = 50
    lbl_radius.config(text=f"Aktueller Radius: {radius}")

def set_large_radius():
    global radius
    radius = 150
    lbl_radius.config(text=f"Aktueller Radius: {radius}")

# Hotkeys
keyboard.add_hotkey("F4", toggle_circle)
keyboard.add_hotkey("F9", set_small_radius)
keyboard.add_hotkey("F10", set_large_radius)

# GUI
root = tk.Tk()
root.title("Mauskreis Controller")

btn_toggle = tk.Button(root, text="Start/Stop (F4)", command=toggle_circle)
btn_toggle.pack(pady=5)

btn_small = tk.Button(root, text="Kleiner Radius (F9)", command=set_small_radius)
btn_small.pack(pady=5)

btn_large = tk.Button(root, text="Großer Radius (F10)", command=set_large_radius)
btn_large.pack(pady=5)

lbl_radius = tk.Label(root, text=f"Aktueller Radius: {radius}")
lbl_radius.pack(pady=5)

root.mainloop()
