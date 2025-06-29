
import tkinter as tk
from tkinter import messagebox
import time
import os
import threading

def shutdown_pc():
    os.system("shutdown /s /t 0")

def start_timer():
    try:
        seconds = int(entry.get())
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben!")
        return

    start_button.config(state="disabled")
    countdown_thread = threading.Thread(target=countdown, args=(seconds,))
    countdown_thread.start()

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        timer_label.config(text=f"Verbleibende Zeit: {remaining} Sekunden")
        time.sleep(1)
    timer_label.config(text="Zeit abgelaufen! PC wird heruntergefahren...")
    shutdown_pc()

root = tk.Tk()
root.title("Shutdown Timer")
root.geometry("300x150")

tk.Label(root, text="Zeit bis Shutdown (in Sekunden):").pack(pady=10)
entry = tk.Entry(root)
entry.pack()

start_button = tk.Button(root, text="Start", command=start_timer)
start_button.pack(pady=10)

timer_label = tk.Label(root, text="")
timer_label.pack()

root.mainloop()
