import os
import subprocess
import time
import ctypes
 
image_path = "Käse.jpg"
 
HAT_KEY = 0xC0  

def is_hat_key_pressed():
    return ctypes.windll.user32.GetAsyncKeyState(HAT_KEY) & 0x8000

def open_image():
    if not os.path.exists(image_path):
        print(f"Fehler: {image_path} nicht gefunden!")
        return None
    return subprocess.Popen(["mspaint", image_path])

processes = [open_image()]

screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height = ctypes.windll.user32.GetSystemMetrics(1)

x=True
while x:
    time.sleep(0.1)
    
    if is_hat_key_pressed():
        print("^-Taste erkannt! Programm beendet.")
        x=False
        break  
 
    new_processes = []
    for p in processes[:]:
        if p.poll() is not None:
            print("Bild geschlossen! Öffne 2 neue...")
            new_processes.append(open_image())
            new_processes.append(open_image())
            processes.remove(p)
 
    processes.extend(new_processes)