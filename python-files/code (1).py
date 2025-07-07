import os
import sys
import time
import threading
import mss
import psutil
from pynput.mouse import Button, Controller, Listener
from pynput import keyboard

# Globale Variablen
mouse = Controller()
right_pressed = False
panic_triggered = False

# Rechte Maustaste verfolgen
def on_click(x, y, button, pressed):
    global right_pressed
    if button == Button.right:
        right_pressed = pressed

# F12 drücken = Selbstzerstörung aktivieren
def on_key_press(key):
    global panic_triggered
    if key == keyboard.Key.f12:
        panic_triggered = True
        print('\x1b[31mPANIK-MODUS AKTIVIERT – Datei wird gelöscht!\x1b[0m')
        file_path = os.path.realpath(__file__)
        threading.Thread(target=delete_self_and_exit, args=(file_path,)).start()

# Selbstlöschung
def delete_self_and_exit(path):
    time.sleep(0.5)
    try:
        os.remove(path)
        print("Datei wurde gelöscht.")
        sys.exit()
    except Exception as e:
        print(f"Fehler beim Löschen: {e}")
        sys.exit(1)

# FiveM läuft?
def is_fivem_running(process_name='FiveM.exe'):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

# Farberkennung (für rot)
def is_red(r, g, b, target=(185, 76, 77), tolerance=10):
    return (
        abs(r - target[0]) <= tolerance and
        abs(g - target[1]) <= tolerance and
        abs(b - target[2]) <= tolerance
    )

# ASCII-Art & Start-Text
print('\x1b[35m \n     \n██████╗ ██████╗ ██████╗ \n╚════██╗╚════██╗╚════██╗\n  ▄███╔╝  ▄███╔╝  ▄███╔╝\n  ▀▀══╝   ▀▀══╝   ▀▀══╝ \n  ██╗     ██╗     ██╗   \n  ╚═╝     ╚═╝     ╚═╝\n\x1b[0m')
print('\x1b[35mMADE BY MR. ANONYM / MR.X\x1b[0m')
print('\x1b[35mF für DIENSTE ANSCHALTEN\x1b[0m')

# Listener starten
Listener(on_click=on_click).start()
keyboard.Listener(on_press=on_key_press).start()

# Warten auf FiveM
if not is_fivem_running():
    print("FiveM nicht gefunden. Script beendet sich.")
    sys.exit()

time.sleep(6)
print('\x1b[35mDIENSTE WURDEN ANGESCHALTET\x1b[0m')
time.sleep(2)

# Bildschirmüberwachung starten
with mss.mss() as sct:
    monitor = sct.monitors[1]
    screen_width = monitor['width']
    screen_height = monitor['height']
    center_x = screen_width // 2
    center_y = screen_height // 2
    region = {'top': center_y, 'left': center_x, 'width': 1, 'height': 1}

    while not panic_triggered:
        img = sct.grab(region)
        r, g, b = img.pixel(0, 0)
        if is_red(r, g, b):
            print("Roter Pixel erkannt in der Bildschirmmitte!")
        time.sleep(0.5)
