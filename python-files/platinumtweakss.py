import tkinter as tk
from tkinter import ttk
import psutil

# Hlavní okno
root = tk.Tk()
root.title("Platinum Tweaks")
root.geometry("900x500")  # velikost okna

# Levá lišta
sidebar = tk.Frame(root, bg="#2c3e50", width=150)
sidebar.pack(side="left", fill="y")

categories = ["Dashboard", "Tweaks", "Cleaner", "Apps"]
for cat in categories:
    btn = tk.Button(sidebar, text=cat, fg="white", bg="#34495e", relief="flat", pady=10)
    btn.pack(fill="x", padx=10, pady=5)

# Střední část - Dashboard
dashboard = tk.Frame(root, bg="#ecf0f1")
dashboard.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Info o účtu a PC
account_label = tk.Label(dashboard, text="Crazikk Account", font=("Arial", 16), bg="#ecf0f1")
account_label.pack(pady=10)

pc_info = tk.Label(dashboard, text=f"CPU: {psutil.cpu_freq().current:.2f} MHz\nRAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB DDR4", bg="#ecf0f1")
pc_info.pack(pady=10)

# Pravá část - Live Vitals a Core Status
right_panel = tk.Frame(root, bg="#bdc3c7", width=200)
right_panel.pack(side="right", fill="y")

cpu_label = tk.Label(right_panel, text="CPU: 0%", bg="#bdc3c7", font=("Arial", 12))
cpu_label.pack(pady=10)

ram_label = tk.Label(right_panel, text="RAM: 0%", bg="#bdc3c7", font=("Arial", 12))
ram_label.pack(pady=10)

core_status = tk.Label(right_panel, text="Backups: 0\nActive Tweaks: 0\nSpace Cleaned: 0 GB", bg="#bdc3c7", font=("Arial", 12))
core_status.pack(pady=20)

# Funkce pro aktualizaci live dat
def update_vitals():
    cpu_label.config(text=f"CPU: {psutil.cpu_percent()}%")
    ram_label.config(text=f"RAM: {psutil.virtual_memory().percent}%")
    root.after(1000, update_vitals)  # aktualizace každou sekundu

update_vitals()
root.mainloop()
