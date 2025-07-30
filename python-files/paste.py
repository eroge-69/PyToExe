import pyautogui

import pyperclip

import keyboard

import time

import mss

import ctypes

import threading

import sys



# Globals

start_pos = None

end_pos = None

offset_y = None

copied_lines = []

row_click_offset = 2  # Slightly below top of row to avoid resizing area



# Block/unblock user input (Windows only)

def block_input(block=True):

    try:

        ctypes.windll.user32.BlockInput(block)

    except Exception as e:

        print(f"[!] Failed to block input: {e}")



# Screenshot using mss

def take_screenshot(x, y, filename="screenshot.png", width=300, height=40):

    with mss.mss() as sct:

        monitor = {"top": y, "left": x, "width": width, "height": height}

        sct_img = sct.grab(monitor)

        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

        print(f"[📷] Screenshot saved: {filename}")



# Hotkey: Set start point

def on_set_start():

    global start_pos

    start_pos = pyautogui.position()

    take_screenshot(start_pos[0], start_pos[1], filename="start_position.png")

    print(f"[✓] Start position set at {start_pos}")



# Hotkey: Set end point

def on_set_end():

    global end_pos, offset_y

    end_pos = pyautogui.position()

    offset_y = end_pos[1] - start_pos[1]

    take_screenshot(end_pos[0], end_pos[1], filename="end_position.png")

    print(f"[✓] End position set at {end_pos}")

    print(f"[→] Calculated vertical offset: {offset_y} pixels")



# Main pasting routine

def paste_labels_and_exit():

    global copied_lines, offset_y, start_pos



    if not copied_lines:

        text = pyperclip.paste()

        copied_lines = [line.strip() for line in text.strip().split('\n') if line.strip()]



    if not start_pos or offset_y is None:

        print("[!] You must set both start and end positions first.")

        return



    print(f"[→] Starting paste of {len(copied_lines)} entries...")

    block_input(True)

    print("[🔒] Mouse input blocked.")



    try:

        for i, line in enumerate(copied_lines):

            x = start_pos[0]

            y = start_pos[1] + (offset_y * i) + row_click_offset

            pyautogui.click(x, y)

            time.sleep(0.2)

            pyperclip.copy(line)

            pyautogui.hotkey('ctrl', 'v')

            time.sleep(0.2)

        print("[✓] Finished pasting.")

    finally:

        block_input(False)

        print("[🔓] Mouse input unblocked.")

        print("👋 Exiting script.")

        sys.exit()



# Threaded start (so ESC can still be caught if needed before starting)

def start_pasting_thread():

    t = threading.Thread(target=paste_labels_and_exit, daemon=True)

    t.start()



# Instructions

print("📌 Hotkeys:")

print("• [s] - Set start position (top of first label)")

print("• [e] - Set end position (top of second label)")

print("• [F11] - Start auto-pasting and auto-exit")

print("• [esc] - Quit anytime before pasting starts")



# Hotkey bindings

keyboard.add_hotkey('s', on_set_start)

keyboard.add_hotkey('e', on_set_end)

keyboard.add_hotkey('F11', start_pasting_thread)



# Wait for exit

keyboard.wait('esc')

print("👋 Script manually exited.")

sys.exit()