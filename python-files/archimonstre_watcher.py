import tkinter as tk
from tkinter import ttk
import pyperclip
import threading
import time
import math
import re

# ----------------------
# Config
# ----------------------
CHECK_INTERVAL = 0.5  # seconds
CLEAR_CLIPBOARD = False

# ----------------------
# Zaaps List
# ----------------------
ZAAPS = [
    {"Name":"Village des Éleveurs","X":-16,"Y":1},
    {"Name":"Village des Dopeuls","X":-34,"Y":-8},
    {"Name":"Village de la Canopée","X":-54,"Y":16},
    {"Name":"Village d’Amakna","X":-2,"Y":0},
    {"Name":"Village côtier","X":-46,"Y":18},
    {"Name":"Tainéla","X":1,"Y":-32},
    {"Name":"Sufokia","X":13,"Y":26},
    {"Name":"Routes Rocailleuses","X":-20,"Y":-20},
    {"Name":"Amakna Château","X":3,"Y":-5},
    {"Name":"Amakna Village","X":-2,"Y":0},
    {"Name":"Montagne des Cracklers","X":-5,"Y":-8},
    {"Name":"Coin des Bouftous","X":5,"Y":7},
    {"Name":"Port de Madrestam","X":7,"Y":-4},
    {"Name":"Plaine des Scarafeuilles","X":-1,"Y":24},
    {"Name":"Astrub","X":5,"Y":-18},
    {"Name":"Bonta","X":-32,"Y":-56},
    {"Name":"Brakmar","X":-26,"Y":35},
    {"Name":"Plaines de Cania Lac","X":-3,"Y":-42},
    {"Name":"Plaines de Cania Massif","X":-13,"Y":-28},
    {"Name":"Plaines de Cania Village Imps","X":-16,"Y":-24},
    {"Name":"Plaines de Cania Village Kanigs","X":0,"Y":-56},
    {"Name":"Île de Frigost Château","X":-67,"Y":-75},
    {"Name":"Île de Frigost Village","X":-78,"Y":-41},
    {"Name":"Île de Moon Plage","X":35,"Y":12},
    {"Name":"Île d'Otomai Village Canopée","X":-54,"Y":16},
    {"Name":"Île d'Otomai Village Côtier","X":-46,"Y":18},
    {"Name":"Île de Pandala Village","X":20,"Y":-29},
    {"Name":"Marais de Sidimote Allée","X":-25,"Y":12},
    {"Name":"Marais de Sidimote Hauts-Plateaux","X":-15,"Y":25},
    {"Name":"Baie de Sufokia Temple","X":13,"Y":35},
    {"Name":"Baie de Sufokia Rivage","X":10,"Y":22},
    {"Name":"Foire aux Trools","X":-11,"Y":-36},
    {"Name":"Îles Wabbit Laboratoire","X":27,"Y":-14},
    {"Name":"Îles Wabbit Île des Cawwots","X":25,"Y":-4},
    {"Name":"Village des Zoths","X":-53,"Y":18}
]

# ----------------------
# Functions
# ----------------------
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def find_nearest_zaap(x, y):
    nearest = None
    min_dist = float('inf')
    for z in ZAAPS:
        dist = distance(x, y, z['X'], z['Y'])
        if dist < min_dist:
            min_dist = dist
            nearest = z
    return nearest, min_dist

# ----------------------
# GUI Setup
# ----------------------
root = tk.Tk()
root.title("Archimonstre GPS")
root.geometry("320x140")
root.attributes("-topmost", True)
root.configure(bg="black")
root.resizable(False, False)

lbl_coords = tk.Label(root, text="Archimonstre: N/A", font=("Courier", 14), fg="cyan", bg="black")
lbl_coords.pack(pady=5)
lbl_zaap = tk.Label(root, text="Nearest Zaap: N/A", font=("Courier", 14), fg="lightgreen", bg="black")
lbl_zaap.pack(pady=5)
lbl_dist = tk.Label(root, text="Distance: N/A", font=("Courier", 12), fg="yellow", bg="black")
lbl_dist.pack(pady=5)

# ----------------------
# Clipboard Monitoring Thread
# ----------------------
def clipboard_loop():
    last_clipboard = ""
    log("Archimonstre Zaap Watcher running with overlay...")
    log("Copy '/travel X,Y' or '/travel X Y' to detect nearest Zaap.")

    while True:
        try:
            clip = pyperclip.paste()
        except:
            clip = ""
        if clip != last_clipboard and clip.strip() != "":
            last_clipboard = clip
            match = re.search(r"/travel\s*(-?\d+)[, ]\s*(-?\d+)", clip)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                nearest, dist = find_nearest_zaap(x, y)
                log(f"Archimonstre at ({x},{y}) | Nearest Zaap: {nearest['Name']} ({nearest['X']},{nearest['Y']}) | Distance: {dist:.1f}")

                # Update GUI
                lbl_coords.config(text=f"Archimonstre: ({x},{y})")
                lbl_zaap.config(text=f"Nearest Zaap: {nearest['Name']} ({nearest['X']},{nearest['Y']})")
                lbl_dist.config(text=f"Distance: {dist:.1f}")

                if CLEAR_CLIPBOARD:
                    pyperclip.copy("")

        time.sleep(CHECK_INTERVAL)

# Run clipboard monitor in a separate thread
threading.Thread(target=clipboard_loop, daemon=True).start()

# Start GUI
root.mainloop()
