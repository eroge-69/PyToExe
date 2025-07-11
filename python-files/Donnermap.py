import os
import pyautogui
import pygetwindow as gw
from pynput import keyboard
from datetime import datetime
from PIL import ImageGrab

# 🔧 Speicherort hier anpassen:
screenshot_dir = "C:/Users/DeinBenutzername/Desktop/Screenshots"  # z. B. anpassen

# Verzeichnis erstellen, falls nicht vorhanden
os.makedirs(screenshot_dir, exist_ok=True)

# Zustand um zwischen Screenshot und Ignorieren zu wechseln
screenshot_toggle = True

def capture_active_window():
    active_window = gw.getActiveWindow()
    if active_window is None:
        print("Kein aktives Fenster erkannt.")
        return

    box = (active_window.left, active_window.top,
           active_window.left + active_window.width,
           active_window.top + active_window.height)

    screenshot = ImageGrab.grab(bbox=box)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
    screenshot.save(filename)
    print(f"✅ Screenshot gespeichert: {filename}")

def on_press(key):
    global screenshot_toggle
    try:
        if key.char.lower() == 'm':
            if screenshot_toggle:
                capture_active_window()
            else:
                print("⏸️ Screenshot ignoriert (zweiter Tastendruck).")
            screenshot_toggle = not screenshot_toggle
    except AttributeError:
        # ESC zum Beenden
        if key == keyboard.Key.esc:
            print("🚪 Beenden...")
            return False  # Stop Listener

# Listener starten
print("🎯 Drücke 'm' für Screenshot (abwechselnd aktiv), 'ESC' zum Beenden.")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
