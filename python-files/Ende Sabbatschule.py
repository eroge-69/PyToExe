
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import threading
import time
from datetime import datetime

# Funktion zum Abspielen der MP3-Datei
def play_music(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# Funktion, die auf die eingestellte Uhrzeit wartet
def wait_for_alarm(alarm_time, file_path):
    while True:
        now = datetime.now().strftime('%H:%M')
        if now == alarm_time:
            play_music(file_path)
            break
        time.sleep(10)

# Funktion, die beim Klick auf "Start" ausgeführt wird
def start_alarm():
    alarm_time = time_entry.get()
    file_path = file_path_var.get()
    if not alarm_time or not file_path:
        messagebox.showerror("Fehler", "Bitte Uhrzeit und MP3-Datei angeben.")
        return
    threading.Thread(target=wait_for_alarm, args=(alarm_time, file_path), daemon=True).start()
    messagebox.showinfo("Wecker aktiviert", f"MP3 wird um {alarm_time} abgespielt.")

# Funktion zum Auswählen der MP3-Datei
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 Dateien", "*.mp3")])
    if file_path:
        file_path_var.set(file_path)

# GUI erstellen
root = tk.Tk()
root.title("Ende Sabbatschule")

tk.Label(root, text="Uhrzeit (HH:MM):").grid(row=0, column=0, padx=10, pady=10)
time_entry = tk.Entry(root)
time_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="MP3-Datei:").grid(row=1, column=0, padx=10, pady=10)
file_path_var = tk.StringVar()
file_entry = tk.Entry(root, textvariable=file_path_var, width=40)
file_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Durchsuchen", command=browse_file).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="Start", command=start_alarm).grid(row=2, column=1, pady=20)

root.mainloop()
