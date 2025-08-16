import sys
import os
import subprocess
import threading
import time
import psutil
import keyboard
from pynput import mouse

# ------------------------------------------
# Chrome-functionaliteit
# ------------------------------------------
def find_chrome_path():
    """Zoekt een geldige Chrome-installatie op Windows."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for path in paths:
        if os.path.isfile(path):
            return path
    return None

def start_chrome_kiosk(url):
    """Start Chrome in kiosk-modus met de opgegeven URL."""
    chrome_path = find_chrome_path()
    if not chrome_path:
        raise FileNotFoundError("Chrome niet gevonden op de standaardlocaties.")
    args = [chrome_path, "--kiosk", "--no-first-run", url]
    try:
        return subprocess.Popen(args)
    except Exception as e:
        raise RuntimeError(f"Kon Chrome niet starten: {e}")

# ------------------------------------------
# Toetsen en A+S+D exit
# ------------------------------------------
def block_unwanted_keys(allowed_keys):
    """Blokkeert alle toetsaanslagen behalve de opgegeven toegestane keys."""
    def on_key_event(event):
        name = event.name
        if name and name.lower() not in allowed_keys:
            keyboard.block_key(name)
    keyboard.hook(on_key_event)

def monitor_exit_combination(duration, exit_callback):
    """
    Controleert continu of A, S en D ingedrukt zijn.
    Als ze 'duration' seconden lang samen ingedrukt blijven, wordt exit_callback uitgevoerd.
    """
    while True:
        if keyboard.is_pressed('a') and keyboard.is_pressed('s') and keyboard.is_pressed('d'):
            start = time.time()
            while time.time() - start < duration:
                if not (keyboard.is_pressed('a') and keyboard.is_pressed('s') and keyboard.is_pressed('d')):
                    break
                time.sleep(0.1)
            else:
                exit_callback()
                return
        time.sleep(0.1)

# ------------------------------------------
# Chrome afsluiten
# ------------------------------------------
def close_chrome_processes():
    """Sluit alle chrome.exe-processen af."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == "chrome.exe":
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

# ------------------------------------------
# Muisbewegingen en klikken
# ------------------------------------------
def suppress_mouse_clicks():
    """Start een mouse.Listener die muisklikken onderdrukt maar beweging toestaat."""
    def on_click(x, y, button, pressed):
        if pressed:
            listener.suppress_event()
    listener = mouse.Listener(on_click=on_click)
    listener.start()

# ------------------------------------------
# Hoofdprogramma
# ------------------------------------------
def main():
    if sys.platform != 'win32':
        print("Dit script is alleen voor Windows 10/11 bedoeld.")
        return

    url = "https://temp-caxljhkutdvdhxaqyadt.jouwweb.site/"  # Vervang dit door je gewenste URL

    # 30 seconden wachten voordat Chrome en beveiliging starten
    print("Wacht 30 seconden voordat Chrome en kioskbeveiliging starten...")
    time.sleep(30)

    try:
        chrome_proc = start_chrome_kiosk(url)
    except Exception as e:
        print(e)
        return

    # Toegestane toetsen
    allowed = {'ctrl', 'alt', 'delete'}
    block_unwanted_keys(allowed)
    suppress_mouse_clicks()

    # Callback voor exit
    def exit_action():
        close_chrome_processes()
        os._exit(0)

    # Start achtergrondthread voor A+S+D exit (5 seconden vasthouden)
    thread = threading.Thread(target=monitor_exit_combination, args=(5, exit_action), daemon=True)
    thread.start()

    # Houd het script draaiende
    keyboard.wait()

if __name__ == "__main__":
    main()
