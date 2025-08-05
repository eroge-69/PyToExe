
import pyautogui
import psutil
import pygetwindow as gw
from PIL import ImageGrab
import threading
import time
import tkinter as tk
import win32gui

# RGB alvo (retângulo vermelho do HUD)
TARGET_COLOR = (124, 40, 35)
COLOR_TOLERANCE = 30  # tolerância de cor
AUTOCLICK_ENABLED = False

def is_fivem_active():
    for proc in psutil.process_iter(['name']):
        if "FiveM" in proc.info['name']:
            active_window = gw.getActiveWindow()
            if active_window and "FiveM" in active_window.title:
                return True
    return False

def color_matches(color1, color2, tolerance):
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

def detect_and_press_e():
    global AUTOCLICK_ENABLED
    while True:
        if AUTOCLICK_ENABLED and is_fivem_active():
            screenshot = ImageGrab.grab()
            width, height = screenshot.size
            center_x = width // 2
            bottom_y = int(height * 0.85)

            region = (center_x - 50, bottom_y - 10, center_x + 50, bottom_y + 10)
            cropped = screenshot.crop(region)

            for x in range(cropped.width):
                for y in range(cropped.height):
                    pixel = cropped.getpixel((x, y))
                    if color_matches(pixel, TARGET_COLOR, COLOR_TOLERANCE):
                        pyautogui.press('e')
                        time.sleep(0.3)
                        break
        time.sleep(0.1)

def toggle_autoclick():
    global AUTOCLICK_ENABLED
    AUTOCLICK_ENABLED = not AUTOCLICK_ENABLED
    status_label.config(text=f"AUTOMÁTICO: {'ATIVO' if AUTOCLICK_ENABLED else 'DESATIVADO'}")

def on_keypress(event):
    if event.keysym == 'F2':
        toggle_autoclick()

def create_gui():
    global status_label
    root = tk.Tk()
    root.title("AutoClicker FiveM")
    root.attributes("-topmost", True)
    root.geometry("220x60")
    root.resizable(False, False)

    status_label = tk.Label(root, text="AUTOMÁTICO: DESATIVADO", font=("Arial", 10))
    status_label.pack(pady=10)

    root.bind("<KeyPress>", on_keypress)
    root.mainloop()

threading.Thread(target=detect_and_press_e, daemon=True).start()
create_gui()
