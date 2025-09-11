import tkinter as tk
from tkinter import ttk
import win32api
import win32con

# Funkce pro detekci monitorů
def get_monitors_info():
    monitors = []
    i = 0
    while True:
        try:
            monitor = win32api.EnumDisplayDevices(None, i)
            if monitor.DeviceName:
                devmode = win32api.EnumDisplaySettings(monitor.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                info = {
                    "name": monitor.DeviceString,
                    "resolution": f"{devmode.PelsWidth}x{devmode.PelsHeight}",
                    "hz": devmode.DisplayFrequency
                }
                monitors.append(info)
            i += 1
        except win32api.error:
            break
    return monitors

# Vytvoření okna
root = tk.Tk()
root.title("Detekce monitoru")
root.geometry("450x250")
root.configure(bg="#1e1e1e")

# Nadpis
title = tk.Label(root, text="Připojené monitory", bg="#1e1e1e", fg="#ffffff", font=("Arial", 14, "bold"))
title.pack(pady=10)

# Informace o monitorech
monitors_info = get_monitors_info()
for i, m in enumerate(monitors_info):
    info_text = f"Monitor {i+1}: {m['name']}\nRozlišení: {m['resolution']} | {m['hz']} Hz"
    label = tk.Label(root, text=info_text, bg="#1e1e1e", fg="#ffffff", font=("Arial", 12), justify="left")
    label.pack(pady=5)

# Celkový počet monitorů
count_label = tk.Label(root, text=f"Celkem monitorů: {len(monitors_info)}", bg="#1e1e1e", fg="#4caf50", font=("Arial", 12, "bold"))
count_label.pack(pady=10)

root.mainloop()
