import os
import time
import re
import shutil
import pyperclip
import pyautogui
import keyboard
import threading

try:
    from pyfiglet import Figlet
except ImportError:
    Figlet = None

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS = [Fore.RED, Fore.BLUE, Fore.MAGENTA, Fore.GREEN]
except ImportError:
    COLORS = [""] * 4

def splash_screen():
    width, height = shutil.get_terminal_size()
    interval = 3.0 / len(COLORS)
    if Figlet:
        f = Figlet(font='slant')
        text = f.renderText("sosarar").splitlines()
    else:
        text = ["sosarar"]
    blank_lines = max((height - len(text)) // 2, 0)
    for color in COLORS:
        os.system('cls' if os.name == 'nt' else 'clear')
        for _ in range(blank_lines):
            print()
        for line in text:
            print(color + line.center(width))
        time.sleep(interval)
    os.system('cls' if os.name == 'nt' else 'clear')

def record_pos(prompt: str):
    print(prompt)
    keyboard.wait('enter')
    pos = pyautogui.position()
    print(f" → Recorded at {pos}\n")
    return pos

def set_positions():
    tb_pos = record_pos("Position your mouse on the Textbox (JOB ID INPUT) and press ENTER…")
    taskbar_pos = record_pos("Position on your taskbar and press ENTER…")
    btn_pos = record_pos("Position on 'Join Job-ID' and press ENTER…")
    print("\n[READY] Monitoring clipboard for 48-character entries.\n")
    return tb_pos, taskbar_pos, btn_pos

def run_loader(tb_pos, taskbar_pos, btn_pos, clip_text):
    print(f"[📋] Found: {clip_text}\n[→] Joining...")
    pyautogui.moveTo(tb_pos)
    pyautogui.click(clicks=2, interval=0)
    pyperclip.copy(clip_text)  # ensure it's on clipboard
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.moveTo(taskbar_pos)
    pyautogui.click()
    pyautogui.moveTo(btn_pos)
    pyautogui.click(clicks=2, interval=0)

def position_watcher(reset_flag):
    while True:
        user_input = input("Type 1 and press ENTER to reset/reposition mouse points: ").strip()
        if user_input == "1":
            reset_flag.set()

def main():
    splash_screen()
    reset_flag = threading.Event()
    tb_pos, taskbar_pos, btn_pos = set_positions()
    recent_clip = pyperclip.paste().strip()

    watcher_thread = threading.Thread(target=position_watcher, args=(reset_flag,), daemon=True)
    watcher_thread.start()

    print("[WAITING] Copy a 48-character string to trigger...")
    while True:
        if reset_flag.is_set():
            tb_pos, taskbar_pos, btn_pos = set_positions()
            reset_flag.clear()
            recent_clip = pyperclip.paste().strip()
            print("[WAITING] Copy a 48-character string to trigger...")

        clip = pyperclip.paste().strip()
        if clip != recent_clip and len(clip) == 48:
            recent_clip = clip
            run_loader(tb_pos, taskbar_pos, btn_pos, clip)

        time.sleep(0.000000000000000000000000000000000000000000000001)

if __name__ == '__main__':
    main()