Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import messagebox
import time
import threading

# Funkcija koja "skenuje"
def start_scan():
    key = code_entry.get()

    if not key:
        messagebox.showwarning("Warning", "Unesi svoj kod prije skeniranja.")
        return

    # Onemogući dugme i prikaži poruku
    start_btn.config(state="disabled")
    status_label.config(text="🔍 Scanning in progress...")

    def scan():
        time.sleep(5)  # simulacija skeniranja
        # Ovde bi išla prava logika pretrage sistema
        result = "✅ Scan Complete: No cheats found."
... 
...         # Prikaži rezultat
...         status_label.config(text=result)
...         start_btn.config(state="normal")
... 
...     threading.Thread(target=scan).start()
... 
... # Glavni prozor
... root = tk.Tk()
... root.title("OVERWATCH SCANNER")
... root.geometry("500x400")
... root.configure(bg="black")
... 
... # Gradient hack (fake plavi donji dio)
... gradient = tk.Frame(root, bg="#0000FF", height=100)
... gradient.pack(side="bottom", fill="x")
... 
... # Naslov
... title = tk.Label(root, text="OVERWATCH SCANNER", fg="#0000FF", bg="black", font=("Courier", 20, "bold"))
... title.pack(pady=40)
... 
... # Input za kod
... code_entry = tk.Entry(root, font=("Courier", 14), justify="center", width=30)
... code_entry.pack(pady=10)
... code_entry.insert(0, "Unesi svoj kod ovdje")
... 
... # Dugme
... start_btn = tk.Button(root, text="START SCANNING", font=("Courier", 14), bg="#0000FF", fg="black", command=start_scan)
... start_btn.pack(pady=20)
... 
... # Status poruka
... status_label = tk.Label(root, text="", fg="white", bg="black", font=("Courier", 12))
... status_label.pack(pady=10)
... 
... # Startaj GUI
... root.mainloop()
