import os
import subprocess
import time
import pyautogui
import tkinter as tk
from tkinter import messagebox

VOLGORDE_BESTAND = "volgorde.txt"
INDEX_BESTAND = "laatste_index.txt"

def laad_volgorde():
    with open(VOLGORDE_BESTAND, "r", encoding="utf-8") as f:
        return [regel.strip() for regel in f if regel.strip().endswith(".reason")]

def laad_index():
    if os.path.exists(INDEX_BESTAND):
        with open(INDEX_BESTAND, "r") as f:
            return int(f.read().strip())
    return 0

def sla_index_op(i):
    with open(INDEX_BESTAND, "w") as f:
        f.write(str(i))

def sluit_huidig_project():
    pyautogui.hotkey("ctrl", "w")
    time.sleep(1)
    pyautogui.press("n")

def open_volgende():
    lijst = laad_volgorde()
    if not lijst:
        messagebox.showerror("Fout", "volgorde.txt is leeg of ontbreekt.")
        return

    index = laad_index()
    bestand = lijst[index % len(lijst)]

    sluit_huidig_project()
    time.sleep(2)
    subprocess.Popen(['start', '', bestand], shell=True)

    sla_index_op(index + 1)

root = tk.Tk()
root.title("Reason Song Loader")
root.geometry("360x120")
root.resizable(False, False)

knop = tk.Button(root, text="Volgende Reason-bestand", command=open_volgende, font=("Arial", 12))
knop.pack(pady=30)

root.mainloop()
