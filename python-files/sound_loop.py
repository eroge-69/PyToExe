
import pygame
import time
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

# Sound abspielen
def play_sound_loop():
    while not stop_flag.is_set():
        pygame.mixer.music.play()
        time.sleep(20)

# Passwortabfrage beim Beenden
def on_close():
    password = simpledialog.askstring("Passwort", "Zum Beenden bitte Passwort eingeben:", show='*')
    if password == "1121":
        stop_flag.set()
        root.destroy()
    else:
        messagebox.showerror("Fehler", "Falsches Passwort!")

# Setup
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("discord-spam.mp3")

stop_flag = threading.Event()
threading.Thread(target=play_sound_loop, daemon=True).start()

# Minimales GUI zur Passwortabfrage
root = tk.Tk()
root.title("Sound läuft...")
root.protocol("WM_DELETE_WINDOW", on_close)
root.geometry("250x80")
tk.Label(root, text="Sound läuft im Hintergrund.").pack(pady=10)
root.withdraw()  # Start minimiert
root.after(1000, root.deiconify)  # Nach 1 Sekunde sichtbar machen (für Passwortdialog)
root.mainloop()
