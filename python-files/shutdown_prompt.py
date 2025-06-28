import tkinter as tk
from tkinter import messagebox
import os
import threading

def shutdown():
    os.system("shutdown /s /t 0")

def on_timeout():
    if not response_received[0]:
        root.after(100, root.destroy)
        shutdown()

def ask_shutdown():
    response = messagebox.askquestion("Herunterfahren", "Computer wirklich herunterfahren?")
    response_received[0] = True
    if response == "yes":
        shutdown()
    else:
        root.destroy()

# Setup
root = tk.Tk()
root.withdraw()  # Versteckt das Hauptfenster

response_received = [False]

# Timer starten (10 Sekunden)
timer = threading.Timer(10.0, on_timeout)
timer.start()

# Frage anzeigen
root.after(100, ask_shutdown)
root.mainloop()
