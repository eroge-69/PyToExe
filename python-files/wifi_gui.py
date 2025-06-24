
import subprocess
import tkinter as tk
from tkinter import ttk
import re

def get_wifi_info():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, encoding='utf-8')
        ssid_match = re.search(r"^\s*SSID\s*:\s*(.+)$", output, re.MULTILINE)
        signal_match = re.search(r"^\s*(訊號|Signal)\s*:\s*(\d+)%", output, re.MULTILINE)
        dbm_match = re.search(r"^\s*接收訊號強度\s*:\s*(-?\d+)\s*dBm", output, re.MULTILINE)

        ssid = ssid_match.group(1).strip() if ssid_match else "N/A"
        signal_percent = int(signal_match.group(2)) if signal_match else 0
        signal_dbm = dbm_match.group(1) + " dBm" if dbm_match else "N/A"

        return ssid, signal_percent, signal_dbm
    except Exception as e:
        return "Error", 0, "Error"

def update_info():
    ssid, signal_percent, signal_dbm = get_wifi_info()
    ssid_label.config(text=f"SSID: {ssid}")
    signal_label.config(text=f"Signal Strength: {signal_percent}%")
    dbm_label.config(text=f"Signal (dBm): {signal_dbm}")
    signal_bar['value'] = signal_percent
    root.after(1000, update_info)

# Create GUI
root = tk.Tk()
root.title("Wi-Fi Signal Monitor")
root.geometry("400x200")

ssid_label = tk.Label(root, text="SSID: ", font=("Arial", 14))
ssid_label.pack(pady=5)

signal_label = tk.Label(root, text="Signal Strength: ", font=("Arial", 14))
signal_label.pack(pady=5)

dbm_label = tk.Label(root, text="Signal (dBm): ", font=("Arial", 14))
dbm_label.pack(pady=5)

signal_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=100)
signal_bar.pack(pady=10)

update_info()
root.mainloop()
