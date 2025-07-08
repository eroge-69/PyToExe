import mss
import time
import psutil
from pynput.mouse import Button, Controller, Listener
from pynput import keyboard

mouse = Controller()
right_pressed = False
trigger_enabled = True  # Startzustand: aktiv
DEBUG = False  # Wenn True, zeigt aktuelle RGB-Werte an

# Farbe für Ziel (z. B. rot) & Toleranz
TARGET_COLOR = (185, 76, 77)
COLOR_TOLERANCE = 10

def on_click(x, y, button, pressed):
    global right_pressed
    if button == Button.right:
        right_pressed = pressed

def on_key_press(key):
    global trigger_enabled
    try:
        if key == keyboard.Key.f6:
            trigger_enabled = not trigger_enabled
            status = "Aktiviert" if trigger_enabled else "Deaktiviert"
            print(f"\033[33m[Triggerbot {status}]\033[0m")
    except:
        pass

# Listener starten
Listener(on_click=on_click).start()
keyboard.Listener(on_press=on_key_press).start()

def is_fivem_running(process_name="FiveM.exe"):
    return any(proc.info['name'] == process_name for proc in psutil.process_iter(['name']))

def is_target_color(r, g, b, target=TARGET_COLOR, tolerance=COLOR_TOLERANCE):
    return all(abs(c - t) <= tolerance for c, t in zip((r, g, b), target))

def wait_for_fivem():
    print("\033[34mby Ole   |   Last Update 20.04.2025\033[0m\n")
    print("\033[34mÖffne FiveM...\033[0m")
    while not is_fivem_running():
        time.sleep(1)
    print("\033[34mFiveM gefunden! Triggerbot gestartet...\033[0m")
    time.sleep(2)

def trigger_loop():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        region = {
            "top": monitor["height"] // 2,
            "left": monitor["width"] // 2,
            "width": 1,
            "height": 1
        }

        while True:
            if right_pressed and trigger_enabled:
                pixel = sct.grab(region).pixel(0, 0)
                r, g, b = pixel[:3]

                if DEBUG:
                    print(f"Pixel: R={r}, G={g}, B={b}")

                if is_target_color(r, g, b):
                    # Kein Konsolenausgabe hier
                    mouse.press(Button.left)
                    time.sleep(0.02)
                    mouse.release(Button.left)
                    time.sleep(0.13)
                else:
                    time.sleep(0.005)
            else:
                time.sleep(0.005)

if __name__ == "__main__":
    wait_for_fivem()
    trigger_loop()

